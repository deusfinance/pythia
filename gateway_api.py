from flask import Flask, request, jsonify, redirect
import traceback
import sys
import random
import time
from flask import session
from flask import send_from_directory
import os
import shutil
import datetime
import redis
import json
from utils import finnhub, mongo, crypto
from env import load_env
load_env()

#TODO: Reza: move to config
# REDIS_HOST = "localhost"
# REDIS_QUEUE = "pythia"

app = Flask(__name__)
app.secret_key = "ghgdghfhgfdfsdaxcxzczdb"
app.redis_client = redis.Redis(host=os.getenv("REDIS_HOST"))
app.redis_queue = os.getenv("REDIS_QUEUE")

@app.route('/', methods=['GET', 'POST'])
def indx():
    return jsonify({
        "success": True,
        "msg": "Pythia API v1",
    })


@app.route('/api/v1/request', methods=['GET', 'POST'])
def request_handler():
    #TODO:
    """
    1- get json data from request
    2- save in mongo
    """
    symbol = request.args.get('symbol')
    current_price = finnhub.get_stock_price(symbol)

    db = mongo.DB()
    new_request = {
        "symbol": symbol,
        "price": current_price['close'],
        "timestamp": current_price['timestamp'],
        "owner": os.getenv("NODE_WALLET_ADDRESS"),
        "rawPrice": current_price,
    }
    request_id = db.insert_dic(new_request, 'requests')

    sign_timestamp = int(time.time())
    message_to_sign = json.dumps({
        "id": str(request_id),
        "timestamp": sign_timestamp,
        "price": current_price['close']
    })
    signature = crypto.sign(os.getenv("NODE_WALLET_PRIVATE_KEY"), message_to_sign)

    db.insert_dic({
        'request': request_id,
        "price": current_price['close'],
        "timestamp": sign_timestamp,
        "owner": os.getenv("NODE_WALLET_ADDRESS"),
        "signature": signature
    }, 'signatures')

    """
    3- publish a json message on redis(network)
    a = {
        type: 'new_request',
        id: 'mongo_id'
    }
    s = json.dumps(a)
    app.redis_client.lpush(app.redis_queue, s)
    """
    redis_message = {
        "type": 'new_request',
        "id": str(request_id),
    }
    app.redis_client.lpush(app.redis_queue, json.dumps(redis_message))
    """
    4- check the request on mongo periodically and
    send the response when data is ready
    """

    minutes_to_check = 0
    confirmed = False
    while minutes_to_check < 120:
        time.sleep(1)
        all_signatures = db['signatures'].find({'request': request_id})
        signers = set()
        for sig in all_signatures:
            message_to_recover = json.dumps({
                "id": str(request_id),
                "timestamp": sig['timestamp'],
                "price": sig['price'],
            })
            sig_owner = crypto.recover(message_to_recover, sig['signature'])
            if sig_owner != sig['owner']:
                continue
            signers.add(sig_owner)
        if len(signers) >= int(os.getenv("NUM_SIGN_TO_CONFIRM")):
            confirmed = True
            break
        minutes_to_check += 1

    return jsonify({
        "success": confirmed,
        "symbol": symbol,
        "price": current_price['close'],
        # "candle": current_price,
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
