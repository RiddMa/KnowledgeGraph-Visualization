import pprint

from utils.db import Mongo
from py2neo import Node, Relationship, Graph
import secret

if __name__ == "__main__":
    docs = Mongo.get_all_cve()
    for doc in docs.limit(1):
        pprint.pprint(doc['content'])
        cve_item = doc['content']
        cve_id = cve_item['']
