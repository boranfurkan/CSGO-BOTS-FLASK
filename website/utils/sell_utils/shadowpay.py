import requests


# Class Shadow defines the Shadow object
class Shadow:

    def __init__(self, user_token, merchant_token, discount):
        # The constructor of the Shadow class
        self.user_token = user_token
        self.merchant_token = merchant_token
        self.discount = discount

        self.volume_dict = {}
        self.suggested_prices_dict = {}

        # Private variables are initialized
        self._inventory = {}
        self.__links_array = []
        self.__market_data = {}
        self.__history = {}
        self.__items_to_update = {"offers": []}
        self.__logs = []

        # The authorization headers for user and merchant are initialized
        self.__user_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.user_token}"
        }

        self.__merchant_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.merchant_token}"
        }

    # Method to get the inventory of user items
    async def get_inventory(self, user_items, is_for_sale: bool):
        request_shadow = requests.get("https://api.shadowpay.com/api/v2/user/offers?limit=999",
                                      headers=self.__user_headers).json()

        for item in request_shadow["data"]:
            item_id = item["id"]
            item_name = item["steam_item"]["steam_market_hash_name"]
            current_price = float((item["price"])).__round__(2)
            image = item["steam_item"]["icon"]
            if is_for_sale:
                if item_name in user_items:
                    suggested_price = user_items[item_name]
                    self._inventory[item_name] = {}
                    self._inventory[item_name]["id"] = item_id
                    self._inventory[item_name]["suggested_price"] = suggested_price
                    self._inventory[item_name]["price"] = current_price
                    self._inventory[item_name]["image"] = image
                    self.__history[item_id] = current_price
                else:
                    print(f"Please add {item_name} into special items. There is no buff data found!")
            else:
                self._inventory[item_name] = {}
                self._inventory[item_name]["id"] = item_id
                self._inventory[item_name]["suggested_price"] = item["steam_item"]["suggested_price"]
                self._inventory[item_name]["price"] = current_price
                self._inventory[item_name]["image"] = image
                self.__history[item_id] = current_price

        total_items = int(request_shadow["metadata"]["total"])
        if total_items > 100:
            offset = 100
            while total_items > offset:
                request_shadow = requests.get(
                    f"https://api.shadowpay.com/api/v2/user/offers?limit=100&offset={offset}",
                    headers=self.__user_headers).json()

                for item in request_shadow["data"]:
                    item_id = item["id"]
                    item_name = item["steam_item"]["steam_market_hash_name"]
                    current_price = float((item["price"])).__round__(2)
                    image = item["steam_item"]["icon"]
                    if is_for_sale:
                        if item_name in user_items:
                            suggested_price = user_items[item_name]
                            self._inventory[item_name] = {}
                            self._inventory[item_name]["id"] = item_id
                            self._inventory[item_name]["suggested_price"] = suggested_price
                            self._inventory[item_name]["price"] = current_price
                            self._inventory[item_name]["image"] = image
                            self.__history[item_id] = current_price
                        else:
                            print(f"Please add {item_name} into special items. There is no buff data found!")
                    else:
                        self._inventory[item_name] = {}
                        self._inventory[item_name]["id"] = item_id
                        self._inventory[item_name]["suggested_price"] = item["steam_item"]["suggested_price"]
                        self._inventory[item_name]["price"] = current_price
                        self._inventory[item_name]["image"] = image
                        self.__history[item_id] = current_price
                offset += 100
        return self._inventory

    # Method to create links for user's inventory items
    def create_links(self):
        url = "https://api.shadowpay.com/api/v2/merchant/items?limit=999"
        for k in range(0, len(self._inventory), 70):
            separated_array = list(self._inventory.keys())[k:k + 70]
            for key in separated_array:
                url += "&steam_market_hash_name[]=" + key
            self.__links_array.append(url)
            url = "https://api.shadowpay.com/api/v2/merchant/items&project=csgo&limit=999"
        return self.__links_array

    # Method to update user's inventory items
    def update_items(self):
        for link in self.__links_array:
            response = requests.get(link, headers=self.__merchant_headers).json()
            for item in response["data"]:
                item_name = item["steam_item"]["steam_market_hash_name"]
                item_id = item["id"]
                item_price = float(item["price"]).__round__(2)

                if item_name not in self.__market_data:
                    self.__market_data[item_name] = []
                    self.__market_data[item_name].append({"id": item_id, "price": item_price})
                else:
                    self.__market_data[item_name].append({"id": item_id, "price": item_price})

        for item in self.__market_data:
            self.__market_data[item].sort(key=lambda x: x["price"])

        for item in self.__market_data:
            if len(self.__market_data[item]) == 1:
                id_to_update = self._inventory[item]["id"]
                price_to_update = self._inventory[item]["suggested_price"] - 0.01
            else:
                range_value = float(self._inventory[item]["suggested_price"] * (100 - self.discount) / 100).__round__(2)

                if int(self.__market_data[item][0]["id"]) != int(self._inventory[item]["id"]):
                    item_price = int(self.__market_data[item][0]["price"])
                    if range_value <= item_price <= self._inventory[item]["suggested_price"]:
                        id_to_update = self._inventory[item]["id"]
                        price_to_update = float(self.__market_data[item][0]["price"] - 0.01).__round__(2)
                    else:
                        id_to_update = self._inventory[item]["id"]
                        price_to_update = self._inventory[item]["suggested_price"] - 0.01
                else:
                    second_item_price = float(self.__market_data[item][1]["price"]).__round__(2)
                    if range_value <= second_item_price <= self._inventory[item]["suggested_price"]:
                        id_to_update = self._inventory[item]["id"]
                        price_to_update = (second_item_price - 0.01).__round__(2)
                    else:
                        id_to_update = self._inventory[item]["id"]
                        price_to_update = self._inventory[item]["suggested_price"] - 0.01

            if float(price_to_update).__round__(2) != float(self.__history[id_to_update]).__round__(2):
                self.__history[id_to_update] = price_to_update
                self.__items_to_update["offers"].append(
                    {
                        "id": id_to_update,
                        "price": price_to_update,
                        "currency": "USD"
                    }
                )

        for k in range(0, len(self.__items_to_update["offers"]), 250):
            new_array = self.__items_to_update["offers"][k:k + 250]
            data = {"offers": new_array}
            response = requests.patch(f"https://api.shadowpay.com/api/v2/user/offers",
                                      headers=self.__user_headers,
                                      json=data).json()

            self.__logs.append(f"Total Updated: {response['metadata']['total_updated_items']} "
                               f"Total Not Updated: {response['metadata']['total_not_updated_items']}")
            for item in response["updated_items"]:
                self.__logs.append(f"{item['steam_item']['steam_market_hash_name']} is updated to: {item['price']}")
        return self.get_logs()

    # Method to get the volume of items
    async def get_items_volume(self):
        response = requests.get(f"https://api.shadowpay.com/api/v2/user/items/prices?token={self.user_token}").json()
        for item in response["data"]:
            item_name = item["steam_market_hash_name"]
            item_price = float(item["price"])
            item_count = int(item["volume"])

            self.volume_dict[item_name] = {}
            self.volume_dict[item_name]["price"] = item_price
            self.volume_dict[item_name]["count"] = item_count
        return self.volume_dict

    # Method to get the suggested prices for items
    async def get_suggested_prices(self):
        response = requests.get(f"https://api.shadowpay.com/api/v2/user/items/steam?token={self.user_token}").json()
        for item in response["data"]:
            item_name = item["steam_market_hash_name"]
            price = float(item["suggested_price"])
            if price > 35:
                if item_name[:7] != "Sticker":
                    self.suggested_prices_dict[item_name] = price

    # Getter method to get the dictionary of suggested prices
    def get_suggested_prices_dict(self):
        return self.suggested_prices_dict

    # Setter method to set a new dictionary of suggested prices
    def set_suggested_prices_dict(self, new_dict: dict):
        self.suggested_prices_dict = new_dict

    def set_items_to_update(self, new_array: list):
        self.__items_to_update["offers"] = new_array
        return self.__items_to_update

    # Setter method to set a new array of items to update
    def set_links_array(self, new_array: list):
        self.__links_array = new_array
        return self.__links_array

    # Setter method to set a new dictionary of market data
    def set_market_data(self, new_dict: dict):
        self.__market_data = new_dict
        return self.__market_data

    # Setter method to set a new array of logs
    def set_logs(self, new_array: list):
        self.__logs = new_array
        return self.__logs

    # Getter method to get the array of items to update
    def get_items_to_update(self):
        return self.__items_to_update["offers"]

    # Getter method to get the array of links
    def get_links_array(self):
        return self.__links_array

    # Getter method to get the dictionary of market data
    def get_market_data(self):
        return self.__market_data

    # Getter method to get the array of logs
    def get_logs(self):
        return self.__logs
