from enum import Enum

from maplebot.job import Job


class RequirementType(Enum):
    ILVL = "ilvl"
    LEVEL = "level"
    JOB = "job"
    PARTICIPANTS = "participants"

    @property
    def expected_type(self):
        match self:
            case (self.ILVL, self.LEVEL, self.PARTICIPANTS):
                return int
            case self.JOB:
                return Job
            case _:
                raise ValueError("Unknown requirement type")


class Requirement:
    def __init__(self, name: str, value: int | Job, req_type: RequirementType):
        if not isinstance(value, req_type.expected_type):
            raise ValueError("Value is not of the expected type")

        self.name = name
        self.value = value
        self.type = req_type


class ILVLRequirement(Requirement):
    def __init__(self, value: int | Job):
        super().__init__("Minimum ILVL", value, RequirementType.ILVL)


class LevelRequirement(Requirement):
    def __init__(self, value: int | Job):
        super().__init__("Minimum Level", value, RequirementType.LEVEL)


class JobRequirement(Requirement):
    def __init__(self, value: int | Job):
        super().__init__("Job", value, RequirementType.JOB)


class ParticipantsRequirement(Requirement):
    def __init__(self, value: int | Job):
        super().__init__("Maximum participants", value, RequirementType.PARTICIPANTS)
