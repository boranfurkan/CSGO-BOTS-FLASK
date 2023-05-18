import time
import requests
from website.utils.common_functions import price_beautify


class Empire:
    def __init__(self, csgo_empire_token):
        self.token = csgo_empire_token
        self._market_dict = {}
        self._auction_dict = {}

        self.__headers = {
            "Authorization": f"Bearer {self.token}"
        }

    async def get_market_items(self):
        def get_last_page_info():
            return requests.get("https://csgoempire.com/api/v2/trading/items?per_page=2500&page=1&price_min=4000"
                                "&price_max=400000&price_max_above=999&sort=desc&order=market_value",
                                headers=self.__headers).json()["last_page"]

        for page in range(1, get_last_page_info()):
            time.sleep(0.25)
            response = requests.get(
                f"https://csgoempire.com/api/v2/trading/items?per_page=2500&page={page}&price_min=4000&"
                f"price_max=400000&price_max_above=999&sort=desc&order=market_value", headers=self.__headers).json()

            for item in response["data"]:
                item_name = item["market_name"]
                item_price = price_beautify(item["market_value"], 2)
                if item_name in self._market_dict:
                    self._market_dict[item_name]["count"] += 1
                    if self._market_dict[item_name]["price"] > item_price:
                        self._market_dict[item_name]["price"] = item_price
                else:
                    self._market_dict[item_name] = {}
                    self._market_dict[item_name]["price"] = item_price
                    self._market_dict[item_name]["count"] = 1
        return self._market_dict

    async def get_auction_items(self):
        response = requests.get(
            f"https://csgoempire.com/api/v2/trading/items?per_page=2500&page=1&price_min=4000&"
            f"price_max=400000&price_max_above=999&sort=desc&order=market_value&auction=yes",
            headers=self.__headers).json()

        for item in response["data"]:
            item_name = item["market_name"]
            item_price = price_beautify(item["market_value"], 2)
            item_url = item["icon_url"]
            item_id = item["id"]
            item_end_time = item["auction_ends_at"]

            if item_name in self._auction_dict:
                self._auction_dict[item_name]["count"] += 1
                if self._auction_dict[item_name]["price"] > item_price:
                    self._auction_dict[item_name]["price"] = item_price
                    self._auction_dict[item_name]["url"] = item_url
                    self._auction_dict[item_name]["id"] = item_id
                    self._auction_dict[item_name]["end_time"] = item_end_time
            else:
                self._auction_dict[item_name] = {}
                self._auction_dict[item_name]["price"] = item_price
                self._auction_dict[item_name]["count"] = 1
                self._auction_dict[item_name]["url"] = item_url
                self._auction_dict[item_name]["id"] = item_id
                self._auction_dict[item_name]["end_time"] = item_end_time

        return self._auction_dict

    def get_market_dict(self):
        return self._market_dict

    def get_auction_dict(self):
        return self._auction_dict

    def set_market_dict(self, new_dict: dict):
        self._market_dict = new_dict

    def set_auction_dict(self, new_dict: dict):
        self._auction_dict = new_dict
