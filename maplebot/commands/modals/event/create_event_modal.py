import discord
from discord import ui


class CreateEventModal(ui.Modal, title="Create a new event (1/2)"):
    """Modal to create a new event"""

    event_title = ui.TextInput(
        label="Title",
        placeholder="Event title",
        style=discord.TextStyle.short,
        max_length=32,
    )
    event_description = ui.TextInput(
        label="Description",
        placeholder="Event description",
        style=discord.TextStyle.paragraph,
        max_length=512,
    )
    event_date = ui.TextInput(
        label="Date",
        placeholder="DD/MM/YYYY",
        style=discord.TextStyle.short,
        max_length=10,
    )
    # time = ui.Select(
    #     placeholder="Time",
    #     options=[
    #         discord.SelectOption(
    #             label=f"{hour:02d}:00",
    #             value=f"{hour:02d}:00",
    #             default=hour == 0,
    #         )
    #         for hour in range(0, 24)
    #     ],
    # )
    # min_level = ui.TextInput(
    #     label="Minimum level",
    #     placeholder="Minimum level required",
    #     style=discord.TextStyle.short,
    #     required=False,
    #     row=3,
    # )
    # min_ilvl = ui.TextInput(
    #     label="Minimum ilvl",
    #     placeholder="Minimum ilvl required",
    #     style=discord.TextStyle.short,
    #     required=False,
    #     row=3,
    # )
    # max_participants = ui.Select(
    #     placeholder="Maximum participants",
    #     options=[
    #         discord.SelectOption(label=str(i), value=str(i), default=i == 2)
    #         for i in range(2, 9)
    #     ],
    #     row=4,
    # )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle the submission of the modal"""
        await interaction.response.send_modal(__CreateEventDetailsModal(self))
        # await interaction.response.send_message(
        #     f"""Creating event with the following parameters:
        #                               **Title:** {self.event_title}
        #                               **Description:** {self.event_description}
        #                               **Date:** {self.event_date}
        #                             """
        # )


class __CreateEventDetailsModal(ui.Modal, title="Create a new event (2/2)"):
    something = ui.TextInput(
        label="Something",
        placeholder="Something",
        style=discord.TextStyle.short,
        max_length=32,
    )

    def __init__(self, parent: CreateEventModal):
        super().__init__()
        self.parent = parent

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"""Creating event with the following parameters:
                                  **Title:** {self.parent.event_title}
                                  **Description:** {self.parent.event_description}
                                  **Date:** {self.parent.event_date}
                                  **Something:** {self.something}
                                """
        )
