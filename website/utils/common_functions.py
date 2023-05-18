def price_beautify(item_price, slice_len):
    item_price_str = str(item_price)
    item_price_len = len(item_price_str)
    item_price_converted = f"{str(item_price_str)[:(item_price_len - slice_len)]}." + \
                           f"{item_price_str[item_price_len - slice_len:]}"
    return float(item_price_converted).__round__(2)
