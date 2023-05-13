import requests


class Shadow:

    def __init__(self, user_token, merchant_token, discount):
        self.user_token = user_token
        self.merchant_token = merchant_token
        self.discount = discount
        self._inventory = {}
        self.__links_array = []
        self.__market_data = {}
        self.__history = {}
        self.__items_to_update = {"offers": []}
        self.__logs = []
        self.__user_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.user_token}"
        }

        self.__merchant_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.merchant_token}"
        }

    def get_inventory(self, user_items):
        request_shadow = requests.get("https://api.shadowpay.com/api/v2/user/offers?limit=999",
                                      headers=self.__user_headers).json()

        for item in request_shadow["data"]:
            item_id = item["id"]
            item_name = item["steam_item"]["steam_market_hash_name"]
            current_price = float((item["price"])).__round__(2)
            if item_name in user_items:
                suggested_price = user_items[item_name]
                self._inventory[item_name] = {}
                self._inventory[item_name]["id"] = item_id
                self._inventory[item_name]["suggested_price"] = suggested_price
                self._inventory[item_name]["price"] = current_price
                self.__history[item_id] = current_price
            else:
                print(f"Please add {item_name} into special items. There is no buff data found!")

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
                    if item_name in user_items:
                        suggested_price = user_items[item_name]
                        self._inventory[item_name] = {}
                        self._inventory[item_name]["id"] = item_id
                        self._inventory[item_name]["suggested_price"] = suggested_price
                        self._inventory[item_name]["price"] = current_price
                        self.__history[item_id] = current_price
                    else:
                        print(f"Please add {item_name} into special items. There is no buff data found!")
                offset += 100
        return self._inventory

    def create_links(self):
        url = "https://api.shadowpay.com/api/v2/merchant/items?limit=999"
        for k in range(0, len(self._inventory), 70):
            separated_array = list(self._inventory.keys())[k:k + 70]
            for key in separated_array:
                url += "&steam_market_hash_name[]=" + key
            self.__links_array.append(url)
            url = "https://api.shadowpay.com/api/v2/merchant/items&project=csgo&limit=999"
        return self.__links_array

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

    def set_items_to_update(self, new_array: list):
        self.__items_to_update["offers"] = new_array
        return self.__items_to_update

    def set_links_array(self, new_array: list):
        self.__links_array = new_array
        return self.__links_array

    def set_market_data(self, new_dict: dict):
        self.__market_data = new_dict
        return self.__market_data

    def set_logs(self, new_array: list):
        self.__logs = new_array
        return self.__logs

    def get_items_to_update(self):
        return self.__items_to_update["offers"]

    def get_links_array(self):
        return self.__links_array

    def get_market_data(self):
        return self.__market_data

    def get_logs(self):
        return self.__logs
