import logging

import pymongo
from bs4 import BeautifulSoup


class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        if 'cve_bot' not in self.client.list_database_names():
            logging.info('cve_bot db does not exist. Insert content to create.')
        self.db = self.client['cve_bot']
        self.html = self.db['html']
        self.json = self.db['json']

    def save_html(self, cve_id, content):
        doc = {
            'cve_id': cve_id,
            'content': content
        }
        # doc_id = self.html.insert_one(doc).inserted_id
        self.html.update_one({'cve_id': cve_id}, {"$set": doc}, upsert=True)
        logging.info(cve_id + '.html saved to MongoDB.')

    def save_json(self, cve_id, content):
        doc = {
            'cve_id': cve_id,
            'content': content
        }
        # doc_id = self.json.insert_one(doc).inserted_id
        self.json.update_one({'cve_id': cve_id}, {"$set": doc}, upsert=True)
        logging.info(cve_id + '.json saved to MongoDB.')

    def get_html(self, cve_id) -> str:
        content = self.html.find_one({'cve_id': cve_id})['content']
        return content


MongoInstance = Mongo()

if __name__ == "__main__":
    tmp_doc = MongoInstance.get_html('CVE-2011-0001')
    soup = BeautifulSoup(tmp_doc, 'html.parser')
