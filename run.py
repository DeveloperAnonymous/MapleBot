"""
This module is the main entry point of the bot.
It creates the bot object and runs it.
"""

import configs
from maplebot import MapleBot

if __name__ == "__main__":
    bot = MapleBot(configs.PREFIX)
    bot.run(configs.TOKEN)
