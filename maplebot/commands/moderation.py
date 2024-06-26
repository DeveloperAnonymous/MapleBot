"""Commands module for moderation."""

import asyncio
import platform

import discord
from discord.ext import commands

from maplebot import Bot
from maplebot import util


class Moderation(commands.Cog):
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def nospoil(self, ctx: commands.Context):
        """
        Deletes the message you replied to.

        Also mentions the user who sent the message.
        """

        spoiler = ctx.message.reference
        spoiler_id = spoiler.message_id
        spoiler_message = await ctx.channel.fetch_message(spoiler_id)
        spoiler_author = spoiler_message.author
        await spoiler_message.delete()
        await ctx.send(f"Please, {spoiler_author.mention}, don't spoil the others!")

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        """
        Updates the bot for me because I'm lazy.

        This command is only available for the bot owner.
        """

        try:
            sys = platform.platform()
            if "Linux" in sys:
                update_result = await asyncio.create_subprocess_shell(
                    "bash update_script.sh",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            elif "Windows" in sys:
                update_result = await asyncio.create_subprocess_shell(
                    '"D:\\Softwares\\Git\\bin\\bash" update_script.sh',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                raise asyncio.CancelledError()
        except asyncio.CancelledError as updateexc:
            update_result = updateexc.output
        stdout, stderr = await update_result.communicate()
        if stdout:
            update_result = stdout.decode("utf-8")
        elif stderr:
            update_result = stderr.decode("utf-8")
        else:
            update_result = "Something went wrong!"

        if len(update_result.strip()) == 0:
            update_result = "No output."

        update_embed = discord.Embed(title=":gear: Updating!")
        update_embed.description = "Pulling lastest version from **github**!"
        update_embed.add_field(
            name="Changes", value="```" + update_result + "```", inline=False
        )
        await ctx.reply(embed=update_embed)

        update_result = update_result.strip()
        if not (
            "up to date." in update_result or update_result == "Something went wrong!"
        ):
            exit(1)


async def setup(bot: Bot):
    await bot.add_cog(Moderation())
    util.logger.info("Moderation cog loaded")
