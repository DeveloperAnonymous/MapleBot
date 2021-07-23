import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('marketalert')
logging.getLogger('discord.state').setLevel(logging.ERROR)

class MarketAlertException(Exception):
    def __init__(self, channel, message):
        self.channel = channel
        self.message = message

    def get_message(self):
        return f":bangbang: **{self.message}**"


