from maplebot.job import Job


class Participant:
    def __init__(self, id: int, name: str, job: Job, level: int):
        self.id = id
        self.name = name
        self.job = job
        self.level = level
