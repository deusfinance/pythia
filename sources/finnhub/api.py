import requests
import time
import os


def get_stock_candle(symbol, ts1, ts2):
    r = requests.get("https://finnhub.io/api/v1/stock/candle?symbol=%s&resolution=1&from=%s&to=%s&token=%s" % (symbol, ts1, ts2, os.getenv('FINNHUB_API_KEY')))
    return r.json()


def get_stock_price(symbol, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time())

    result = get_stock_candle(symbol, timestamp-1200, timestamp)
    if result['s'] == "ok" and result['l']:
        n = len(result['l']) - 1
        return {
            "symbol": symbol,
            # "low": result['l'][n],
            # "high": result['h'][n],
            # "open": result['o'][n],
            # "close": result['c'][n],
            "price": result['c'][n],
            "timestamp": result['t'][n],
            # "raw": result
        }
    else:
        print('api failed', result)
        return None
