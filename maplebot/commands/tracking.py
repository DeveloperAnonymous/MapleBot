"""Commands module for tracking items on the market."""

import discord
from aiohttp.client_exceptions import ClientResponseError
from discord import Interaction, app_commands
from discord.app_commands import Choice
from discord.app_commands.errors import AppCommandError
from discord.app_commands.errors import CommandInvokeError as AppCommandInvokeError
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandError, CommandInvokeError

import configs
from maplebot import MapleBot, World, emojis, util
from maplebot.api.universalis import universalis_api
from maplebot.api.universalis.models import UniversalisItem, UniversalisItemListing
from maplebot.api.xiv import xiv_api
from maplebot.util import MarketAlertException


class MarketConverter(commands.Converter, app_commands.Transformer[tuple[str | None, str]]):
    async def convert(self, _: commands.Context, argument: str) -> tuple[str | None, str]:
        args = argument.split()
        datacenter = args[0].lower()
        item_name = " ".join(args[1:]) if len(args) > 1 else None

        if not any(datacenter == x.lower() for x in util.get_datacenters()) and datacenter != "region":
            item_name = " ".join(args)
            datacenter = None

        return datacenter, item_name

    async def transform(self, interaction: discord.Interaction, value: str) -> tuple[str | None, str]:
        ctx = await commands.Context.from_interaction(interaction)
        return await self.convert(ctx, value)


class Tracking(commands.Cog):
    """Commands for tracking items on the market."""

    def __init__(self, bot: MapleBot):
        self.bot = bot

    def format_listing_entry(self, listing: UniversalisItemListing, datacenter: str) -> str:
        """Format a single listing entry."""
        if datacenter in configs.REGIONS.keys():
            return f"{util.get_datacenter_for_world(listing.world_name)} - {listing.world_name}: {listing.quantity:,}x {listing.price_per_unit:,}g ({listing.total:,}g)"

        return f"{listing.world_name}: {listing.quantity:,}x {listing.price_per_unit:,}g ({listing.total:,}g)"

    @commands.hybrid_command(brief="List all available datacenters.")
    async def datacenters(self, ctx: Context):
        """List all available datacenters."""
        await ctx.send("Available datacenters:\n- " + "\n- ".join(util.get_datacenters()))

    @commands.command(name="market", brief="Get the current market price of an item.")
    async def market(self, ctx: commands.Context, *, content: MarketConverter):
        f"""
        **THIS COMMAND IS DEPRECATED, USE `/market` INSTEAD!**
        Gives you the current market price of the item in your datacenter.

        You can also specify a datacenter to check the price in another datacenter.
        If you don't specify a datacenter, it will use your preferred world.

        When using `region` as datacenter, it will use the region of your preferred world to check the price.

        Syntax:
        {configs.PREFIX}market <item_name>
        {configs.PREFIX}market (datacenter) <item_name>

        Example:
        {configs.PREFIX}market Tsai tou Vounou
        {configs.PREFIX}market Aether Tsai tou Vounou

        {configs.PREFIX}market region Tsai tou Vounou
        """
        datacenter, item_name = content

        await self._send_market(ctx, item_name, datacenter)

    @app_commands.command(name="market", description="Get the current market price of an item.")
    @app_commands.describe(
        item_name="The name of the item to search for",
        datacenter="The datacenter to search in, defaults to your preferred world",
    )
    @app_commands.choices(
        datacenter=[Choice(name=datacenter, value=datacenter) for datacenter in (*util.get_datacenters() + ["Region"],)]
    )
    async def market_interaction(self, interaction: discord.Interaction, item_name: str, datacenter: str = None):
        """Get the current market price of an item."""
        await interaction.response.defer(thinking=True)

        if datacenter and datacenter not in util.get_datacenters() and datacenter != "Region":
            raise MarketAlertException(
                interaction.channel,
                f"Invalid datacenter. Available datacenters are:\n- " + "\n- ".join(util.get_datacenters()),
            )

        await self._send_market(interaction, item_name, datacenter)

    async def _send_market(self, ctx: Context | Interaction, item_name: str, datacenter: str | None = None):
        """Send a market message."""
        if isinstance(ctx, Interaction):
            ctx = await commands.Context.from_interaction(ctx)

        world_data: World = None
        if datacenter is None or datacenter == "Region":
            async with self.bot.db_pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        """
                        SELECT region, datacenter, world
                        FROM user_settings
                        WHERE id = %s
                        """,
                        (ctx.author.id,),
                    )

                    result = await cursor.fetchone()
                    if result is not None:
                        world_data = World(*result)

            if world_data is None:
                raise MarketAlertException(
                    ctx.channel,
                    f"You didn't set your preferred world. Please set it with `/setworld`",
                )

        if datacenter == "Region":
            datacenter = world_data.region
        elif datacenter is None:
            datacenter = world_data.datacenter

        message = await ctx.send(f"{emojis.LOADING} Searching for item...")
        try:
            xivapi_item = await xiv_api.get_item_by_name(item_name)

            if xivapi_item is None:
                return await message.edit(
                    content=f'{emojis.BANGBANG} Requested item "{item_name}" was not found. Make sure you have a valid item name'
                )

        except ClientResponseError as err:
            await message.edit(content=err.message)
            return util.logging.error(f"Error fetching item: {err}")
        except Exception as err:
            await message.edit(content="An error occurred while fetching the item")
            return util.logging.error(f"Error fetching item: {err}")

        await message.edit(content=f"{emojis.LOADING} Searching for **{xivapi_item.name}**")

        try:
            universalis_nq_item: UniversalisItem = await universalis_api.get_item(xivapi_item.id, 10, False, datacenter)

            universalis_hq_item: UniversalisItem = await universalis_api.get_item(xivapi_item.id, 10, True, datacenter)
        except ClientResponseError as err:
            util.logger.error(f"Error fetching item: {err}")
            return await message.edit(content=f"A problem with Universalis happened! **{err.message}**")

        sorted_nq_listings = sorted(
            universalis_nq_item.listings,
            key=lambda listing: (listing.price_per_unit, -listing.quantity),
        )

        sorted_hq_listings = sorted(
            universalis_hq_item.listings,
            key=lambda listing: (listing.price_per_unit, -listing.quantity),
        )

        embed = discord.Embed(
            title=f"{xivapi_item.name}",
            url=f"https://universalis.app/market/{xivapi_item.id}",
            color=0x00FF00,
            type="rich",
        )
        embed.set_thumbnail(url=xivapi_item.icon_url)

        if len(sorted_nq_listings) > 0:
            embed.add_field(
                name="Top 10 NQ Listings:",
                value="```\n"
                + "\n".join(
                    [
                        self.format_listing_entry(listing, datacenter)
                        for listing in sorted_nq_listings[:10]
                        if not listing.hq
                    ]
                    + ["```"]
                ),
                inline=False,
            )

        if len(sorted_hq_listings) > 0:
            embed.add_field(
                name="Top 10 HQ Listings:",
                value="```\n"
                + "\n".join(
                    [
                        self.format_listing_entry(listing, datacenter)
                        for listing in sorted_hq_listings[:10]
                        if listing.hq
                    ]
                    + ["```"]
                ),
                inline=False,
            )

        embed.add_field(
            name="Minimum NQ price:",
            value=f"{universalis_nq_item.min_price_nq:,}g",
            inline=True,
        )
        embed.add_field(
            name="Minimum HQ price:",
            value=f"{universalis_hq_item.min_price_hq:,}g",
            inline=True,
        )

        embed.set_footer(text=f"Last review time: {universalis_nq_item.last_updated.strftime("%d/%m/%Y %H:%M:%S")}")

        await message.edit(content=f"Results for **{xivapi_item.name}**", embed=embed)

    async def cog_command_error(self, ctx: Context, error: CommandError):
        error = error.original if isinstance(error, CommandInvokeError) else error
        if isinstance(error, MarketAlertException):
            try:
                channel = error.channel

                return await channel.send(error.get_message())
            except discord.Forbidden:
                util.logging.warning(f"Unable to send Exception message, \n{error.message}")

        await ctx.message.add_reaction(emojis.QUESTION)

    async def cog_app_command_error(self, interaction: Interaction, error: AppCommandError):
        error = error.original if isinstance(error, AppCommandInvokeError) else error
        if isinstance(error, MarketAlertException):
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(error.get_message(), ephemeral=True)
                else:
                    await interaction.response.send_message(error.get_message(), ephemeral=True)
            except discord.Forbidden:
                util.logging.warning(f"Unable to send Exception message, \n{error.message}")
            finally:
                return

        if interaction.message:
            await interaction.message.add_reaction(emojis.QUESTION)


async def setup(bot: MapleBot):
    await bot.add_cog(Tracking(bot))
    util.logger.info("Tracking cog loaded")
