import pprint

from utils.db import Mongo
from py2neo import Node, Relationship, Graph
import secret
from vulnentity import Vulnerability, Asset, Attack

if __name__ == "__main__":
    docs = Mongo.get_all_cve()
    for doc in docs.limit(1):
    # pprint.pprint(doc['content'])
    cve_item = doc["content"]
    vuln = Vulnerability(
        cve_item["cve_id"],
        cve_item["vuln_desc"],
        cve_item["publish_date"],
        cve_item["last_update_date"],
        cve_item["cvss_score"],
        cve_item["cvss_severity"],
        cve_item["vulnerability_types"],
        cve_item["access_complexity"],
        cve_item["authentication"],
        cve_item["availability_impact"],
        cve_item["confidentiality_impact"],
        cve_item["gained_access"],
        cve_item["integrity_impact"],
        cve_item["references"],
    )
    attack = Attack(cve_item["cwe_id"])
    assets = []
    for product in cve_item["affected_products"]:
        asset = Asset(product["type"], product["vendor"], product["name"], product["version"])
        assets.append(asset)
    print("11")
