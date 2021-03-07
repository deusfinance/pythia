import json
import os
import time
from bson.objectid import ObjectId
from utils import finnhub, mongo, crypto

"""
Processes a message that is coming into the node.
The format is like this:

{
	type: 'new_request',
	id: 'mongo_id'
}
This function should:
1- load the doc from db
2- sign or reject it if there is not enough signatures yet
"""


def process_message(msg):
	print("node_util.process_message", os.getenv("NODE_WALLET_ADDRESS"), type(msg), msg)
	data = json.loads(msg)
	if data['type'] == 'new_request':
		mongo_id = data.get('id')
		db = mongo.DB()
		request = db['requests'].find_one({'_id': ObjectId(mongo_id)})
		if request:
			old_signatures = db['signatures'].find({'request': ObjectId(mongo_id)})

			signers = set()
			for sig in old_signatures:
				if sig['owner'] == os.getenv("NODE_WALLET_ADDRESS"):
					return
				message_to_recover = json.dumps({
					"id": mongo_id,
					"timestamp": sig['timestamp'],
					"price": sig['price'],
				})
				sig_owner = crypto.recover(message_to_recover, sig['signature'])
				if sig_owner != sig['owner']:
					continue
				signers.add(sig_owner)
				if len(signers) >= int(os.getenv("NUM_SIGN_TO_CONFIRM")):
					return

			price = finnhub.get_stock_price(request['symbol'], request['timestamp'])

			# calculate difference of request price and node estimated price
			price_diff = abs(price['close'] - request['price'])

			# check price tolerance
			if price_diff/request['price'] < float(os.getenv("PRICE_TOLERANCE")):
				sign_timestamp = int(time.time())
				message_to_sign = json.dumps({
					"id": str(mongo_id),
					"timestamp": sign_timestamp,
					"price": price['close'],
				})
				signature = crypto.sign(os.getenv("NODE_WALLET_PRIVATE_KEY"), message_to_sign)
				db.insert_dic({
					'request': ObjectId(mongo_id),
					"price": price['close'],
					"timestamp": sign_timestamp,
					"owner": os.getenv("NODE_WALLET_ADDRESS"),
					"signature": signature
				}, 'signatures')
			else:
				print("Reject signing of request %s with price %s. estimated price: %s" % (mongo_id, request['price'], price['close']))

