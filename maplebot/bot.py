import asyncio

import aiopg
import discord
from discord.ext import commands, tasks

from dbconfig import DatabaseConfig
from maplebot import util


class Bot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, intents=discord.Intents.all(), **options)
        self.synced = False

        self.maple_items = []
        self.maple_alerts = []

        self.status_generator = iter(
            [
                discord.Activity(
                    type=discord.ActivityType.watching, name="Maple Syrup"
                ),
                discord.Activity(
                    type=discord.ActivityType.playing,
                    name="Maple Syrup Drinking Simulator",
                ),
                discord.Activity(type=discord.ActivityType.watching, name="the market"),
            ]
        )

    async def setup_hook(self) -> None:
        # self.db_pool = await aiopg.create_pool(dsn=DatabaseConfig().dsn, minsize=1, maxsize=5)

        await self.load_extension("maplebot.commands.events")
        await self.load_extension("maplebot.commands.tracking")
        await self.load_extension("maplebot.commands.moderation")
        await self.load_extension("maplebot.commands.sinner")

        # if not self.synced:
        #     synced_commands = await self.tree.sync(guild=self.get_guild(636009188786700289))
        #     util.logger.info(
        #         f"Synced {len(synced_commands)} commands to the Discord API"
        #     )

    async def on_ready(self):
        print(f"Logged as {self.user.name} #{self.user.id}")

        if not self.change_status.is_running():
            self.change_status.start()

    @tasks.loop(seconds=60*5)
    async def change_status(self):
        await self.change_presence(activity=next(self.status_generator))

    @change_status.error
    async def change_status_error(self, _):
        util.logger.error(
            "Something went wrong while changing status, restarting loop in 5 seconds..."
        )
        await asyncio.sleep(5)
        self.change_status.start()
