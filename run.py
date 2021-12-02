import asyncio

import discord
from discord.ext import commands, tasks

import configs
from bot import util
from bot.commands import Tracking, Moderation


class Bot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        self.add_cog(Tracking())
        self.add_cog(Moderation())

        self.maple_items = []
        self.maple_alerts = []

        self.status_generator = iter([
            discord.Activity(type=discord.ActivityType.watching, name="Maple Syrup"),
            discord.Activity(type=discord.ActivityType.playing, name="Maple Syrup Drinking Simulator"),
            discord.Activity(type=discord.ActivityType.watching, name="the market")
        ])

    async def on_ready(self):
        print(f"Logged as {self.user.name} #{self.user.id}")

        if not self.change_status.is_running():
            self.change_status.start()

    @tasks.loop(seconds=60)
    async def change_status(self):
        await self.change_presence(activity=next(self.status_generator))

    @change_status.error
    async def change_status_error(self, _):
        util.logger.error("Something went wrong while changing status, restarting loop in 5 seconds...")
        await asyncio.sleep(5)
        self.change_status.start()


if __name__ == "__main__":
    bot = Bot(configs.PREFIX)
    bot.run(configs.TOKEN)
