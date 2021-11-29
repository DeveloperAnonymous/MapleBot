from datetime import datetime
from typing import List

from . import UniversalisItemListing


class UniversalisItem:
    def __init__(self, raw_item) -> None:
        self.id: int = raw_item['itemID']
        self.last_updated: datetime = datetime.fromtimestamp(float(raw_item['lastUploadTime'])/1000)
        self.listings: List[UniversalisItemListing] = build_listings(raw_item['listings'])
        self.min_price_nq: int = raw_item['minPriceNQ']
        self.min_price_hq: int = raw_item['minPriceHQ']


def build_listings(raw_listings) -> List[UniversalisItemListing]:
    return [UniversalisItemListing(raw_listing) for raw_listing in raw_listings]
