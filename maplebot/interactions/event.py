import discord
from discord import ui

class EventInteraction(ui.View):
    def __init__(self, author: discord.Member):
        self.author = author
        