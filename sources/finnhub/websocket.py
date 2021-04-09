#https://pypi.org/project/websocket_client/
import websocket, threading, json, os, time
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
            print("finnhub ws: %s - [%s]" % (message, time.ctime()))
    except ValueError:
        print("Unknown response", message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("============== finnhub trade socket subscription closed ==============")
    time.sleep(10)
    print("============== finnhub trade socket subscription retry ==============")
    start()


def on_open(ws):
    print("============== finnhub trade socket subscription start ==============")
    symbols_to_subscribe = os.getenv('FINNHUB_SUBSCRIBE_SYMBOLS', "TSLA").split(';')
    for symbol in symbols_to_subscribe:
        # print('>>>>>>>>>> subscribing to symbol: %s' % symbol)
        ws.send('{"type":"subscribe","symbol":"%s"}' % symbol)


def start():
    print('============== Finnhub Websocket Start ==============')
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://ws.finnhub.io?token=%s" % os.getenv("FINNHUB_API_KEY"),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.on_open = on_open

    ws_thread = threading.Thread(target=ws.run_forever)
    # ws_thread.daemon = True
    ws_thread.start()


if __name__ == "__main__":
    start()
