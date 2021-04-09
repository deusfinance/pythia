from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os
import redis
import json
from utils import mongo, crypto
import sources
from env import load_env
load_env()

#TODO: Reza: move to config
# REDIS_HOST = "localhost"
# REDIS_QUEUE = "pythia"

app = Flask(__name__)
app.secret_key = "ghgdghfhgfdfsdaxcxzczdb"
app.redis_client = redis.Redis(host=os.getenv("REDIS_HOST"))
app.redis_queue = os.getenv("REDIS_QUEUE")
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def indx():
    return jsonify({
        "success": True,
        "msg": "Pythia API v1",
    })

db = mongo.DB()

@app.route('/api/v1/request', methods=['GET', 'POST'])
def request_handler():
    #TODO:
    """
    1- get json data from request
    2- save in mongo
    """
    symbol = request.args.get('symbol').upper()
    source = request.args.get('source', default='finnhub')
    print("new request for symbol: %s from source: %s" % (symbol, source))

    started_at = int(time.time() * 1000)
    confirmed_at= None

    [current_price, error] = sources.get_symbol_price(symbol, source)
    if error:
        return jsonify({
            "success": False,
            "message": error
        })

    if not current_price:
        return jsonify({
            "success": False,
            "symbol": symbol,
            "message": "Not found"
        })

    new_request = {
        "symbol": symbol,
        "price": current_price['price'],
        "timestamp": current_price['timestamp'],
        "owner": os.getenv("NODE_WALLET_ADDRESS"),
        "source": source,
        "rawPrice": current_price,
        "started_at": started_at,
    }
    request_id = db.insert_dic(new_request, 'requests')

    sign_timestamp = int(time.time())
    message_to_sign = json.dumps({
        "id": str(request_id),
        "timestamp": sign_timestamp,
        "price": current_price['price']
    })
    signature = crypto.sign(os.getenv("NODE_WALLET_PRIVATE_KEY"), message_to_sign)

    db.insert_dic({
        'request': request_id,
        "price": current_price['price'],
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

    seconds_to_check = 0
    confirmed = False
    all_signatures = []
    signers = set()
    while seconds_to_check < 5:
        time.sleep(0.25)
        all_signatures = db['signatures'].find({'request': request_id})
        all_signatures = list(all_signatures)
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
            confirmed_at = int(time.time() * 1000)
            db["requests"].update_one({"_id": request_id}, {"$set": {"confirmed_at": confirmed_at}})
            break
        seconds_to_check += 0.25


    return jsonify({
        "success": confirmed,
        "symbol": symbol,
        "price": current_price['price'],
        # "candle": current_price,
        "creator": os.getenv("NODE_WALLET_ADDRESS"),
        "signatures": [{
            "owner": s['owner'],
            "timestamp": s['timestamp'],
            "price": s['price'],
            "signature": s['signature'],
        } for s in all_signatures if s['owner'] in signers],
        "started_at": started_at,
        "confirmed_at": confirmed_at
        # "signers": [s for s in signers]
    })


if __name__ == "__main__":
    app.run(host=os.getenv('GATEWAY_HOST', '0.0.0.0'), port=os.getenv('GATEWAY_PORT', 8000), debug=True)
