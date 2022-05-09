import json
from datetime import datetime

from py2neo import NodeMatcher, Relationship

from db import mg, neo
from logger_factory import mylogger

from vulnentity import Vulnerability, Asset, Exploit, split_properties, VulnEntity, ApiVersion

limit = 10000


def init_vuln():
    start = datetime.now()
    mylogger('timer').info('Start init_vuln')

    cursor = mg.get_nvd()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger('init_kg').debug(doc)
        props = split_properties(doc, api_ver=ApiVersion.NVDv1)
        vuln = Vulnerability(props["vuln_props"])

    mylogger('timer').info(f'init_vuln with limit {limit} runtime = {datetime.now() - start}')
    return 0


def init_asset():
    start = datetime.now()
    mylogger('timer').info('Start init_asset')

    cursor = mg.get_cpe()
    for doc in cursor.limit(limit):
        mylogger('init_kg').debug(doc)
        asset = Asset(doc)

    mylogger('timer').info(f'init_asset with limit {limit} runtime = {datetime.now() - start}')
    return 0


def init_exploit():
    start = datetime.now()
    mylogger('timer').info('Start init_exploit')

    cursor = mg.get_edb()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger('init_kg').debug(doc)
        exploit = Exploit(doc)

    mylogger('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')
    return 0


def create_rel_vuln():
    start = datetime.now()
    global limit
    cursor = NodeMatcher(neo.graph).match("Vulnerability").limit(limit)
    for vuln_node in cursor:
        props = json.loads(vuln_node['props'])
        for op_dict in props['assets']:
            if op_dict['operator'] == 'OR':
                for match in op_dict['cpe_match']:
                    if match['vulnerable']:
                        asset_node = neo.get_asset_node('Asset', cpe23uri=match['cpe23Uri']).first()
                        if asset_node is not None:
                            neo.add_relationship(start=asset_node, type_='HAS', end=vuln_node)
    return 0


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
    init_asset()
    init_exploit()
    create_rel_vuln()
