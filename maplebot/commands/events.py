import datetime
from typing import List

import discord
from maplebot import emojis as e
from maplebot.event import Event
from maplebot.interactions import EventInteraction
from maplebot.requirement import (
    ILVLRequirement,
    LevelRequirement,
    ParticipantsRequirement,
    Requirement,
)
from dateutil import tz
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def get_event_name(self, ctx: commands.Context, bot: commands.Bot) -> str:
        message: discord.Message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id,
            timeout=60,
        )
        event_name: str = message.content
        await message.delete()

        return event_name.content

    @commands.command("createevent")
    async def create_event(self, ctx: commands.Context):
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
        original_message = await ctx.send(embed=event_embed)

        # Get the name of the event
        message: discord.Message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id,
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
        await original_message.edit(embed=event_embed)

        # Get the description of the event
        message: discord.Message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id,
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
        await original_message.edit(embed=event_embed)

        # Get the date of the event
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id,
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
        await original_message.edit(embed=event_embed)

        # Get the minimum ilvl required
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id,
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
        await original_message.edit(embed=event_embed)

        # Get the minimum level required
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id,
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
        await original_message.edit(embed=event_embed)

        # Get the maximum number of participants
        message = await bot.wait_for(
            "message",
            check=lambda m: m.author.id == ctx.author.id
            and m.channel.id == ctx.channel.id,
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
        # Create a list of requirements List[Requirement]
        requirements: List[Requirement] = []
        if min_ilvl is not None:
            requirements.append(ILVLRequirement(min_ilvl))
        if min_level is not None:
            requirements.append(LevelRequirement(min_level))
        if max_participants is not None:
            requirements.append(ParticipantsRequirement(max_participants))

        event = Event(
            event_name, event_description, event_date, requirements, ctx.author
        )

        original_message.delete()
        message = await ctx.send(f"{e.LOADING} Creating event...")
        # await event_api.create_event(event)
        await message.edit(content=f"{e.CHECK} Event created!", embed=event.get_embed())
