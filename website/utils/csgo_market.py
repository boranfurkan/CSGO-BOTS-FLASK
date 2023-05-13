import time
import requests


class CsgoMarket:

    def __init__(self, secret_key, discount):
        self.key = secret_key
        self.discount = discount

        self._inventory = {}
        self.__links_array = []
        self.__market_data = {}
        self.__history = {}
        self.__items_to_update = {}
        self.__logs = []
        self.__user_headers = {
            "Content-Type": "application/json",
        }

    def get_inventory(self, user_items):
        response = requests.get(f"https://market.csgo.com/api/v2/items?key={self.key}",
                                headers=self.__user_headers).json()

        for item in response["items"]:
            item_name = item["market_hash_name"]
            if item_name in user_items:
                item_id = item["item_id"]
                current_price = item["price"] * 1000
                suggested_price = user_items[item_name] * 1000
                self._inventory[item_name] = {}
                self._inventory[item_name]["id"] = item_id
                self._inventory[item_name]["suggested_price"] = suggested_price
                self._inventory[item_name]["price"] = current_price
                self.__history[item_id] = {"name": item_name, "price": current_price}
            else:
                print(f"Please add {item_name} into special items. There is no buff data found!")
        return self._inventory

    def create_links(self):
        url = f"https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?key={self.key}"
        for k in range(0, len(self._inventory), 50):
            separated_array = list(self._inventory.keys())[k:k + 50]
            for key in separated_array:
                url += "&list_hash_name[]=" + key
            self.__links_array.append(url)
            url = f"https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?key={self.key}"
        return self.__links_array

    def request_market_data(self):
        counter = 0
        for url in self.__links_array:
            response = requests.get(url, headers=self.__user_headers).json()
            for item in response["data"]:
                item_name = item
                for unique_item in response["data"][item_name]:
                    item_id = unique_item["id"]
                    item_price = int(unique_item["price"])
                    if item_name not in self.__market_data:
                        self.__market_data[item_name] = []
                        self.__market_data[item_name].append({"id": item_id, "price": item_price})
                    else:
                        self.__market_data[item_name].append({"id": item_id, "price": item_price})
            counter += 1
            if counter == 5:
                time.sleep(1)
                counter = 0
        for item in self.__market_data:
            self.__market_data[item].sort(key=lambda x: x["price"])
        return self.__market_data

    def update_items(self):
        for item in self.__market_data:
            if len(self.__market_data[item]) == 1:
                id_to_update = self._inventory[item]["id"]
                price_to_update = self._inventory[item]["suggested_price"] - 20
            else:
                range_value = float(self._inventory[item]["suggested_price"] * (100 - self.discount) / 100).__round__(2)

                if int(self.__market_data[item][0]["id"]) != int(self._inventory[item]["id"]):
                    item_price = int(self.__market_data[item][0]["price"])
                    if range_value <= item_price <= self._inventory[item]["suggested_price"]:
                        id_to_update = self._inventory[item]["id"]
                        price_to_update = self.__market_data[item][0]["price"] - 20
                    else:
                        id_to_update = self._inventory[item]["id"]
                        price_to_update = self._inventory[item]["suggested_price"] - 20
                else:
                    second_item_price = self.__market_data[item][1]["price"]
                    if range_value <= second_item_price <= self._inventory[item]["suggested_price"]:
                        id_to_update = self._inventory[item]["id"]
                        price_to_update = second_item_price - 20
                    else:
                        id_to_update = self._inventory[item]["id"]
                        price_to_update = self._inventory[item]["suggested_price"] - 20

            if float(price_to_update).__round__(2) != float(self.__history[id_to_update]["price"]).__round__(2):
                self.__history[id_to_update]["price"] = price_to_update
                self.__items_to_update[item] = {}
                self.__items_to_update[item]["item_id"] = id_to_update
                self.__items_to_update[item]["price"] = price_to_update

        counter = 0
        for item, values in self.__items_to_update.items():
            item_name = item
            item_id = values["item_id"]
            item_price = values["price"]
            response = requests.post(f"https://market.csgo.com/api/v2/set-price?key={self.key}&item_id={item_id}"
                                     f"&price={item_price}&cur=USD", headers=self.__user_headers).json()
            counter += 1
            if counter == 5:
                time.sleep(1)
                counter = 0
            self.__logs.append(f"{item_name} is updated to: {item_price}, {response}")

        return self.get_logs()

    def make_user_online(self):
        response = requests.get(f"https://market.csgo.com/api/v2/ping?key={self.key}").text
        return response

    def set_items_to_update(self, new_dict: dict):
        self.__items_to_update = new_dict
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
        return self.__items_to_update["items"]

    def get_links_array(self):
        return self.__links_array

    def get_market_data(self):
        return self.__market_data

    def get_logs(self):
        return self.__logs