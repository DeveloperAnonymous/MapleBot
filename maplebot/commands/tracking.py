"""Commands module for tracking items on the market."""

import discord
from aiohttp.client_exceptions import ClientResponseError
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandInvokeError

import configs
from maplebot import Bot, World, emojis, util
from maplebot.api.universalis import universalis_api
from maplebot.api.universalis.models import UniversalisItem, UniversalisItemListing
from maplebot.api.xiv import xiv_api
from maplebot.util import MarketAlertException


class MarketConverter(commands.Converter):
    async def convert(self, _: Context, argument: str) -> tuple[str | None, str]:
        args = argument.split(" ")
        datacenter = args[0].lower()
        item_name = " ".join(args[1:]) if len(args) > 1 else None

        if not any(datacenter == x.lower() for x in util.get_datacenters()) and datacenter != "region":
            item_name = " ".join(args)
            datacenter = None

        return datacenter, item_name


class Tracking(commands.Cog):
    """Commands for tracking items on the market."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def format_listing_entry(self, listing: UniversalisItemListing, datacenter: str) -> str:
        """Format a single listing entry."""
        if datacenter in configs.REGIONS.keys():
            return f"{util.get_datacenter_for_world(listing.world_name)} - {listing.world_name}: {listing.quantity:,}x {listing.price_per_unit:,}g ({listing.total:,}g)"

        return f"{listing.world_name}: {listing.quantity:,}x {listing.price_per_unit:,}g ({listing.total:,}g)"

    @commands.command()
    async def datacenters(self, ctx: Context):
        """List all available datacenters."""
        await ctx.send(
            "Available datacenters:\n- "
            + "\n- ".join(
                sorted([datacenter for datacenters in configs.REGIONS.values() for datacenter in datacenters.keys()])
            )
        )

    @commands.command()
    async def market(self, ctx: Context, *, content: MarketConverter):
        f"""
        Gives you the current market price of the item in your datacenter.

        You can also specify a datacenter to check the price in another datacenter.
        If you don't specify a datacenter, it will use your preferred world.

        When using `region` as datacenter, it will use the region of your preferred world to check the price.

        Syntax:
        {configs.PREFIX}market <item_name>
        {configs.PREFIX}market <datacenter> <item_name>

        Example:
        {configs.PREFIX}market Tsai tou Vounou
        {configs.PREFIX}market Aether Tsai tou Vounou

        {configs.PREFIX}market region Tsai tou Vounou
        """
        world_data: World = None

        datacenter, item_name = content
        if datacenter is None or datacenter == "region":
            # Fetch the user's default datacenter, or keep world as none
            async with self.bot.db_pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        """
                        SELECT region, datacenter, world
                        FROM user_settings
                        WHERE discord_id = %s
                        """,
                        (ctx.author.id,),
                    )

                    result = await cursor.fetchone()
                    if result is not None:
                        world_data = World(*result)

        if datacenter is None and (world_data is None or world_data.world is None):
            raise MarketAlertException(
                ctx.channel,
                f"You didn't set your preferred world. Please set it with `{configs.PREFIX}setworld`",
            )

        if datacenter == "region":
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

    async def cog_command_error(self, ctx: Context, error):
        error = error.original if isinstance(error, CommandInvokeError) else error
        if isinstance(error, MarketAlertException):
            try:
                channel = error.channel

                return await channel.send(error.get_message())
            except discord.Forbidden:
                util.logging.warning(f"Unable to send Exception message, \n{error.message}")

        await ctx.message.add_reaction(emojis.QUESTION)


async def setup(bot: Bot):
    await bot.add_cog(Tracking(bot))
    util.logger.info("Tracking cog loaded")
