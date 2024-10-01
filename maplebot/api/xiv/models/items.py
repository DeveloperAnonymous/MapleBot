import configs


class XivApiItem:
    def __init__(self, raw_item) -> None:
        self.id: int = raw_item["row_id"]
        self.name: str = raw_item["fields"]["Name"]
        self.description: str = raw_item["fields"]["Description"]
        self.icon_url: str = f"{configs.XIVAPI_BASE_URL}/asset?path={raw_item["fields"]["Icon"]["path_hr1"]}&format=png"
