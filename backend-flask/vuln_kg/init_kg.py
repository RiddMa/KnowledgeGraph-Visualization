from pprint import pprint

from db import mg

from vulnentity import Vulnerability, Asset, Exploit, split_properties, VulnEntity, ApiVersion


def init_vuln():
    cursor = mg.get_nvd()
    for doc in cursor.limit(3):
        doc = doc['content']
        pprint(doc)
        props = split_properties(doc, api_ver=ApiVersion.NVDv1)
        vuln = Vulnerability(props["vuln_props"])
        # asset = Asset(props['asset_props'])
        # exploit = Exploit(props["exploit_props"])


if __name__ == "__main__":
    # docs = mg.get_all_cve()
    # for doc in docs.limit(1):
    #     # pprint(doc['content'])
    #     cve_item = doc["content"]
    #     props = split_properties(cve_item)
    #     vuln = Vulnerability(props["vuln_props"])
    #     vuln.add_node()
    #     attack = Exploit(props["attack_props"])
    #     attack.add_node()
    #     asset_props = props["asset_props"]
    #     assets = []
    #     for prop in asset_props:
    #         a = Asset(prop)
    #         a.add_node()
    #         assets.append(a)
    #     vuln_entity = VulnEntity(vuln, attack, assets)
    #     vuln_entity.add_relationship()
    #     print("1")
    init_vuln()
