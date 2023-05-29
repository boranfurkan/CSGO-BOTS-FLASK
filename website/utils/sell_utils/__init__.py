# Import necessary modules and functions from other files
from .shadowpay import Shadow
from .waxpeer import Waxpeer
from .csgo_market import CsgoMarket
from website.utils.buy_utils.google_sheet import GoogleSheet
from website.utils.common_functions import price_beautify
import asyncio


# The asynchronous function that gets user items from different sources
async def get_user_items(shadow_token, waxpeer_token, csgo_market_token):
    # Initialize a dictionary to store all items data and status
    all_items_data = {
        "items": {},
        "status": ""
    }
    try:
        # Creating instances of Shadow, Waxpeer, and CsgoMarket classes using respective tokens,
        # and creating asyncio tasks to get inventories from them

        shadowpay_instance = Shadow(user_token=shadow_token, merchant_token="", discount=0)
        shadowpay_instance = asyncio.create_task(shadowpay_instance.get_inventory(user_items={}, is_for_sale=False))

        waxpeer_instance = Waxpeer(token=waxpeer_token, discount=0, cookie="")
        waxpeer_instance = asyncio.create_task(waxpeer_instance.get_inventory(user_items={}, is_for_sale=False))

        csgo_market_instance = CsgoMarket(secret_key=csgo_market_token, discount=0)
        csgo_market_instance = asyncio.create_task(csgo_market_instance.get_inventory(user_items={}, is_for_sale=False))

        sheet_data = GoogleSheet()
        # Creating an instance of GoogleSheet class and an asyncio task to get Buff items
        buff = asyncio.create_task(sheet_data.get_buff_items())

        # Gather all tasks and await for their completion
        await asyncio.gather(shadowpay_instance, waxpeer_instance, csgo_market_instance, buff)
        buff = buff.result()

        # Process the result of each task and store relevant information in all_items_data dictionary
        # If an item is found in both the user's inventory (Shadow, Waxpeer, or CsgoMarket) and Buff data,
        # it is stored with its price, listing, buy order, and image information.
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

        # Ensure that all items in all_items_data have 'shadowpay_price', 'waxpeer_price', and 'csgo_market_price'
        # fields. If any field is not present, it is set to 0.
        for item in all_items_data["items"]:
            if "shadowpay_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["shadowpay_price"] = 0
            if "waxpeer_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["waxpeer_price"] = 0
            if "csgo_market_price" not in all_items_data["items"][item].keys():
                all_items_data["items"][item]["csgo_market_price"] = 0

        # Update the status to "success"
        all_items_data["status"] = "success"
        return all_items_data

    # Handle any exceptions and return the error as status
    except BaseException as error:
        all_items_data["status"] = error
        return all_items_data

