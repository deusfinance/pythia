import os
import sys
from . import finnhub, test

current_dir = os.path.dirname(os.path.realpath(__file__))
# parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)


def init_services():
    finnhub.websocket.start()


def get_symbol_price(symbol, source, timestamp=None):
    if source in sys.modules[__name__].__dict__.keys():
        source_module = getattr(sys.modules[__name__], source)
        current_price = source_module.get_symbol_price(symbol, timestamp)
        return [current_price, None]
    else:
        return [None, "Unknown source module"]
