import logging
import pymongo


class MG:
    def __init__(self):
    self.client = pymongo.MongoClient("mongodb://localhost:27017/")
    if "cve_bot" not in self.client.list_database_names():
        logging.info('Database "cve_bot" does not exist.')
    self.db = self.client["cve_bot"]
    self.json = self.db["json"]

    def save_json(self, cve_id, content):
        doc = {"cve_id": cve_id, "content": content}
        # doc_id = self.json.insert_one(doc).inserted_id
        self.json.update_one({"cve_id": cve_id}, {"$set": doc}, upsert=True)
        logging.info(cve_id + ".json saved to MongoDB.")

    def get_all_cve(self) -> object:
        cursor = self.json.find({}, {"content": 1, "_id": 0})
        return cursor


Mongo = MG()
