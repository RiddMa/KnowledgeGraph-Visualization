import json
import re
from datetime import datetime
import ray

from db import MyNeo
from logger_factory import mylogger_p

limit = 1


@ray.remote
def init_vuln_ray():
    from db import MyMongo
    from datetime import datetime
    from logger_factory import mylogger
    from vuln_kg.vulnentity import \
        Vulnerability, ApiVersion, split_properties
    global limit

    start = datetime.now()
    mylogger_p('timer').info('Start init_vuln')

    mg = MyMongo()
    cursor = mg.get_nvd()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger_p('init_kg').debug(doc)
        try:
            props = split_properties(doc, api_ver=ApiVersion.NVDv1)
            vuln = Vulnerability(props["vuln_props"])
        except BaseException as e:
            mylogger('init_kg').error(e)

    mg.client.close()
    mylogger_p('timer').info(f'init_vuln with limit {limit} runtime = {datetime.now() - start}')
    return 0


@ray.remote
def init_asset_ray():
    from db import MyMongo
    from datetime import datetime
    from logger_factory import mylogger
    from vuln_kg.vulnentity import Asset
    global limit

    start = datetime.now()
    mylogger_p('timer').info('Start init_asset')

    mg = MyMongo()
    cursor = mg.get_cpe()
    for doc in cursor.limit(limit):
        mylogger_p('init_kg').debug(doc)
        try:
            asset = Asset(doc)
        except BaseException as e:
            mylogger('init_kg').error(e)
    mg.client.close()
    mylogger_p('timer').info(f'init_asset with limit {limit} runtime = {datetime.now() - start}')
    return 0


@ray.remote
def init_exploit_ray():
    from db import MyMongo
    from datetime import datetime
    from logger_factory import mylogger
    from vuln_kg.vulnentity import Exploit
    global limit

    start = datetime.now()
    mylogger_p('timer').info('Start init_exploit')

    mg = MyMongo()
    cursor = mg.get_edb()
    for doc in cursor.limit(limit):
        doc = doc['content']
        mylogger_p('init_kg').debug(doc)
        try:
            exploit = Exploit(doc)
        except BaseException as e:
            mylogger('init_kg').error(e)

    mg.client.close()
    mylogger_p('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')
    return 0


@ray.remote
def create_rel_va_ray():
    """
    Create Asset-HAS->Vuln and Vuln-AFFECTS->Asset relationship.

    :return:
    """
    start = datetime.now()

    from py2neo import NodeMatcher
    from db import MyNeo
    global limit
    neo = MyNeo()
    cursor = NodeMatcher(neo.graph).match("Vulnerability").limit(limit)
    for vuln_node in cursor:
        props = json.loads(vuln_node['props'])
        for op_dict in props['assets']:
            if op_dict['operator'] == 'OR':
                for match in op_dict['cpe_match']:
                    if match['vulnerable']:
                        asset_node = neo.get_node('Asset', cpe23uri=match['cpe23Uri']).first()
                        if asset_node is not None:
                            neo.add_relationship(start=asset_node, type_='Has', end=vuln_node)
                            neo.add_relationship(start=vuln_node, type_='Affects', end=asset_node)
    neo.close_db()
    mylogger_p('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')
    return 0


def create_rel_va():
    from py2neo import NodeMatcher
    from db import MyNeo
    global limit
    start = datetime.now()
    neo = MyNeo()
    cursor = NodeMatcher(neo.graph).match("Vulnerability").limit(limit)
    # cursor = NodeMatcher(neo.graph).match("Vulnerability")
    for vuln_node in cursor:
        cnt = 0
        props = json.loads(vuln_node['props'])
        for op_dict in props['assets']:
            if op_dict['operator'] == 'OR':
                for match in op_dict['cpe_match']:
                    if match['vulnerable']:
                        # asset_node = neo.get_node('Asset', cpe23uri=match['cpe23Uri']).first()
                        pattern = re.sub(r'\*+', '.*', match['cpe23Uri'])
                        # asset_node = neo.get_node('Asset').where(f"_.cpe23uri =~ {pattern}")
                        # asset_node = neo.match_asset(pattern)
                        # if asset_node is not None:
                        #     cnt += neo.add_relationship_cql(start=asset_node, type_='Has', end=vuln_node)
                        #     cnt += neo.add_relationship_cql(start=vuln_node, type_='Affects', end=asset_node)
                        assets = neo.match_asset(pattern)
                        for asset in assets:
                            cnt += neo.add_rel_cql_va(cve_id=vuln_node['cve_id'], cpe23uri=asset['cpe23uri'])
        mylogger_p('init_kg').info(f'Created {cnt} relationships for {vuln_node["cve_id"]}')
    neo.close_db()
    mylogger_p('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')
    return 0


@ray.remote
def create_rel_eva_ray():
    """
    Create Exploit-Exploits->Vuln and Vuln-Exploited_by->Exploit,
    then Deduct Exploit-Against->Asset and Asset-Exploited_by->Exploit

    :return:
    """

    from db import MyNeo
    from py2neo import NodeMatcher, RelationshipMatcher
    global limit
    start = datetime.now()
    mylogger_p('timer').info('Start create_rel_ve')

    neo = MyNeo()
    cursor = NodeMatcher(neo.graph).match("Exploit").limit(limit)
    for exploit_node in cursor:
        cve_ids = exploit_node['cve_ids']
        for cve_id_no in cve_ids:
            cve_id = f'CVE-{cve_id_no}'
            vuln_node = neo.get_node('Vulnerability', cve_id=cve_id).first()
            if vuln_node is not None:
                neo.add_relationship(start=exploit_node, type_='Exploits', end=vuln_node)
                neo.add_relationship(start=vuln_node, type_='Exploited_by', end=exploit_node)
                RelationshipMatcher(neo.graph).match([vuln_node], r_type='Affects')
    neo.close_db()
    mylogger_p('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')


def create_rel_eva():
    """
    Create Exploit-Exploits->Vuln and Vuln-Exploited_by->Exploit,
    then Deduct Exploit-Against->Asset and Asset-Exploited_by->Exploit

    :return:
    """

    from db import MyNeo
    from py2neo import NodeMatcher, RelationshipMatcher
    global limit
    start = datetime.now()
    mylogger_p('timer').info('Start create_rel_ve')

    neo = MyNeo()
    cursor = NodeMatcher(neo.graph).match("Exploit").limit(limit)
    rel_matcher = RelationshipMatcher(neo.graph)
    for exploit_node in cursor:
        cve_ids = exploit_node['cve_ids']
        for cve_id_no in cve_ids:
            cve_id = f'CVE-{cve_id_no}'
            vuln_node = neo.get_node('Vulnerability', cve_id=cve_id).first()
            if vuln_node is not None:
                neo.add_relationship(start=exploit_node, type_='Exploits', end=vuln_node)
                neo.add_relationship(start=vuln_node, type_='Exploited_by', end=exploit_node)
                for rel in rel_matcher.match([vuln_node], r_type='Affects'):
                    pass
    neo.close_db()
    mylogger_p('timer').info(f'init_exploit with limit {limit} runtime = {datetime.now() - start}')


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


def init_nodes():
    node_start_time = datetime.now()
    mylogger_p('init_kg').info('Start Node init')

    vuln_id = init_vuln_ray.remote()
    asset_id = init_asset_ray.remote()
    exploit_id = init_exploit_ray.remote()
    ray.get([vuln_id, asset_id, exploit_id])

    mylogger_p('init_kg').info('Finished Node init')
    mylogger_p('timer').info(
        f'ray.get([vuln_id, asset_id, exploit_id]) with limit {limit} runtime = {datetime.now() - node_start_time}')

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


def get_node_stats():
    _neo = MyNeo()
    neo_stat = {
        "Vuln": _neo.session.run('match (n:Vulnerability) return count(n)').data()[0]['count(n)'],
        "Asset": {
            "Total": _neo.session.run('match (n:Asset) return count(n)').data()[0]['count(n)'],
            "Application": _neo.session.run('match (n:Application) return count(n)').data()[0]['count(n)'],
            "OS": _neo.session.run('match (n:OperatingSystem) return count(n)').data()[0]['count(n)'],
            "Hardware": _neo.session.run('match (n:Hardware) return count(n)').data()[0]['count(n)'],
        },
        "Exploit": _neo.session.run('match (n:Exploit) return count(n)').data()[0]['count(n)'],
    }
    _neo.close_db()
    return neo_stat


def init_rels():
    rel_start_time = datetime.now()
    mylogger_p('init_kg').info('Start Relationship init')

    rel_va = create_rel_va_ray.remote()
    rel_eva = create_rel_eva_ray.remote()
    ray.get([rel_va, rel_eva])

    mylogger_p('init_kg').info('Finished Node init')
    mylogger_p('timer').info(
        f'ray.get([vuln_id, asset_id, exploit_id]) with limit {limit} runtime = {datetime.now() - rel_start_time}')


if __name__ == "__main__":
    global_start = datetime.now()
    mylogger_p('timer').info('Start init')

    n = MyNeo()
    n.create_node_index()
    n.create_rel_index()
    mylogger_p('db').info('Checked index, good to go')

    # ray.init()
    # init_nodes()
    mylogger_p('init_kg').info(f"Neo4j stat:\n{get_node_stats()}")

    # init_rels()
    create_rel_va()
    # create_rel_eva()

    mylogger_p('timer').info(f'Runtime = {datetime.now() - global_start}')
    n.close_db()
