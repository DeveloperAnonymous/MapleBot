import logging

import discord

import configs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("maplebot")
logging.getLogger("discord.state").setLevel(logging.ERROR)


class MarketAlertException(Exception):
    def __init__(self, channel: discord.TextChannel, message: str):
        self.channel = channel
        self.message = message

    def get_message(self):
        return f":bangbang: **{self.message}**"


def get_datacenters() -> list[str]:
    """
    Get a list of all available datacenters.

    Returns:
        list[str]: List of datacenters.
    """
    return sorted([datacenter for datacenters in configs.REGIONS.values() for datacenter in datacenters.keys()])


def get_worlds() -> list[str]:
    """
    Get a list of all available worlds.

    Returns:
        list[str]: List of worlds.
    """
    return sorted([world for datacenters in configs.REGIONS.values() for world in datacenters.values()])


def get_datacenter_for_world(world: str) -> str | None:
    """
    Get the datacenter for a given world.

    Args:
        world (str): The world to get the datacenter for.

    Returns:
        str: The datacenter for the given world.
    """
    for datacenters in configs.REGIONS.values():
        for datacenter, worlds in datacenters.items():
            if world in worlds:
                return datacenter

    return None
