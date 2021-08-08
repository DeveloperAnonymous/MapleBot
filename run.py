from discord.ext import commands, tasks

import configs
from bot.commands.tracking import Tracking


class Bot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        self.add_cog(Tracking(self))

        self.maple_items = []
        self.maple_alerts = []

        # asyncio.new_event_loop().run_until_complete(self.on_new_alert())

    async def on_ready(self):
        print(f"Connected as {self.user.name} #{self.user.id}")

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
