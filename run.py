import asyncio
import discord
from discord.ext import commands, tasks

import configs
from bot import util
from bot.commands import Tracking, Moderation


class Bot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        self.add_cog(Tracking(self))
        self.add_cog(Moderation(self))

        self.maple_items = []
        self.maple_alerts = []

        self.status_generator = iter([
            discord.Activity(type=discord.ActivityType.watching, name="Maple Syrup"),
            discord.Activity(type=discord.ActivityType.playing, name="Maple Syrup Drinking Simulator"),
            discord.Activity(type=discord.ActivityType.watching, name="the market")
        ])

        # asyncio.new_event_loop().run_until_complete(self.on_new_alert())

    async def on_ready(self):
        print(f"Logged as {self.user.name} #{self.user.id}")

        if not self.change_status.is_running():
            self.change_status.start()

    # Change status every minute
    @tasks.loop(seconds=60)
    async def change_status(self):
        await self.change_presence(activity=next(self.status_generator))

    @change_status.error
    async def change_status_error(self, error):
        util.logger.error("Something went wrong while changing status, restarting loop in 5 seconds...")
        asyncio.sleep(5)
        self.change_status.start()

    @tasks.loop(minutes=1)
    async def update_tracked_items(self):
        pass

    # async def on_new_alert(self):
    #     async with websockets.connect(f"ws://{configs.WS_HOST}:{configs.WS_PORT}/") as ws:
    #         msg = await ws.recv()
    #         util.logger.info(msg)


if __name__ == "__main__":
    bot = Bot(configs.PREFIX)
    bot.run(configs.TOKEN)
