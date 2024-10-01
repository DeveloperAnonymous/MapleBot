from . import SaddlebagItemState


class SaddlebagItem:
    avg: int
    item_id: str
    market_value: int
    median: int
    min_price: int
    name: str
    npc_vendor_info: str
    purchase_amount: int
    quantity_sold: int
    url: str
    percent_change: float
    state: SaddlebagItemState

    def __init__(self, data: dict):
        self.avg = data["avg"]
        self.item_id = data["itemID"]
        self.market_value = data["marketValue"]
        self.median = data["median"]
        self.min_price = data["minPrice"]
        self.name = data["name"]
        self.npc_vendor_info = data["npc_vendor_info"]
        self.purchase_amount = data["purchaseAmount"]
        self.quantity_sold = data["quantitySold"]
        self.url = data["url"]
        self.percent_change = data["percentChange"]
        self.state = SaddlebagItemState(data["state"])
