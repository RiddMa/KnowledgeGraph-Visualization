from pprint import pprint
from datetime import datetime
from db import mg
from logger_factory import mylogger

from vulnentity import Vulnerability, Asset, Exploit, split_properties, VulnEntity, ApiVersion

limit = 10000


def init_vuln():
    cursor = mg.get_nvd()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger('init_kg').debug(doc)
        props = split_properties(doc, api_ver=ApiVersion.NVDv1)
        vuln = Vulnerability(props["vuln_props"])
        # asset = Asset(props['asset_props'])
        # exploit = Exploit(props["exploit_props"])


def init_asset():
    cursor = mg.get_cpe()
    for doc in cursor.limit(limit):
        mylogger('init_kg').debug(doc)
        asset = Asset(doc)


def init_exploit():
    cursor = mg.get_edb()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger('init_kg').debug(doc)
        exploit = Exploit(doc)


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

    start = datetime.now()
    init_vuln()
    init_asset()
    init_exploit()
    mylogger('root').info(f'With limit {limit} runtime = {datetime.now() - start}')
