"""Commands module for tracking items on the market."""

import discord
from aiohttp.client_exceptions import ClientResponseError
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandInvokeError

import configs
from maplebot import Bot, emojis, util
from maplebot.api.universalis import universalis_api
from maplebot.api.universalis.models.item import UniversalisItem
from maplebot.api.xiv import xiv_api
from maplebot.util import MarketAlertException


class MarketConverter(commands.Converter):
    async def convert(self, _: Context, argument: str) -> tuple[str | None, str]:
        args = argument.split(" ")
        world = args[0].lower()
        item_name = " ".join(args[1:]) if len(args) > 1 else None

        if not any(world == x.lower() for x in configs.DATACENTERS):
            item_name = " ".join(args)
            world = None

        return world, item_name


class Tracking(commands.Cog):
    """Commands for tracking items on the market."""
    def __init__(self, bot: Bot):
        self.bot = bot

    # @commands.command()
    async def track(self, ctx: Context, item_name: str):
        """
        Search for your item on https://universalis.app

        item id will be the numbers after the last slash on the url.

        Example: https://universalis.app/market/29497
        item id would be "29497"
        """
        try:
            xivapi_item = await xiv_api.get_item_by_name(item_name)
            await ctx.send(f"Tracking **{xivapi_item.name}**")
        except ClientResponseError as err:
            if err.status == 404:
                raise MarketAlertException(
                    ctx.channel,
                    "Requested item id was not found. Make sure you have a valid id",
                ) from err
            else:
                await ctx.send(err.message)

    @commands.command()
    async def market(self, ctx: Context, *, content: MarketConverter):
        """
        Gives you the current market price of an item.

        By default, this searches for the item in the Aether data center.
        If you have a preferred data center, you can set it with `ma!datacenter <datacenter>`.

        Syntax:
        !market <item_name>
        !market <datacenter> <item_name>

        Example:
        !market Tsai tou Vounou
        !market Crystal Tsai tou Vounou
        """

        world, item_name = content
        if world is not None and not any(
            world.lower() == x.lower() for x in configs.DATACENTERS
        ):
            raise MarketAlertException(
                ctx.channel,
                "Please specify a valid world from this selection:\n- "
                + "\n- ".join(sorted(configs.DATACENTERS.keys()))
            )
        
        if world is None:
            # Fetch the user's default datacenter, or keep world as none
            async with self.bot.db_pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        """
                        SELECT datacenter
                        FROM user_settings
                        WHERE discord_id = %s
                        """,
                        (ctx.author.id,),
                    )

                    datacenter = await cursor.fetchone()
                    if datacenter is not None:
                        world = datacenter[0]

        message = await ctx.send(f"{emojis.LOADING} Searching for item...")
        try:
            xivapi_item = await xiv_api.get_item_by_name(item_name)

            if xivapi_item is None:
                return await message.edit(
                    content=f'{emojis.BANGBANG} Requested item "{item_name}" was not found. Make sure you have a valid item name'
                )

        except ClientResponseError as err:
            if err.status == 404:
                raise MarketAlertException(
                    ctx.channel,
                    "Requested item id was not found. Make sure you have a valid id",
                ) from err
            else:
                await message.edit(content=err.message)
        except Exception as err:
            await message.edit(content="An error occurred while fetching the item")
            return util.logging.error(f"Error fetching item: {err}")

        await message.edit(
            content=f"{emojis.LOADING} Searching for **{xivapi_item.name}**"
        )

        try:
            universalis_nq_item: UniversalisItem = await universalis_api.get_item(
                xivapi_item.id, False, world
            )

            universalis_hq_item: UniversalisItem = await universalis_api.get_item(
                xivapi_item.id, True, world
            )
        except ClientResponseError as err:
            await message.edit(content=f"A problem with Universalis happened! **{err.message}**")

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
                        f"{listing.world_name}: {listing.quantity:,}x {listing.price_per_unit:,}g ({listing.total:,}g)"
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
                        f"{listing.world_name}: {listing.quantity:,}x {listing.price_per_unit:,}g ({listing.total:,}g)"
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

        embed.set_footer(
            text=f"Last review time: {universalis_nq_item.last_updated.strftime("%d/%m/%Y %H:%M:%S")}"
        )

        await message.edit(
            content=f"Results for **{xivapi_item.name}**", embed=embed
        )

    async def cog_command_error(self, ctx: Context, error):
        error = error.original if isinstance(error, CommandInvokeError) else error
        if isinstance(error, MarketAlertException):
            try:
                channel = error.channel

                await channel.send(error.get_message())
            except discord.Forbidden:
                util.logging.warning(
                    f"Unable to send Exception message, \n{error.message}"
                )

        await ctx.message.add_reaction(emojis.QUESTION)
        raise error


async def setup(bot: Bot):
    await bot.add_cog(Tracking(bot))
    util.logger.info("Tracking cog loaded")
