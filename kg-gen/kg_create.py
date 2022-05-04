import pprint

from utils.db import mg

from vulnentity import Vulnerability, Asset, Exploit, split_properties, VulnEntity

if __name__ == "__main__":
    docs = mg.get_all_cve()
    for doc in docs.limit(1):
        # pprint.pprint(doc['content'])
        cve_item = doc["content"]
        props = split_properties(cve_item)
        vuln = Vulnerability(props["vuln_props"])
        vuln.add_node()
        attack = Exploit(props["attack_props"])
        attack.add_node()
        asset_props = props["asset_props"]
        assets = []
        for prop in asset_props:
            a = Asset(prop)
            a.add_node()
            assets.append(a)
        vuln_entity = VulnEntity(vuln, attack, assets)
        vuln_entity.add_relationship()
        print("1")
