import logging
import pymongo

from custom_logger import mylogger


class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        if 'cve_bot' not in self.client.list_database_names():
            logging.getLogger().info('cve_bot db does not exist. Insert content to create.')
        self.db = self.client['cve_bot']
        self.html = self.db['html']
        self.json = self.db['json']
        self.nvd_json_src = self.db['nvd_json_src']
        self.nvd_json = self.db['nvd_json']
        self.cxsecurity_index = self.db['cxsecurity_index']
        self.cxsecurity_html = self.db['cxsecurity_html']
        self.cxsecurity_json = self.db['cxsecurity_json']
        self.edb_html = self.db['edb_html']
        self.edb_json = self.db['edb_json']
        self.cpe = self.db['cpe']

    def save_cvedetails_html(self, cve_id, content):
        doc = {
            'cve_id': cve_id,
            'content': content
        }
        # doc_id = self.html.insert_one(doc).inserted_id
        self.html.update_one({'cve_id': cve_id}, {"$set": doc}, upsert=True)
        logging.getLogger('CveDetails').info(cve_id + '.html saved to MongoDB cvedetails_html')

    def get_cvedetails_html(self, cve_id) -> str:
        content = self.html.find_one({'cve_id': cve_id})['content']
        return content

    def save_cvedetails_json(self, cve_id, content):
        doc = {
            'cve_id': cve_id,
            'content': content
        }
        # doc_id = self.json.insert_one(doc).inserted_id
        self.json.update_one({'cve_id': cve_id}, {"$set": doc}, upsert=True)
        logging.getLogger('CveDetails').info(cve_id + '.json saved to MongoDB cvedetails_json')

    def save_nvd_json_src(self, cve_id, content):
        doc = {
            'cve_id': cve_id,
            'content': content
        }
        self.nvd_json_src.update_one({'cve_id': cve_id}, {"$set": doc}, upsert=True)
        logging.getLogger('Nvd').info(cve_id + '.json saved to MongoDB nvd_json_src')

    def get_nvd_json_src(self, cve_id=None):
        if cve_id is None:
            content = self.nvd_json_src.find()
        else:
            content = self.nvd_json_src.find_one({'cve_id': cve_id})['content']
        return content

    def save_nvd_json(self, cve_id, content):
        doc = {
            'cve_id': cve_id,
            'content': content
        }
        self.nvd_json.update_one({'cve_id': cve_id}, {"$set": doc}, upsert=True)
        logging.getLogger('Nvd').info(cve_id + '.json saved to MongoDB nvd_json')

    def get_nvd_json(self, cve_id=None):
        if cve_id is None:
            content = self.nvd_json.find()
        else:
            content = self.nvd_json.find_one({'cve_id': cve_id})
        return content

    def save_cxsecurity_index(self, exploit_id, content):
        doc = {
            'exploit_id': exploit_id,
            'content': content
        }
        self.cxsecurity_index.update_one({'exploit_id': exploit_id}, {"$set": doc}, upsert=True)
        logging.getLogger('CxSecurity').info(exploit_id + ' index saved to MongoDB cxsecurity_index')

    def save_cxsecurity_html(self, exploit_id, content):
        doc = {
            'exploit_id': exploit_id,
            'content': content
        }
        self.cxsecurity_html.update_one({'exploit_id': exploit_id}, {"$set": doc}, upsert=True)
        logging.getLogger('CxSecurity').info(exploit_id + '.html saved to MongoDB cxsecurity_html')

    def save_cxsecurity_json(self, exploit_id, content):
        doc = {
            'exploit_id': exploit_id,
            'content': content
        }
        self.cxsecurity_json.update_one({'exploit_id': exploit_id}, {"$set": doc}, upsert=True)
        logging.getLogger('CxSecurity').info(exploit_id + '.json saved to MongoDB cxsecurity_json')

    def save_edb_html(self, edb_id, content):
        doc = {
            'edb_id': edb_id,
            'content': content
        }
        self.edb_html.update_one({'edb_id': edb_id}, {"$set": doc}, upsert=True)
        logging.getLogger('edb').info(edb_id + '.html saved to MongoDB edb_html')

    def save_edb_json(self, edb_id, content):
        doc = {
            'edb_id': edb_id,
            'content': content
        }
        self.edb_json.update_one({'edb_id': edb_id}, {"$set": doc}, upsert=True)
        logging.getLogger('edb').info(edb_id + '.json saved to MongoDB edb_json')

    def get_edb_json(self, edb_id=None):
        if edb_id is None:
            content = self.edb_json.find()
        else:
            content = self.edb_json.find_one({'edb_id': edb_id})
        return content

    def save_cpe(self, cpe23uri, content):
        self.cpe.update_one({'cpe23uri': cpe23uri}, {"$set": content}, upsert=True)
        mylogger('cpe').info(cpe23uri + '.json saved to MongoDB cpe')


mg = Mongo()
