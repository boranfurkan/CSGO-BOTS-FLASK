from .google_sheet import GoogleSheet
from .empire import Empire
import asyncio
from ..sell_utils import Shadow, CsgoMarket


async def get_all_auction_data(csgo_empire_token, shadow_token, market_token, buff_rate):
    all_items_data = {
        "items": [],
        "ids": [],
        "status": ""
    }

    try:
        csgo_empire = Empire(csgo_empire_token=csgo_empire_token)
        current_auctions = asyncio.create_task(csgo_empire.get_auction_items())
        empire_market_data = asyncio.create_task(csgo_empire.get_market_items())

        sheet_data = GoogleSheet()
        steam_inventories = asyncio.create_task(sheet_data.get_steam_inventories())
        buff = asyncio.create_task(sheet_data.get_buff_items())

        shadowpay = Shadow(user_token=shadow_token, merchant_token="", discount=0)
        shadowpay_market_data = asyncio.create_task(shadowpay.get_items_volume())

        csgo_market = CsgoMarket(secret_key=market_token, discount=0)
        csgo_market_data = asyncio.create_task(csgo_market.get_items_volume())

        await asyncio.gather(current_auctions, empire_market_data, steam_inventories,
                             buff, shadowpay_market_data, csgo_market_data)

        current_auctions = current_auctions.result()
        empire_market_data = empire_market_data.result()
        steam_inventories = steam_inventories.result()
        shadowpay_market_data = shadowpay_market_data.result()
        csgo_market_data = csgo_market_data.result()
        buff = buff.result()

        for item, values in current_auctions.items():
            if item not in steam_inventories:
                if values["price"] > 40:
                    if item in buff:
                        item_image_url = values["url"]
                        item_id = values["id"]
                        auction_price = values["price"]
                        auction_ends = values["end_time"]

                        if item in empire_market_data:
                            market_price = empire_market_data[item]["price"]
                            if market_price < auction_price:
                                price = market_price
                                is_cheaper_in_market = True
                            else:
                                price = auction_price
                                is_cheaper_in_market = False
                        else:
                            price = auction_price
                            is_cheaper_in_market = False

                        """Buff Listing Check"""
                        buff_listing = buff[item]["listing"]
                        discount = (float(1 - (price * 0.614) / (buff_listing * buff_rate)) * 100).__round__(2)
                        if discount >= 4:
                            buff_buy_order = buff[item]["buy_order"]
                            if buff_buy_order != 0:
                                buy_order_discount = (float(
                                    1 - (price * 0.614) / (buff_buy_order * buff_rate)) * 100).__round__(2)
                            else:
                                buy_order_discount = "N/A"

                            if item in shadowpay_market_data:
                                shadowpay_cheapest_rate = float(shadowpay_market_data[item]["price"] /
                                                                buff[item]["listing7"]).__round__(2)

                                shadowpay_count = shadowpay_market_data[item]["count"]
                            else:
                                shadowpay_cheapest_rate = 0
                                shadowpay_count = 0

                            if item in csgo_market_data:
                                csgo_market_cheapest_rate = float(csgo_market_data[item]["price"] /
                                                                  buff[item]["listing7"]).__round__(2)

                                csgo_market_count = csgo_market_data[item]["count"]
                            else:
                                csgo_market_cheapest_rate = 0
                                csgo_market_count = 0

                            all_items_data["items"].append(
                                {"id": item_id,
                                 "name": item,
                                 "url": item_image_url,
                                 "auction_ends": auction_ends,
                                 "current_price": price,
                                 "is_cheaper_in_market": is_cheaper_in_market,
                                 "discount": discount,
                                 "buy_order_discount": buy_order_discount,
                                 "shadowpay_count": shadowpay_count,
                                 "shadowpay_cheapest_rate": shadowpay_cheapest_rate,
                                 "csgo_market_count": csgo_market_count,
                                 "csgo_market_cheapest_rate": csgo_market_cheapest_rate
                                 }
                            )
                            all_items_data["ids"].append(item_id)

            all_items_data["status"] = "success"
        return all_items_data, empire_market_data, steam_inventories, shadowpay_market_data, csgo_market_data, buff

    except Exception as error:
        all_items_data["status"] = {}
        all_items_data["data"] = "error"
        all_items_data["status"]["details"] = str(error)
        return all_items_data


def update_auction_data(token):
    try:
        csgo_empire = Empire(token)
        new_auctions = asyncio.run(csgo_empire.get_auction_items())
        return new_auctions, "success"

    except Exception as error:
        return str(error), "error"


async def buff_buy_data(csgo_empire_token, shadow_token, market_token, buff_buy_rate):
    all_items_data = {
        "items": {},
        "status": ""
    }

    try:
        csgo_empire = Empire(csgo_empire_token=csgo_empire_token)
        empire_market_data = asyncio.create_task(csgo_empire.get_market_items())

        sheet_data = GoogleSheet()
        steam_inventories = asyncio.create_task(sheet_data.get_steam_inventories())
        buff = asyncio.create_task(sheet_data.get_buff_items())
        item_histories = asyncio.create_task(sheet_data.get_item_histories())

        shadowpay = Shadow(user_token=shadow_token, merchant_token="", discount=0)
        shadowpay_market_data = asyncio.create_task(shadowpay.get_items_volume())

        csgo_market = CsgoMarket(secret_key=market_token, discount=0)
        csgo_market_data = asyncio.create_task(csgo_market.get_items_volume())

        await asyncio.gather(empire_market_data, steam_inventories, buff, item_histories,
                             shadowpay_market_data, csgo_market_data)

        empire_market_data = empire_market_data.result()
        steam_inventories = steam_inventories.result()
        buff = buff.result()
        item_histories = item_histories.result()
        shadowpay_market_data = shadowpay_market_data.result()
        csgo_market_data = csgo_market_data.result()

        for item, values in buff.items():
            if item not in steam_inventories:
                buff_listing = float(values["listing"]).__round__(2)
                if buff_listing != 0 and buff_listing != "0":
                    buff_buy_order = float(values["buy_order"]).__round__(2)
                    if item in item_histories:
                        suggested_price = float(item_histories[item]["average_14"]).__round__(2)
                        if suggested_price != 0 and suggested_price != "0":
                            discount = float(100 * (1 - (buff_listing * float(buff_buy_rate) / suggested_price))).__round__(2)

                            if item in shadowpay_market_data:
                                item_cheapest_shadowpay = shadowpay_market_data[item]["price"]
                                item_volume_shadowpay = shadowpay_market_data[item]["count"]
                            else:
                                item_cheapest_shadowpay = ""
                                item_volume_shadowpay = 0

                            if item in csgo_market_data:
                                item_cheapest_market = csgo_market_data[item]["price"]
                                item_volume_market = csgo_market_data[item]["count"]
                            else:
                                item_cheapest_market = ""
                                item_volume_market = 0

                            if item in empire_market_data:
                                if empire_market_data[item]["price"] * 0.61 < buff_listing:
                                    is_empire_cheaper = True
                                else:
                                    is_empire_cheaper = False

                                buff_rate = float(1 - (empire_market_data[item]["price"] * 0.615) /
                                                  (buff_listing * buff_buy_rate)).__round__(2)
                            else:
                                is_empire_cheaper = False
                                buff_rate = ""

                            all_items_data["items"][item] = {
                                "buff_listing": buff_listing,
                                "buff_buy_order": buff_buy_order,
                                "suggested_price": suggested_price,
                                "discount": discount,
                                "is_cheaper_empire": is_empire_cheaper,
                                "buff_rate": buff_rate,
                                "shadowpay_cheapest": item_cheapest_shadowpay,
                                "shadowpay_count": item_volume_shadowpay,
                                "market_cheapest": item_cheapest_market,
                                "market_count": item_volume_market,
                            }

        all_items_data["status"] = "success"
        return all_items_data

    except Exception as error:
        all_items_data["status"] = "error"
        all_items_data["details"] = str(error)
        return all_items_data
