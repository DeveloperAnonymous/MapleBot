import logging

import discord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("maplebot")
logging.getLogger("discord.state").setLevel(logging.ERROR)


class MarketAlertException(Exception):
    def __init__(self, channel: discord.TextChannel, message: str):
        self.channel = channel
        self.message = message

    def get_message(self):
        return f":bangbang: **{self.message}**"
