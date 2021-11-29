from datetime import datetime

class UniversalisItemListing:
    def __init__(self, raw_listing) -> None:
        self.last_review_time: datetime = datetime.fromtimestamp(float(raw_listing['lastReviewTime'])/1000)
        self.price_per_unit: int = raw_listing["pricePerUnit"]
        self.quantity: int = raw_listing["quantity"]
        self.world_name: str = raw_listing["worldName"]
        self.hq: bool = raw_listing["hq"]
        # self.materia: list = raw_listing["materia"]
        self.total: int = raw_listing["total"]
