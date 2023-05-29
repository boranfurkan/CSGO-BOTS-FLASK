# Importing necessary libraries
import time
import requests
from website.utils.common_functions import price_beautify


# Defining a class Empire
class Empire:
    def __init__(self, csgo_empire_token):
        # Initializing object with the provided token
        # Two dictionaries are created to store market and auction data
        self.token = csgo_empire_token
        self._market_dict = {}
        self._auction_dict = {}

        # Headers for the request to the API
        self.__headers = {
            "Authorization": f"Bearer {self.token}"
        }

    # This method fetches the market items from the Empire API
    async def get_market_items(self):
        # This nested function returns the last page info from the API
        def get_last_page_info():
            return requests.get("https://csgoempire.com/api/v2/trading/items?per_page=2500&page=1&price_min=4000"
                                "&price_max=400000&price_max_above=999&sort=desc&order=market_value",
                                headers=self.__headers).json()["last_page"]

        # Iterating through all pages from 1 to the last page
        for page in range(1, get_last_page_info()):
            time.sleep(0.25)
            response = requests.get(
                f"https://csgoempire.com/api/v2/trading/items?per_page=2500&page={page}&price_min=4000&"
                f"price_max=400000&price_max_above=999&sort=desc&order=market_value", headers=self.__headers).json()

            # Iterating through the items in the response and adding them to _market_dict
            # If an item already exists, update its count and price if current price is lower
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

    # This method fetches the auction items from the Empire API
    async def get_auction_items(self):
        # Requesting data from the API
        response = requests.get(
            f"https://csgoempire.com/api/v2/trading/items?per_page=2000&page=1&price_min=4000&"
            f"price_max=400000&price_max_above=999&auction=yes",
            headers=self.__headers)

        # Checking the response status code and handling accordingly
        if response.status_code == 200:
            response = response.json()
        elif response.status_code == 429:
            print("gg")

        # Iterating through the items in the response and adding them to _auction_dict
        # If an item already exists, update its count and price if current price is lower
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

    # Getter method for market data
    def get_market_dict(self):
        return self._market_dict

    # Getter method for auction data
    def get_auction_dict(self):
        return self._auction_dict

    # Setter method to update market data
    def set_market_dict(self, new_dict: dict):
        self._market_dict = new_dict

    # Setter method to update auction data
    def set_auction_dict(self, new_dict: dict):
        self._auction_dict = new_dict
