from pymongo import MongoClient
import pymongo
import os

mongo_client = {}

class DB:
    def __init__(self, url=None):
        url = url or os.getenv("MONGODB_URL")
        global mongo_client
        if mongo_client.get(url) is None:
            mongo_client[url] = MongoClient(url)

        self.db = mongo_client[url][os.getenv("MONGODB_DB")]
        
    def query(self, table, conds):
        return self.db[table].find(conds)

    def insert_dic(self, d, table_name, upsert=False, cond={}):
        try:
            return self.db[table_name].insert(d)
        except pymongo.errors.DuplicateKeyError:
            if upsert:
                doc = self.db[table_name].find_one(cond)
                if doc:
                    if "_id" in d:
                        del d['_id']
                self.db[table_name].update_one({
                    "_id": doc['_id']
                }, {"$set": d})

    def update_dic(self, table_name, d, cond, cond_val, multi=True):
        if multi:
            self.db[table_name].update({cond: cond_val}, {"$set":d}, multi=multi)
        else:
            self.db[table_name].update_one({cond: cond_val}, {"$set":d})

    def __getitem__(self, i):
        return self.db[i]
