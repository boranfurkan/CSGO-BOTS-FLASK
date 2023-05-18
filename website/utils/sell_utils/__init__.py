from .shadowpay import Shadow
from .waxpeer import Waxpeer
from .csgo_market import CsgoMarket
from website.utils.buy_utils.google_sheet import GoogleSheet
from website.utils.common_functions import price_beautify
import asyncio


async def get_user_items(shadow_token, waxpeer_token, csgo_market_token):
    all_items_data = {
        "items": {},
        "status": ""
    }
    try:
        shadowpay_instance = Shadow(user_token=shadow_token, merchant_token="", discount=0)
        shadowpay_instance = asyncio.create_task(shadowpay_instance.get_inventory(user_items={}, is_for_sale=False))

        waxpeer_instance = Waxpeer(token=waxpeer_token, discount=0, cookie="")
        waxpeer_instance = asyncio.create_task(waxpeer_instance.get_inventory(user_items={}, is_for_sale=False))

        csgo_market_instance = CsgoMarket(secret_key=csgo_market_token, discount=0)
        csgo_market_instance = asyncio.create_task(csgo_market_instance.get_inventory(user_items={}, is_for_sale=False))

        sheet_data = GoogleSheet()
        buff = asyncio.create_task(sheet_data.get_buff_items())

        await asyncio.gather(shadowpay_instance, waxpeer_instance, csgo_market_instance, buff)
        buff = buff.result()
        for item, values in shadowpay_instance.result().items():
            if item in buff:
                all_items_data["items"][item] = {}
                all_items_data["items"][item]["shadowpay_price"] = values["price"]
                all_items_data["items"][item]["listing"] = buff[item]["listing"]
                all_items_data["items"][item]["buy_order"] = buff[item]["buy_order"]
                all_items_data["items"][item]["listing7"] = buff[item]["listing7"]
                all_items_data["items"][item]["listing30"] = buff[item]["listing30"]
                all_items_data["items"][item]["listing60"] = buff[item]["listing60"]
                all_items_data["items"][item]["image"] = values["image"]

        for item, values in waxpeer_instance.result().items():
            if item in all_items_data["items"]:
                all_items_data["items"][item]["waxpeer_price"] = price_beautify(values["price"], 3)
            else:
                if item in buff:
                    all_items_data["items"][item] = {}
                    all_items_data["items"][item]["waxpeer_price"] = price_beautify(values["price"], 3)
                    all_items_data["items"][item]["listing"] = buff[item]["listing"]
                    all_items_data["items"][item]["buy_order"] = buff[item]["buy_order"]
                    all_items_data["items"][item]["listing7"] = buff[item]["listing7"]
                    all_items_data["items"][item]["listing30"] = buff[item]["listing30"]
                    all_items_data["items"][item]["listing60"] = buff[item]["listing60"]
                    all_items_data["items"][item]["image"] = values["image"]

        for item, values in csgo_market_instance.result().items():
            if item in all_items_data["items"]:
                all_items_data["items"][item]["csgo_market_price"] = price_beautify(int(values["price"]), 3)
            else:
                if item in buff:
                    all_items_data["items"][item] = {}
                    all_items_data["items"][item]["listing"] = buff[item]["listing"]
                    all_items_data["items"][item]["buy_order"] = buff[item]["buy_order"]
                    all_items_data["items"][item]["listing7"] = buff[item]["listing7"]
                    all_items_data["items"][item]["listing30"] = buff[item]["listing30"]
                    all_items_data["items"][item]["listing60"] = buff[item]["listing60"]
                    all_items_data["items"][item]["csgo_market_price"] = price_beautify(int(values["price"]), 3)

        for item in all_items_data["items"]:
            if "shadowpay_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["shadowpay_price"] = 0
            if "waxpeer_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["waxpeer_price"] = 0
            if "csgo_market_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["csgo_market_price"] = 0

        all_items_data["status"] = "success"
        return all_items_data

    except BaseException as error:
        all_items_data["status"] = error
        return all_items_data

