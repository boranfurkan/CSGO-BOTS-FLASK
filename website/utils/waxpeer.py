import requests


class Waxpeer:

    def __init__(self, token, cookie, discount):
        self.token = token
        self.cookie = cookie
        self.discount = discount

        self._inventory = {}
        self.__market_data = {}
        self.__history = {}
        self.__items_to_update = {"items": []}
        self.__logs = []
        self.__headers = {}

    def get_inventory(self, user_items):
        response = requests.get(f"https://api.waxpeer.com/v1/list-items-steam?api={self.token}").json()

        for item in response["items"]:
            item_name = item["name"]
            if item_name in user_items:
                item_id = item["item_id"]
                current_price = item["price"]
                suggested_price = user_items[item_name] * 1000
                self._inventory[item_name] = {}
                self._inventory[item_name]["id"] = item_id
                self._inventory[item_name]["suggested_price"] = suggested_price
                self._inventory[item_name]["price"] = current_price
                self.__history[item_id] = {"name": item_name, "price": current_price}
            else:
                print(f"Please add {item_name} into special items. There is no buff data found!")
        return self._inventory

    def request_market_data(self):
        base_url = f"https://api.waxpeer.com/v1/mass-info?api={self.token}"
        for k in range(0, len(self._inventory), 50):

            data = {"name": [], "sell": 1}
            separated_array = list(self._inventory.keys())[k:k + 50]

            for item in separated_array:
                data["name"].append(item)

            response = requests.post(base_url, json=data).json()
            for item in response["data"]:
                for listing in response["data"][item]["listings"]:
                    item_name = item
                    item_id = listing["item_id"]
                    item_price = listing["price"]
                    if item_name not in self.__market_data:
                        self.__market_data[item_name] = []
                        self.__market_data[item_name].append({"id": item_id, "price": item_price})
                    else:
                        self.__market_data[item_name].append({"id": item_id, "price": item_price})

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
                self.__items_to_update["items"].append(
                    {
                        "item_id": id_to_update,
                        "price": price_to_update,
                    }
                )

        for k in range(0, len(self.__items_to_update["items"]), 50):
            new_array = self.__items_to_update["items"][k:k + 50]
            data = {"items": new_array}
            response = requests.post(f"https://api.waxpeer.com/v1/edit-items?api={self.token}", json=data).json()
            self.__logs.append(f"Total Updated: {len(response['updated'])} "
                               f"Total Not Updated: {len(response['failed'])}")

            for item in response["updated"]:
                self.__logs.append(f"{item['item_id']} is updated to: {item['price']}")
        return self.get_logs()

    def set_items_to_update(self, new_array: list):
        self.__items_to_update["items"] = new_array
        return self.__items_to_update

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
