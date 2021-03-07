import requests
import time
# API_KEY = "c0tfl4n48v6r4maeqn40"
API_KEY = "sandbox_c0tfl4n48v6r4maeqn4g"


def get_stock_candle(symbol, ts1, ts2):
    r = requests.get("https://finnhub.io/api/v1/stock/candle?symbol=%s&resolution=1&from=%s&to=%s&token=%s" % (symbol, ts1, ts2, API_KEY))
    return r.json()


def get_stock_price(symbol, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time())

    result = get_stock_candle(symbol, timestamp-120, timestamp)
    if result['s'] == "ok" and result['l']:
        n = len(result['l']) - 1
        return {
            "symbol": symbol,
            "low": result['l'][n],
            "high": result['h'][n],
            "open": result['o'][n],
            "close": result['c'][n],
            "timestamp": result['t'][n],
            # "raw": result
        }
    else:
        return None
