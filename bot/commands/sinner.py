from difflib import SequenceMatcher

import discord
from discord.ext import commands

PRAYER = "Excuse me father, for I have sinned."

class Sinner(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if SequenceMatcher(None, message.content, PRAYER).ratio() > 0.8:
            await message.channel.send("Aye, mine own issue, i f'rgive thee :pray:")
