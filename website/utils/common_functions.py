def price_beautify(item_price, slice_len):
    # Convert the item price to a string
    item_price_str = str(item_price)
    # Get the length of the item price string
    item_price_len = len(item_price_str)
    # Convert the item price to a new format
    item_price_converted = f"{str(item_price_str)[:(item_price_len - slice_len)]}." + \
                           f"{item_price_str[item_price_len - slice_len:]}"
    # Return the converted price as a float, rounded to 2 decimal places
    return float(item_price_converted).__round__(2)
