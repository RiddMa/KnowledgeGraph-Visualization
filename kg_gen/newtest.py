from utils.db import mongo

from vulnentity import Vulnerability, Asset, Attack, split_properties, VulnEntity

if __name__ == "__main__":
    docs = mongo.get_all_cve()
    for doc in docs.limit(1):
        # pprint.pprint(doc['content'])
        cve_item = doc["content"]
        props = split_properties(cve_item)
        vuln = Vulnerability(props["vuln_props"])
        attack = Attack(props["attack_props"])
        asset_props = props["asset_props"]
        assets = []
        for prop in asset_props:
            a = Asset(prop)
            tmp = a.get_node()
            assets.append(a)
        vuln_entity = VulnEntity(vuln, attack, assets)
        vuln_entity.add_relationship()
