"""Commands module for moderation."""

from discord.ext import commands

from maplebot import Bot, util


class Moderation(commands.Cog):
    @commands.hybrid_command(name="nospoil", brief="Delete the message you reply to and warn the user not to spoil.")
    @commands.has_permissions(manage_messages=True)
    async def nospoil(self, ctx: commands.Context):
        """Delete the message you reply to and warn the user not to spoil."""
        spoiler = ctx.message.reference
        spoiler_id = spoiler.message_id
        spoiler_message = await ctx.channel.fetch_message(spoiler_id)
        spoiler_author = spoiler_message.author
        await spoiler_message.delete()
        await ctx.send(f"Please, {spoiler_author.mention}, don't spoil the others!")


async def setup(bot: Bot):
    await bot.add_cog(Moderation())
    util.logger.info("Moderation cog loaded")
