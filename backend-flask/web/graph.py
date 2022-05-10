import json
import time
from collections import OrderedDict
from pprint import pprint

from flask import Blueprint

from db import neo

bp = Blueprint('graph', __name__, url_prefix='/api/graph')


def assemble_graph_data(assets=(), vulns=(), exploits=(), rels=()):
    nodes, links = [], []

    asset_map = {d["eid"]: d for d in assets}
    nodes.extend([{
        "id": t[0],
        "name": t[1]["vendor"] + " " + t[1]["name"] + " " + t[1]["version"],
        "data": t[1],
        "type": "asset"
    } for t in asset_map.items()])

    vuln_map = {d["eid"]: d for d in vulns}
    nodes.extend([{
        "id": t[0],
        "name": t[1]["cve_id"],
        "data": t[1],
        "type": "vuln"
    } for t in vuln_map.items()])

    exploit_map = {d["eid"]: d for d in exploits}
    nodes.extend([{
        "id": t[0],
        "name": t[1]["vulnerability_types"],
        "data": t[1],
        "type": "exploit"
    } for t in exploit_map.items()])

    links = [{"source": l[0]["eid"], "target": l[2]["eid"], "name": l[1]} for l in rels]

    return {"nodes": nodes, "links": links}


@bp.route('/')
def retrieve_graph_stats():
    t0 = time.time()

    def work(tx):
        cql_vuln = "match (vul:Vulnerability) return count(vul) as vul_count"
        cql_atk = "match (e:Exploit) return count(e) as exploit_count"
        cql_app = "match (app:Application) return count(app) as app_count"
        cql_hw = "match (hardware:Hardware) return count(hardware) as hw_count"
        cql_os = "match (os:OperatingSystem) return count(os) as os_count"
        cql_app_family = "match (app:Application:Family) return count(app) as cnt"
        cql_hw_family = "match (hardware:Hardware:Family) return count(hardware) as cnt"
        cql_os_family = "match (os:OperatingSystem:Family) return count(os) as cnt"
        cql_affected_app = "match (n:Application)-[]->(af:Family) return count(n) as cnt"
        cql_affected_os = "match (n:OperatingSystem)-[]->(af:Family) return count(n) as cnt"
        cql_affected_hw = "match (n:Hardware)-[]->(af:Family) return count(n) as cnt"
        result = {"vul_count": tx.run(cql_vuln).data()[0]["vul_count"],
                  "exploit_count": tx.run(cql_atk).data()[0]["exploit_count"],
                  "app_count": tx.run(cql_app).data()[0]["app_count"],
                  "os_count": tx.run(cql_os).data()[0]["os_count"],
                  "hw_count": tx.run(cql_hw).data()[0]["hw_count"],
                  "app_family": tx.run(cql_app_family).data()[0]["cnt"],
                  "os_family": tx.run(cql_os_family).data()[0]["cnt"],
                  "hw_family": tx.run(cql_hw_family).data()[0]["cnt"],
                  'affected_app': tx.run(cql_affected_app).data()[0]["cnt"],
                  'affected_os': tx.run(cql_affected_os).data()[0]["cnt"],
                  'affected_hw': tx.run(cql_affected_hw).data()[0]["cnt"],
                  }
        result = {
            'vul': {
                'vul_count': tx.run(cql_vuln).data()[0]["vul_count"],
                'affected_asset': -1,
                'affected_app': tx.run(cql_affected_app).data()[0]["cnt"],
                'affected_os': tx.run(cql_affected_os).data()[0]["cnt"],
                'affected_hw': tx.run(cql_affected_hw).data()[0]["cnt"],
            },
            'asset': {
                'asset_count': -1,
                'family_cnt': -1,
                'app_family': tx.run(cql_app_family).data()[0]["cnt"],
                'app_count': tx.run(cql_app).data()[0]["app_count"],
                'os_family': tx.run(cql_os_family).data()[0]["cnt"],
                'os_count': tx.run(cql_os).data()[0]["os_count"],
                'hw_family': tx.run(cql_hw_family).data()[0]["cnt"],
                'hw_count': tx.run(cql_hw).data()[0]["hw_count"],
            },
            'exploit': {
                'exploit_count': tx.run(cql_atk).data()[0]["exploit_count"],
            },
        }
        result['vul']["affected_asset"] = result['vul']['affected_app'] + result['vul']['affected_os'] + result['vul'][
            'affected_hw']
        result['asset']["asset_count"] = result['asset']['app_count'] + result['asset']['os_count'] + result['asset'][
            'hw_count']
        result['asset']["family_cnt"] = result['asset']['app_family'] + result['asset']['os_family'] + result['asset'][
            'hw_family']
        return result

    res = neo.get_session().read_transaction(work)
    # res = neo.get_movie()
    print("time elapsed:" + str(time.time() - t0))
    return res


def label_to_id_field(label) -> str:
    """
    Convert label to id field of entity

    :param label:
    :return:
    """
    _converter = {
        'Vulnerability': 'cve_id',
        'Family': 'cpe23uri',
        'Asset': 'cpe23uri',
        'Application': 'cpe23uri',
        'OperatingSystem': 'cpe23uri',
        'Hardware': 'cpe23uri',
        'Exploit': 'edb_id',
    }
    return _converter[label]


def get_symbol_size(label):
    _symbol_size_map = {
        'Vulnerability': 30,
        'Family': 20,
        'Asset': 10,
        'Application': 10,
        'OperatingSystem': 10,
        'Hardware': 10,
        'Exploit': 30,
    }
    return _symbol_size_map[label]


vul_label_settings = {
    'show': True,
    'position': 'inside',
    'fontSize': 14,
    'overflow': 'break',
    'fontWeight': 'bold',
    'textBorderColor': 'inherit',
    'textBorderWidth': '2',
}

category_map = {
    'Vulnerability': {'name': '漏洞'},
    'Family': {'name': '家族'},
    'Asset': {'name': '资产'},
    'Application': {'name': '应用程序'},
    'OperatingSystem': {'name': '操作系统'},
    'Hardware': {'name': '硬件'},
    'Exploit': {'name': '利用'},
}


def get_node_category(type_list):
    if 'Family' in type_list:
        type_list = list(category_map.keys()).index('Family')
    elif 'Vulnerability' in type_list:
        type_list = list(category_map.keys()).index('Vulnerability')
    elif 'Application' in type_list:
        type_list = list(category_map.keys()).index('Application')
    elif 'OperatingSystem' in type_list:
        type_list = list(category_map.keys()).index('OperatingSystem')
    elif 'Hardware' in type_list:
        type_list = list(category_map.keys()).index('Hardware')
    elif 'Application' in type_list:
        type_list = list(category_map.keys()).index('Application')
    elif 'Exploit' in type_list:
        type_list = list(category_map.keys()).index('Exploit')
    return type_list


@bp.route('/<limit>')
# returned Node: id, labels, items()
def retrieve_graph(limit):
    def work(tx, _limit):
        cql_vuln = "match (v:Vulnerability) return v.cve_id as cve_id limit $limit"
        result = tx.run(cql_vuln, limit=_limit).data()
        cve_id_list, nodes, links = [item['cve_id'] for item in result], [], []

        cql_get_family = "match (v:Vulnerability)-[r]-(a:Family) where v.cve_id in $cve_id_list return v,r,a"
        cql_get_assets = 'match (v:Vulnerability)-[r1]-(af:Family)-[r2]-(a:Asset) where v.cve_id in $cve_id_list return v,r1,af,r2,a'

        result = tx.run(cql_get_assets, cve_id_list=cve_id_list)
        node_map, rel_map = {}, {}
        global category_map
        for entry in result:
            '''part for nodes'''
            for i in [0, 2, 4]:
                pass
                node = {'type': list(entry[i].labels), 'name': entry[i][label_to_id_field(list(entry[i].labels)[0])]}
                for _tuple in entry[i].items():
                    node[_tuple[0]] = _tuple[1]
                '''graph related'''
                node['category'] = get_node_category(node['type'])
                # node['symbolSize'] = get_symbol_size(node['type'][0])
                if 'Vulnerability' in node['type'] or 'Family' in node['type']:
                    node['label'] = vul_label_settings
                node_map[node['name']] = node

            '''part for relationship'''
            for i in [1, 3]:
                rel = {'name': entry[i]['rid'], 'category': entry[i].type}
                for _tuple in entry[i].items():
                    rel[_tuple[0]] = _tuple[1]
                rel['source'], rel['target'] = rel['rid'].split('->')
                '''graph related'''
                # rel['lineStyle'] = {
                #     'curveness': (i - 2) / 8
                # }
                rel_map[rel['name']] = rel

        return {'categories': list(category_map.values()), "nodes": list(node_map.values()),
                "links": list(rel_map.values())}

    limit = min(50, int(limit))
    res = neo.get_session().read_transaction(work, limit)
    return res


@bp.route('/test/<limit>')
def test(limit):
    def work(tx, _limit):
        cql_vuln = "match (vuln:Vulnerability) return vuln limit $limit"
        result = tx.run(cql_vuln, limit=_limit).data()
        return result

    res = neo.get_session().read_transaction(work, int(limit))
    pprint(json.dumps(res))
    return json.dumps(res)


@bp.route('/search/<keyword>')
def search_graph(keyword):
    def work(tx, limit_):
        cql1 = "match (asset:Asset)-[has]->(vuln:Vulnerability{cve_id:'" + keyword + "'}) return asset,has,vuln"
        cql2 = "match (vuln:Vulnerability{cve_id:'" + keyword + "'})-[cause]->(exploit:Attack) return exploit,cause,vuln"
        result = tx.run(cql1).data()
        return assemble_graph_data(result)

    res = neo.get_session().read_transaction(work, keyword)
    return res
