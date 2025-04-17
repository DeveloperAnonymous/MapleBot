class World:
    def __init__(self, region: str, datacenter: str, world: str):
        self.region = region
        self.datacenter = datacenter
        self.world = world

    def __str__(self):
        return f"{self.datacenter} - {self.world}"
