from bot.util import MarketAlertException
import logging
from bot.commands.tracking import Tracking
import discord
from discord.ext import commands, tasks
import json

import configs
from bot import util

class Bot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        self.add_cog(Tracking(self))

        self.tracked_items = []


    async def on_ready(self):
        print(f"Connected as {self.user.name} #{self.user.id}")


    @tasks.loop(minutes=1)
    async def update_tracked_items(self):
        pass


if __name__ == "__main__":
    bot = Bot(configs.PREFIX)
    bot.run(configs.TOKEN)