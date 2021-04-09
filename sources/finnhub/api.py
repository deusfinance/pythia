import requests
import time
import os


def get_stock_candle(symbol, ts1, ts2):
    r = requests.get("https://finnhub.io/api/v1/stock/candle?symbol=%s&resolution=1&from=%s&to=%s&token=%s" % (symbol, ts1, ts2, os.getenv('FINNHUB_API_KEY')))
    return r.json()


def get_quote(symbol):
    r = requests.get("https://finnhub.io/api/v1/quote?symbol=%s&token=%s" % (symbol, os.getenv('FINNHUB_API_KEY')))
    return r.json()


def get_price_target(symbol):
    r = requests.get("https://finnhub.io/api/v1/stock/price-target?symbol=%s&token=%s" % (symbol, os.getenv('FINNHUB_API_KEY')))
    return r.json()


# https://finnhub.io/docs/api/price-target
def get_stock_price(symbol, timestamp=None):
    if timestamp is None:
        result = get_quote(symbol)
        if 'c' in result and result['c'] > 0:
            return {
                "symbol": symbol,
                # "price": result['targetMean'],
                "price": result['c'],
                "timestamp": result['t'],
            }
        else:
            print('api failed', result)
            return None
    else:
        result = get_stock_candle(symbol, timestamp-1200, timestamp)
        if result['s'] == "ok" and result['l']:
            n = len(result['l']) - 1
            return {
                "symbol": symbol,
                "price": result['c'][n],
                "timestamp": result['t'][n],
            }
        else:
            print('api failed', result)
            return None
