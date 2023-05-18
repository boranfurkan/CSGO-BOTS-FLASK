import gspread


class GoogleSheet:
    def __init__(self):
        self.service_account = gspread.service_account(filename="/Users/boran/Desktop/CSGO-FLASK/website/utils/buy_utils/buff_keys.json")
        self.sheet = "Buff Data"
        self._buff_dict = {}
        self._steam_dict = {}

    async def get_buff_items(self):
        sheet = self.service_account.open(self.sheet)
        worksheet = sheet.worksheet("Sheet1")
        buff_data = worksheet.get_all_records()
        for item_buff in buff_data:
            item_name = item_buff["ITEM"]
            item_listing = item_buff["LISTING"]
            item_buy_order = item_buff["BUY ORDER"]
            item_listing7 = item_buff["LISTING_7"]
            item_listing30 = item_buff["LISTING_30"]
            item_listing60 = item_buff["LISTING_60"]

            self._buff_dict[item_name] = {}
            self._buff_dict[item_name]["listing"] = item_listing
            self._buff_dict[item_name]["buy_order"] = item_buy_order
            self._buff_dict[item_name]["listing7"] = item_listing7
            self._buff_dict[item_name]["listing30"] = item_listing30
            self._buff_dict[item_name]["listing60"] = item_listing60
        return self._buff_dict

    async def get_steam_inventories(self):
        sheet = self.service_account.open(self.sheet)
        worksheet = sheet.worksheet("Sheet2")
        users = worksheet.row_values(1)
        for idx, user in enumerate(users):
            items_of_user = worksheet.col_values(idx + 1)
            for item_name in items_of_user[1:]:
                self._steam_dict[item_name] = user

        return self._steam_dict

    def get_buff_dict(self):
        return self._buff_dict

    def set_buff_dict(self, new_dict: dict):
        self._buff_dict = new_dict

    def get_steam_dict(self):
        return self._steam_dict

    def set_steam_dict(self, new_dict: dict):
        self._steam_dict = new_dict
