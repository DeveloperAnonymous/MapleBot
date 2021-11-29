import configs


class XivApiItem:
    def __init__(self, raw_item) -> None:
        self.id: int = raw_item["ID"]
        self.name: str = raw_item["Name"]
        self.description: str = raw_item["Description"]
        self.icon_url: str = configs.XIVAPI_BASE_URL + raw_item["IconHD"]
