import datetime

import discord
from dateutil import tz
from discord import app_commands
from discord.ext import commands

from maplebot import Bot
from maplebot import emojis as emojis
from maplebot import util
from maplebot.commands.modals.event import CreateEventModal
from maplebot.event import Event
from maplebot.requirement import (
    ILVLRequirement,
    LevelRequirement,
    ParticipantsRequirement,
    Requirement,
)


@app_commands.guild_only()
class Events(
    commands.GroupCog, group_name="event", description="Commands to manage events"
):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new event")
    async def create(
        self,
        interaction: discord.Interaction
    ):
        """
        Create a new event
        """
        modal = CreateEventModal()
        await interaction.response.send_modal(modal)
        # await interaction.response.send_message(
        #     f"""Creating event with the following parameters:
        #                                   **Title:** {title}
        #                                   **Description:** {description}
        #                                   **Date:** {date}
        #                                   **Minimum ilvl:** {min_ilvl}
        #                                   **Minimum level:** {min_level}
        #                                   **Maximum participants:** {max_participants}
        #                                 """
        # )

    async def old_create(self, interaction: discord.Interaction):
        """Create a new event"""

        bot = self.bot

        # Create the event embed
        event_embed = discord.Embed(
            title="Create a new event",
            description="Please follow the steps to create a new event!\nYou can also use **\\n** to skip lines.",
            color=0x00FF00,
        )
        event_embed.add_field(
            name="Step 1",
            value="Please type the name of the event you want to create.",
            inline=False,
        )
        event_embed.set_footer(
            text="*NOTE: You can correct any mistakes you make at the end of the event creation process."
        )
        await interaction.response.send_message(embed=event_embed)

        # Get the name of the event
        message: discord.Message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.author.id
            and m.channel.id == interaction.channel.id,
            timeout=60,
        )
        event_name: str = message.content
        await message.delete()

        # Prepare for the next step
        event_embed.clear_fields()
        event_embed.add_field(name="Event name", value=event_name, inline=False)
        event_embed.add_field(
            name="Step 2",
            value="Please type the description of the event.",
            inline=False,
        )
        await interaction.response.edit_message(embed=event_embed)

        # Get the description of the event
        message: discord.Message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id
            and m.channel.id == interaction.channel.id,
            timeout=60,
        )
        event_description: str = message.content.replace("\\n", "\n")
        await message.delete()

        event_embed.remove_field(1)
        event_embed.add_field(
            name="Event description", value=event_description, inline=False
        )
        event_embed.add_field(
            name="Step 3",
            value="Please type the date of when the event will occur. (DD/MM/YYYY HH:mm TZ)",
            inline=False,
        )
        await interaction.response.edit_message(embed=event_embed)

        # Get the date of the event
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id
            and m.channel.id == interaction.channel.id,
            timeout=60,
        )
        raw_event_date: str = message.content
        await message.delete()

        date_time = raw_event_date.split(" ")
        date = date_time[0].split("/")
        time = date_time[1].split(":")
        timezone = date_time[2]

        timezone = tz.gettz(timezone)
        event_date = datetime.datetime(
            int(date[2]),
            int(date[1]),
            int(date[0]),
            int(time[0]),
            int(time[1]),
            tzinfo=timezone,
        )

        event_embed.remove_field(2)
        event_embed.add_field(
            name="Event date",
            value=event_date.strftime("%B %d, %Y at %I:%M %p %Z"),
            inline=False,
        )
        event_embed.add_field(
            name="Step 4",
            value="Please type the minimum ilvl required to participate to the event. (Use 'None' if not applicable)",
            inline=False,
        )
        await interaction.response.edit_message(embed=event_embed)

        # Get the minimum ilvl required
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id
            and m.channel.id == interaction.channel.id,
            timeout=60,
        )
        raw_min_ilvl = message.content
        await message.delete()

        min_ilvl = int("".join(filter(str.isdigit, raw_min_ilvl)))
        if raw_min_ilvl.lower() == "none":
            min_ilvl = None

        event_embed.remove_field(3)
        event_embed.add_field(
            name="Minimum ilvl",
            value=min_ilvl if min_ilvl is not None else "N/A",
            inline=False,
        )
        event_embed.add_field(
            name="Step 5",
            value="Please type the minimum level required to participate to the event. (Use 'None' if not applicable)",
            inline=False,
        )
        await interaction.response.edit_message(embed=event_embed)

        # Get the minimum level required
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id
            and m.channel.id == interaction.channel.id,
            timeout=60,
        )
        raw_min_level = message.content
        await message.delete()

        min_level = int("".join(filter(str.isdigit, raw_min_level)))
        if raw_min_level.lower() == "none":
            min_level = None

        event_embed.remove_field(4)
        event_embed.add_field(
            name="Minimum level",
            value=min_level if min_level is not None else "N/A",
            inline=False,
        )
        event_embed.add_field(
            name="Step 6",
            value="Please type the maximum number of participants allowed to participate to the event. (Use 'None' if not applicable)",
            inline=False,
        )
        await interaction.response.edit_message(embed=event_embed)

        # Get the maximum number of participants
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.author.id
            and m.channel.id == interaction.channel.id,
            timeout=60,
        )
        raw_max_participants = message.content
        await message.delete()

        max_participants = int("".join(filter(str.isdigit, raw_max_participants)))
        if raw_max_participants.lower() == "none":
            max_participants = None

        event_embed.remove_field(5)
        event_embed.add_field(
            name="Maximum participants",
            value=max_participants if max_participants is not None else "N/A",
            inline=False,
        )

        # Create the event
        # Create a list of requirements list[Requirement]
        requirements: list[Requirement] = []
        if min_ilvl is not None:
            requirements.append(ILVLRequirement(min_ilvl))
        if min_level is not None:
            requirements.append(LevelRequirement(min_level))
        if max_participants is not None:
            requirements.append(ParticipantsRequirement(max_participants))

        event = Event(
            event_name, event_description, event_date, requirements, interaction.author
        )

        interaction.delete_original_response()
        message = await interaction.send(f"{emojis.LOADING} Creating event...")
        # await event_api.create_event(event)
        await message.edit(content=f"{emojis.CHECK} Event created!", embed=event.get_embed())


async def setup(bot: Bot):
    await bot.add_cog(Events(bot))
    util.logger.info("Events cog loaded")
