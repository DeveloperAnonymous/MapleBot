from types import NoneType

import discord
from aiohttp.client_exceptions import ClientResponseError
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandInvokeError

import configs
from bot import emojis as e
from bot import util
from bot.api.universalis import universalis_api
from bot.api.universalis.models.item import UniversalisItem
from bot.api.xiv import xiv_api
from bot.util import MarketAlertException


class MarketConverter(commands.Converter):
    async def convert(self, ctx: Context, argument: str) -> tuple[str | NoneType, str]:
        args = argument.split(" ")
        world = args[0]
        item_name = " ".join(args[1:]) if len(args) > 1 else None

        if not any(world.lower() == x.lower() for x in configs.SERVERS.keys()):
            item_name = " ".join(args)
            world = None

        return world, item_name


class Tracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
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
                raise MarketAlertException(ctx.channel,
                                           "Requested item id was not found. Make sure you have a valid id")
            else:
                await ctx.send(err.message)

    @commands.command()
    async def market(self, ctx: Context, *, content: MarketConverter):
        """
        Gives you the current market price of an item.
        """

        world, item_name = content
        if world is not None and not any(world.lower() == x.lower() for x in configs.SERVERS.keys()):
            raise MarketAlertException(ctx.channel, "Please specify a valid world from this selection:\n" + ", ".join(
                configs.SERVERS.keys()))

        message = await ctx.send(f"{e.LOADING} Searching for item...")
        try:
            xivapi_item = await xiv_api.get_item_by_name(item_name)

            if xivapi_item is None:
                return await message.edit(
                    content=f"{e.BANGBANG} Requested item \"{item_name}\" was not found. Make sure you have a valid item name")

            await message.edit(content=f"{e.LOADING} Searching for **{xivapi_item.name}**")

            universalis_item: UniversalisItem = await universalis_api.get_item(xivapi_item.id, world)

            sorted_listings = sorted(universalis_item.listings,
                                     key=lambda listing: (listing.price_per_unit, -listing.quantity))

            embed = discord.Embed(title=f"{xivapi_item.name}", url=f"https://universalis.app/market/{xivapi_item.id}",
                                  color=0x00ff00)
            embed.set_thumbnail(url=xivapi_item.icon_url)

            embed.add_field(name="Top 10 Listings:", value="```\n" + "\n".join(
                [f"{listing.world_name}: {listing.quantity}x {listing.price_per_unit}g ({listing.total}g)" for listing
                 in sorted_listings[:10]]
                + ["```"]
            ), inline=False)
            embed.add_field(name="Minimum NQ price:", value=f"{universalis_item.min_price_nq}g")
            embed.add_field(name="Minimum HQ price:", value=f"{universalis_item.min_price_hq}g")
            embed.set_footer(text=f"Last updated: {universalis_item.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

            await message.edit(content=f"Results for **{xivapi_item.name}**", embed=embed)
        except ClientResponseError as err:
            if err.status == 404:
                raise MarketAlertException(ctx.channel,
                                           "Requested item id was not found. Make sure you have a valid id")
            else:
                await message.edit(content=err.message)

    async def cog_command_error(self, ctx: Context, error):
        error = error.original if isinstance(error, CommandInvokeError) else error
        if isinstance(error, MarketAlertException):
            try:
                channel = error.channel

                await channel.send(error.get_message())
            except discord.Forbidden:
                util.logging.warning(f"Unable to send Exception message, \n{error.message}")

        await ctx.message.add_reaction(e.QUESTION)
        raise error
