"""The main bot class for MapleBot."""

import asyncio
import os

import aiopg
import discord
from discord.ext import commands, tasks

import configs
from dbconfig import DatabaseConfig
from maplebot import util


class Bot(commands.Bot):
    """Main bot class for MapleBot."""

    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, intents=discord.Intents.all(), case_insensitive=True, **options)
        self.synced = False

        self.maple_items = []
        self.maple_alerts = []

        self.db_pool = None
        self.logging_channel: discord.TextChannel = None

        self.status_generator = iter(
            [
                discord.Activity(type=discord.ActivityType.watching, name="Maple Syrup"),
                discord.Activity(
                    type=discord.ActivityType.playing,
                    name="Maple Syrup Drinking Simulator",
                ),
                discord.Activity(type=discord.ActivityType.watching, name="the market"),
            ]
        )

    async def setup_hook(self) -> None:
        await self.setup_db()

        self.logging_channel = await self.fetch_channel(configs.LOG_CHANNEL)

        # Load cogs automatically from maplebot/commands, not in configs
        for cog in os.listdir("maplebot/commands"):
            if cog.endswith(".py") and not cog.startswith("__"):
                cog = cog[:-3]
                await self.load_extension(f"maplebot.commands.{cog}")

        # if not self.synced:
        #     synced_commands = await self.tree.sync(guild=self.get_guild(636009188786700289))
        #     util.logger.info(
        #         "Synced %s commands to the Discord API", len(synced_commands)
        #     )

    async def on_ready(self) -> None:
        """Event that triggers when the bot is ready."""
        print(f"Logged as {self.user.name} #{self.user.id}")

        if not self.change_status.is_running():
            self.change_status.start()

    @tasks.loop(seconds=60 * 5)
    async def change_status(self) -> None:
        """Change the bot's status every 5 minutes."""
        await self.change_presence(activity=next(self.status_generator))

    @change_status.error
    async def change_status_error(self, _) -> None:
        """Error handler for change_status task."""
        util.logger.error("Something went wrong while changing status, restarting loop in 5 seconds...")
        await asyncio.sleep(5)
        self.change_status.start()

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Event that triggers when the bot joins a guild."""
        if not guild.chunked:
            await guild.chunk()
        util.logger.info(f"Joined guild **{guild.name}** with {guild.member_count} members")
        await self.logging_channel.send(f"Joined guild **{guild.name}** with {guild.member_count} members")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Event that triggers when the bot leaves a guild."""
        util.logger.info(f"Left guild **{guild.name}** with {guild.member_count} members")
        await self.logging_channel.send(f"Left guild **{guild.name}** with {guild.member_count} members")

    async def setup_db(self) -> None:
        """Set up the database connection pool and create tables if they don't exist."""
        self.db_pool = await aiopg.create_pool(dsn=DatabaseConfig().dsn, minsize=1, maxsize=5)

        util.logger.info("Setting up database")
        for migration in os.listdir("migrations"):
            if migration.endswith(".sql"):
                util.logger.info(f"Running migration {migration}")
                async with self.db_pool.acquire() as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute(open(f"migrations/{migration}").read())
        util.logger.info("Database setup complete")
