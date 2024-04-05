from typing import List

import discord

from .participant import Participant
from .requirement import Requirement

class Event:
    def __init__(self, name: str, description: str, participants: List[Participant], requirements: List[Requirement], owner: discord.Member):
        self.name = name
        self.owner = owner
        self.description = description
        self.participants = participants
        self.requirements = requirements

    def get_embed(self):
        # Create a discord.Embed object
        embed = discord.Embed(title=self.name, description=self.description)
        embed.set_footer(text="Created by {}".format(self.owner.name))

        # Add the participants
        participants_output = ""
        for participant in self.participants:
            # Build the participant value
            participants_output += f"{participant.name} ({participant.job.name})\n"

        embed.add_field(name="Participants", value=participants_output, inline=False)

        # Add the requirements
        requirements_output = ""
        for requirement in self.requirements:
            # Build the requirement value
            requirements_output += f"{requirement.name} - {requirement.value}\n"

        embed.add_field(name="Requirements", value=requirements_output, inline=False)

        return embed
        