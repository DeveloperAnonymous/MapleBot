import discord
from discord import ui

from configs import REGIONS


class WorldSelection:
    def __init__(self, region: str, datacenter: str, world: str):
        self.region = region
        self.datacenter = datacenter
        self.world = world


class WorldSelectionInteraction(ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=60)

        self.author = author
        self.selection: WorldSelection | None = None

        options = [
            discord.SelectOption(label=datacenter, value=f"{region}.{datacenter}")
            for region, centers in REGIONS.items()
            for datacenter in centers
        ]
        self.datacenter_select = ui.Select(
            placeholder="Select datacenter…", options=options, min_values=1, max_values=1
        )
        self.datacenter_select.callback = self.select_datacenter
        self.add_item(self.datacenter_select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author.id

    async def select_datacenter(self, interaction: discord.Interaction):
        await interaction.response.defer()

        region, datacenter = self.datacenter_select.values[0].split(".", 1)
        self.datacenter_select.disabled = True

        world_options = [
            discord.SelectOption(label=world, value=f"{region}.{datacenter}.{world}")
            for world in REGIONS[region][datacenter]
        ]
        self.server_select = ui.Select(placeholder="Select world…", options=world_options, min_values=1, max_values=1)
        self.server_select.callback = self.select_world
        self.add_item(self.server_select)

        await interaction.message.edit(view=self)

    async def select_world(self, interaction: discord.Interaction):
        region, datacenter, world = self.server_select.values[0].split(".", 2)
        self.selection = WorldSelection(region, datacenter, world)

        await interaction.message.edit(view=None)
        self.stop()

    @ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, _: ui.Button):
        await interaction.response.edit_message(view=None)
        self.stop()
