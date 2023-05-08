import asyncio
import requests
import gspread
from .logger import logger


async def get_user_items(shadow_token, waxpeer_token, csgo_market_token):
    all_items_data = {
        "items": {},
        "status": None
    }
    try:
        async def get_buff():
            buff_items = {}
            service_account = gspread.service_account(filename="website/buff_keys.json")
            sheet = service_account.open("Buff Data")
            worksheet = sheet.worksheet("Sheet1")
            buff_data = worksheet.get_all_records()
            for item_buff in buff_data:
                item_name = item_buff["ITEM"]
                item_listing = item_buff["LISTING"]
                item_buy_order = item_buff["BUY ORDER"]
                item_listing7 = item_buff["LISTING_7"]
                item_listing30 = item_buff["LISTING_30"]
                item_listing60 = item_buff["LISTING_60"]

                buff_items[item_name] = {}
                buff_items[item_name]["listing"] = item_listing
                buff_items[item_name]["buy_order"] = item_buy_order
                buff_items[item_name]["listing7"] = item_listing7
                buff_items[item_name]["listing30"] = item_listing30
                buff_items[item_name]["listing60"] = item_listing60

            return buff_items

        async def get_shadowpay():
            shadowpay_items = {}
            shadow_headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {shadow_token}"
            }
            shadowpay_response = requests.get(f"https://api.shadowpay.com/api/v2/user/offers?limit=100",
                                              headers=shadow_headers).json()

            for item_shadow in shadowpay_response["data"]:
                item_name = item_shadow["steam_item"]["steam_market_hash_name"]
                item_current_price = item_shadow["price"]
                image = item_shadow["steam_item"]["icon"]
                shadowpay_items[item_name] = {
                    "price": item_current_price,
                    "image": image
                }

            total_items = int(shadowpay_response["metadata"]["total"])

            if total_items > 100:
                offset = 100
                while total_items > offset:
                    shadowpay_response = requests.get(
                        f"https://api.shadowpay.com/api/v2/user/offers?limit=100&offset={offset}",
                        headers=shadow_headers).json()

                    for item_shadow in shadowpay_response["data"]:
                        item_name = item_shadow["steam_item"]["steam_market_hash_name"]
                        item_current_price = item_shadow["price"]
                        image = item_shadow["steam_item"]["icon"]
                        shadowpay_items[item_name] = {
                            "price": item_current_price,
                            "image": image
                        }
                    offset += 100
            return shadowpay_items

        async def get_waxpeer():
            waxpeer_items = {}
            waxpeer_response = requests.get(f"https://api.waxpeer.com/v1/list-items-steam?api={waxpeer_token}"
                                            f"&game=csgo").json()
            for item_waxpeer in waxpeer_response["items"]:
                item_name = item_waxpeer["name"]
                item_current_price = price_beautify(item_waxpeer["price"])
                image = item_waxpeer["steam_price"]["img"]
                waxpeer_items[item_name] = {
                    "price": item_current_price,
                    "image": image
                }
            return waxpeer_items

        async def get_csgo_market():
            csgo_market_items = {}
            csgo_market_response = requests.get(f"https://market.csgo.com/api/v2/items?key={csgo_market_token}").json()

            for item_csgo_market in csgo_market_response["items"]:
                item_name = item_csgo_market["market_hash_name"]
                item_current_price = item_csgo_market["price"]
                csgo_market_items[item_name] = item_current_price

            return csgo_market_items

        shadowpay = asyncio.create_task(get_shadowpay())
        waxpeer = asyncio.create_task(get_waxpeer())
        csgo_market = asyncio.create_task(get_csgo_market())
        buff = asyncio.create_task(get_buff())
        await asyncio.gather(shadowpay, waxpeer, csgo_market, buff)
        buff = buff.result()
        for item, values in shadowpay.result().items():
            if item in buff:
                all_items_data["items"][item] = {}
                all_items_data["items"][item]["shadowpay_price"] = values["price"]
                all_items_data["items"][item]["listing"] = buff[item]["listing"]
                all_items_data["items"][item]["buy_order"] = buff[item]["buy_order"]
                all_items_data["items"][item]["listing7"] = buff[item]["listing7"]
                all_items_data["items"][item]["listing30"] = buff[item]["listing30"]
                all_items_data["items"][item]["listing60"] = buff[item]["listing60"]
                all_items_data["items"][item]["image"] = values["image"]

        for item, values in waxpeer.result().items():
            if item in all_items_data["items"]:
                all_items_data["items"][item]["waxpeer_price"] = values["price"]
            else:
                if item in buff:
                    all_items_data["items"][item] = {}
                    all_items_data["items"][item]["waxpeer_price"] = values["price"]
                    all_items_data["items"][item]["listing"] = buff[item]["listing"]
                    all_items_data["items"][item]["buy_order"] = buff[item]["buy_order"]
                    all_items_data["items"][item]["listing7"] = buff[item]["listing7"]
                    all_items_data["items"][item]["listing30"] = buff[item]["listing30"]
                    all_items_data["items"][item]["listing60"] = buff[item]["listing60"]
                    all_items_data["items"][item]["image"] = values["image"]

        for item, price in csgo_market.result().items():
            if item in all_items_data["items"]:
                all_items_data["items"][item]["csgo_market_price"] = price
            else:
                if item in buff:
                    all_items_data["items"][item] = {}
                    all_items_data["items"][item]["listing"] = buff[item]["listing"]
                    all_items_data["items"][item]["buy_order"] = buff[item]["buy_order"]
                    all_items_data["items"][item]["listing7"] = buff[item]["listing7"]
                    all_items_data["items"][item]["listing30"] = buff[item]["listing30"]
                    all_items_data["items"][item]["listing60"] = buff[item]["listing60"]
                    all_items_data["items"][item]["csgo_market_price"] = price

        for item in all_items_data["items"]:
            if "shadowpay_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["shadowpay_price"] = 0
            if "waxpeer_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["waxpeer_price"] = 0
            if "csgo_market_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["csgo_market_price"] = 0

        all_items_data["status"] = "success"
        logger.info("success")
        return all_items_data

    except BaseException as error:
        all_items_data["status"] = error
        logger.error(error)
        return all_items_data


def price_beautify(item_price):
    item_price_str = str(item_price)
    item_price_len = len(item_price_str)
    item_price_converted = f"{str(item_price_str)[:(item_price_len - 3)]}." + f"{item_price_str[item_price_len - 3:]}"
    return float(item_price_converted).__round__(2)
