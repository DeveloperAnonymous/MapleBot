"""Commands module for moderation."""

from discord.ext import commands
from discord.ext.commands import Context

from maplebot import Bot, util


class OwnerCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sync(self, ctx: Context):
        synced = await self.bot.tree.sync()

        await ctx.send(f"✅ Synced {len(synced)} commands.", ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(OwnerCog(bot))
    util.logger.info("Owner cog loaded")
