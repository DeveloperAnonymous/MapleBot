"""
This module contains the Job enum class.
"""

from enum import Enum


class Job(Enum):
    """
    Enum class to represent the different jobs in the game.

    Attributes:
        acronyme (str): The acronyme of the job.
        name (str): The name of the job.
    """

    ### Tanks ###
    DRK = ("DRK", "Dark Knight")
    GNB = ("GNB", "Gunbreaker")
    PLD = ("PLD", "Paladin")
    WAR = ("WAR", "Warrior")

    ### Healers ###
    AST = ("AST", "Astrologian")
    SCH = ("SCH", "Scholar")
    SGE = ("SGE", "Sage")
    WHM = ("WHM", "White Mage")

    ### DPS ###
    # Melee
    DRG = ("DRG", "Dragoon")
    MNK = ("MNK", "Monk")
    NIN = ("NIN", "Ninja")
    SAM = ("SAM", "Samurai")
    RPR = ("RPR", "Reaper")

    # Ranged
    BRD = ("BRD", "Bard")
    DNC = ("DNC", "Dancer")
    MCH = ("MCH", "Machinist")

    # Magic
    BLM = ("BLM", "Black Mage")
    BLU = ("BLU", "Blue Mage")
    SMN = ("SMN", "Summoner")
    RDM = ("RDM", "Red Mage")

    def __init__(self, acronyme, name):
        self._acronyme = acronyme
        self._name = name

    @property
    def acronyme(self):
        """Returns the acronyme of the job."""
        return self._acronyme

    @property
    def job_name(self):
        """Returns the name of the job."""
        return self._name
