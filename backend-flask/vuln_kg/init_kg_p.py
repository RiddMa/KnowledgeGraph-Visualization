import json
from datetime import datetime
import ray
from logger_factory import mylogger, mylogger_p

limit = 0


# def init_asset():
#     start = datetime.now()
#     mylogger('timer').info('Start init_asset')
#
#     cursor = MyMongo().get_cpe()
#     for doc in cursor.limit(limit):
#         mylogger('init_kg').debug(doc)
#         asset = Asset(doc)
#
#     mylogger('timer').info(f'init_asset with limit {limit} runtime = {datetime.now() - start}')
#     return 0
@ray.remote
def init_vuln_ray():
    from db import MyMongo
    from datetime import datetime
    from logger_factory import mylogger
    from vuln_kg.vulnentity import Vulnerability, ApiVersion, split_properties

    start = datetime.now()
    mylogger_p('timer').info('Start init_vuln')

    mg = MyMongo()
    cursor = mg.get_nvd()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger_p('init_kg').debug(doc)
        props = split_properties(doc, api_ver=ApiVersion.NVDv1)
        vuln = Vulnerability(props["vuln_props"])
    mg.client.close()
    mylogger_p('timer').info(f'init_vuln with limit {limit} runtime = {datetime.now() - start}')
    return 0


@ray.remote
def init_asset_ray():
    from db import MyMongo
    from datetime import datetime
    from logger_factory import mylogger
    from vuln_kg.vulnentity import Asset

    start = datetime.now()
    mylogger_p('timer').info('Start init_asset')

    mg = MyMongo()
    cursor = mg.get_cpe()
    for doc in cursor.limit(limit):
        mylogger_p('init_kg').debug(doc)
        asset = Asset(doc)
    mg.client.close()
    mylogger_p('timer').info(f'init_asset with limit {limit} runtime = {datetime.now() - start}')
    return 0


@ray.remote
def init_exploit_ray():
    from db import MyMongo
    from datetime import datetime
    from logger_factory import mylogger
    from vuln_kg.vulnentity import Exploit

    start = datetime.now()
    mylogger_p('timer').info('Start init_exploit')

    mg = MyMongo()
    cursor = mg.get_edb()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger_p('init_kg').debug(doc)
        exploit = Exploit(doc)
    mg.client.close()
    mylogger_p('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')
    return 0


@ray.remote
def create_rel_vuln():
    """
    Create Asset-HAS->Vuln and Vuln-AFFECTS->Asset relationship.

    :return:
    """
    start = datetime.now()

    from py2neo import NodeMatcher
    from db import MyNeo
    neo = MyNeo()
    cursor = NodeMatcher(neo.graph).match("Vulnerability").limit(10)
    for vuln_node in cursor:
        props = json.loads(vuln_node['props'])
        for op_dict in props['assets']:
            if op_dict['operator'] == 'OR':
                for match in op_dict['cpe_match']:
                    if match['vulnerable']:
                        asset_node = neo.get_node('Asset', cpe23uri=match['cpe23Uri']).first()
                        if asset_node is not None:
                            neo.add_relationship(start=asset_node, type_='Has', end=vuln_node, props=None)
                            neo.add_relationship(start=vuln_node, type_='Affects', end=asset_node, props=None)
    return 0


@ray.remote
def create_rel_ve():
    """
    Create Vuln->Exploit and Exploit-USE->Vuln

    :return:
    """

    from db import MyNeo
    from py2neo import NodeMatcher
    start = datetime.now()
    mylogger_p('timer').info('Start create_rel_ve')

    neo = MyNeo()
    cursor = NodeMatcher(neo.graph).match("Exploit").limit(10)
    for exploit_node in cursor:
        cve_ids = exploit_node['cve_ids']
        for cve_id_no in cve_ids:
            cve_id = f'CVE-{cve_id_no}'
            vuln_node = neo.get_node('Vulnerability', cve_id=cve_id).first()
            if vuln_node is not None:
                neo.add_relationship(start=exploit_node, type_='Exploits', end=vuln_node, props=None)
                neo.add_relationship(start=vuln_node, type_='Exploited_by', end=exploit_node, props=None)


def init_vuln_p():
    from db import MyMongo
    from vuln_kg.vulnentity import split_properties, Vulnerability, ApiVersion
    start = datetime.now()
    mylogger_p('timer').info('Start init_vuln')
    mg = MyMongo()
    cursor = mg.get_nvd()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger_p('init_kg').debug(doc)
        props = split_properties(doc, api_ver=ApiVersion.NVDv1)
        vuln = Vulnerability(props["vuln_props"])

    mylogger_p('timer').info(f'init_vuln with limit {limit} runtime = {datetime.now() - start}')
    return 0


def init_asset_p():
    from db import MyMongo
    from vuln_kg.vulnentity import Asset
    start = datetime.now()
    mylogger_p('timer').info('Start init_asset')
    mg = MyMongo()
    cursor = mg.get_cpe()
    for doc in cursor.limit(limit):
        mylogger_p('init_kg').debug(doc)
        asset = Asset(doc)

    mylogger_p('timer').info(f'init_asset with limit {limit} runtime = {datetime.now() - start}')
    return 0


def init_exploit_p():
    from db import MyMongo
    from vuln_kg.vulnentity import Exploit
    start = datetime.now()
    mylogger_p('timer').info('Start init_exploit')
    mg = MyMongo()
    cursor = mg.get_edb()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger_p('init_kg').debug(doc)

        exploit = Exploit(doc)
    mg.client.close()
    mylogger_p('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')
    return 0


if __name__ == "__main__":
    global_start = datetime.now()
    mylogger_p('timer').info('Start init')

    node_start_time = datetime.now()
    mylogger_p('init_kg').info('Start Node init')

    # from multiprocessing import Pool
    #
    # pool = Pool()
    # vuln_id = pool.apply_async(init_vuln_p)
    # asset_id = pool.apply_async(init_asset_p)
    # exploit_id = pool.apply_async(init_exploit_p)
    #
    # answer = [asset_id.get(), vuln_id.get(), exploit_id.get()]
    # mylogger_p('timer').info(answer)
    # mylogger_p('timer').info(f'Pool with limit {limit} runtime = {datetime.now() - global_start}')

    vuln_id = init_vuln_ray.remote()
    asset_id = init_asset_ray.remote()
    exploit_id = init_exploit_ray.remote()
    ray.get([vuln_id, asset_id, exploit_id])

    mylogger_p('init_kg').info('Finished Node init')

    mylogger_p('timer').info(
        f'ray.get([vuln_id, asset_id, exploit_id]) with limit {limit} runtime = {datetime.now() - node_start_time}')

    rel_start_time = datetime.now()
    mylogger_p('init_kg').info('Start Relationship init')

    rel_va = create_rel_vuln.remote()
    rel_ve = create_rel_
    ray.get([rel_va, ])

    mylogger_p('init_kg').info('Finished Node init')
    mylogger_p('timer').info(
        f'ray.get([vuln_id, asset_id, exploit_id]) with limit {limit} runtime = {datetime.now() - rel_start_time}')
