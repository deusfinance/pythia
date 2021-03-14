import redis, os, json, sys


r = redis.StrictRedis(host=os.getenv("REDIS_HOST"), decode_responses=True)


def set_symbol_price(symbol, info):
    r.set("symbol-price-%s" % symbol.upper(), json.dumps(info), 30)


def get_symbol_price(symbol):
    return {
        "price": 123.85,
        "timestamp": 1615724746
    }
    # try:
    #     price = r.get("symbol-price-%s" % symbol.upper())
    #     if not price:
    #         return None
    #     price = json.loads(price)
    #     return price
    # except ValueError:
    #     print("Oops!", sys.exc_info()[0], "occurred.")
    #     return None
