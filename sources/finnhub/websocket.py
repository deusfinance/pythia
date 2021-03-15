#https://pypi.org/project/websocket_client/
import websocket, json, os
from . import price_cache


def on_trade_data(data):
    for trade in data:
        price = {
            "symbol": trade['s'].upper(),
            "price": trade['p'],
            "timestamp": int(trade['t'] / 1000)
        }
        # print(price)
        price_cache.set_symbol_price(trade['s'], price)


def on_message(ws, message):
    # print(message)
    try:
        message = json.loads(message)
        if message['type'] == 'trade':
            on_trade_data(message['data'])
        else:
            print(message)
    except ValueError:
        print("Unknown response", message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"TSLA"}')


def start():
    print('============== Finnhub Websocket Start ==============')
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        # "wss://ws.finnhub.io?token=c0v5f0v48v6pr2p75fmg",
        "wss://ws.finnhub.io?token=%s" % os.getenv("FINNHUB_API_KEY"),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    start()
