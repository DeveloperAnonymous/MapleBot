"""Commands module for moderation."""

from discord.ext import commands
from discord.ext.commands import Context

from maplebot import MapleBot, util


class OwnerCog(commands.Cog):
    def __init__(self, bot: MapleBot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sync(self, ctx: Context):
        synced = await self.bot.tree.sync()

        await ctx.send(f"✅ Synced {len(synced)} commands.", ephemeral=True)


async def setup(bot: MapleBot):
    await bot.add_cog(OwnerCog(bot))
    util.logger.info("Owner cog loaded")
