from discord import errors, http
from bot.util import MarketAlertException
from aiohttp.client_exceptions import ClientResponseError

from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandError

from .. import http, util

class Tracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def track(self, ctx: Context, item_id: int):
        """
        Search for your item on https://universalis.app

        item id will be the numbers after the last slash on the url.

        Example: https://universalis.app/market/29497
        item id would be "29497"
        """
        try:
            item_name = await http.get_item_name(item_id)
            await ctx.send(f"Tracking **{item_name}**")
        except ClientResponseError as err:
            if err.status == 404:
                raise MarketAlertException(ctx.channel, "Requested item id was not found. Make sure you have a valid id")
            else:
                await ctx.send(err.message)

    async def cog_command_error(self, ctx: Context, error):
        if isinstance(error, MarketAlertException):
            try:
                ctx = error.channel
                
                await ctx.send(error.get_message())
            except:
                util.logging.warn(f"Unable to send Exception message, \n{error.message}")
        else:
            await ctx.send("Please check for correct usage")
            await ctx.send_help(ctx.command)