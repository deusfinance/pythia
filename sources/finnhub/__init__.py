from . import api, price_cache, websocket


def get_symbol_price(symbol, timestamp):
    current_price = price_cache.get_symbol_price(symbol)
    if not current_price:
        print('price not exit in redis. load from api')
        current_price = api.get_stock_price(symbol, timestamp)
        print('price from api:', current_price)
    return current_price
