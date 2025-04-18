import logging

import discord

import configs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("maplebot")
logging.getLogger("discord.state").setLevel(logging.ERROR)

ALL_DATACENTERS = sorted(
    datacenter_name for region_datacenters in configs.REGIONS.values() for datacenter_name in region_datacenters.keys()
)

ALL_WORLDS = sorted(
    world
    for region_datacenters in configs.REGIONS.values()
    for worlds in region_datacenters.values()
    for world in worlds
)

WORLD_TO_DATACENTER = {
    world: datacenter
    for datacenters in configs.REGIONS.values()
    for datacenter, worlds in datacenters.items()
    for world in worlds
}


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
    return ALL_DATACENTERS


def get_worlds() -> list[str]:
    """
    Get a list of all available worlds.

    Returns:
        list[str]: List of worlds.
    """
    return ALL_WORLDS


def get_datacenter_for_world(world: str) -> str | None:
    """
    Get the datacenter for a given world.

    Args:
        world (str): The world to get the datacenter for.

    Returns:
        str: The datacenter for the given world.
    """
    return WORLD_TO_DATACENTER.get(world)
