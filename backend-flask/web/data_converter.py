from math import sqrt
from typing import Dict, Union

from db import neo


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


def _retrieve_graph_stats(tx):
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
    # result = {"vul_count": tx.run(cql_vuln).data()[0]["vul_count"],
    #           "exploit_count": tx.run(cql_atk).data()[0]["exploit_count"],
    #           "app_count": tx.run(cql_app).data()[0]["app_count"],
    #           "os_count": tx.run(cql_os).data()[0]["os_count"],
    #           "hw_count": tx.run(cql_hw).data()[0]["hw_count"],
    #           "app_family": tx.run(cql_app_family).data()[0]["cnt"],
    #           "os_family": tx.run(cql_os_family).data()[0]["cnt"],
    #           "hw_family": tx.run(cql_hw_family).data()[0]["cnt"],
    #           'affected_app': tx.run(cql_affected_app).data()[0]["cnt"],
    #           'affected_os': tx.run(cql_affected_os).data()[0]["cnt"],
    #           'affected_hw': tx.run(cql_affected_hw).data()[0]["cnt"],
    #           }

    # result = {
    #     'vul': {
    #         'vul_count': tx.run(cql_vuln).data()[0]["vul_count"],
    #         'affected_asset': -1,
    #         'affected_app': tx.run(cql_affected_app).data()[0]["cnt"],
    #         'affected_os': tx.run(cql_affected_os).data()[0]["cnt"],
    #         'affected_hw': tx.run(cql_affected_hw).data()[0]["cnt"],
    #     },
    #     'asset': {
    #         'asset_count': -1,
    #         'family_cnt': -1,
    #         'app_family': tx.run(cql_app_family).data()[0]["cnt"],
    #         'app_count': tx.run(cql_app).data()[0]["app_count"],
    #         'os_family': tx.run(cql_os_family).data()[0]["cnt"],
    #         'os_count': tx.run(cql_os).data()[0]["os_count"],
    #         'hw_family': tx.run(cql_hw_family).data()[0]["cnt"],
    #         'hw_count': tx.run(cql_hw).data()[0]["hw_count"],
    #     },
    #     'exploit': {
    #         'exploit_count': tx.run(cql_atk).data()[0]["exploit_count"],
    #     },
    # }
    # result['vul']["affected_asset"] = result['vul']['affected_app'] + result['vul']['affected_os'] + result['vul'][
    #     'affected_hw']
    # result['asset']["asset_count"] = result['asset']['app_count'] + result['asset']['os_count'] + result['asset'][
    #     'hw_count']
    # result['asset']["family_cnt"] = result['asset']['app_family'] + result['asset']['os_family'] + result['asset'][
    #     'hw_family']
    # # return result
    # # a = [list(i[1].items()) for i in list(result.items())]
    # # return json.dumps({'vul': a[0], 'asset': a[1], 'exploit': a[2]})
    # _res = [list(i[1].items()) for i in list(result.items())]
    # for item_list in _res:
    #     for item in item_list:
    #         _res[_res.index(item_list)][item_list.index(item)] = {item[0]: item[1]}
    # ans = {
    #     'vul': _res[0],
    #     'assets': _res[1],
    #     'exploit': _res[2],
    # }
    # return json.dumps(ans)
    result = {
        'vul': [
            {'name': 'vul_count', 'value': tx.run(cql_vuln).data()[0]["vul_count"]},
            {'name': 'affected_asset', 'value': -1},
            {'name': 'affected_app', 'value': tx.run(cql_affected_app).data()[0]["cnt"]},
            {'name': 'affected_os', 'value': tx.run(cql_affected_os).data()[0]["cnt"]},
            {'name': 'affected_hw', 'value': tx.run(cql_affected_hw).data()[0]["cnt"]},
        ],
        'asset': [
            {'name': 'asset_count', 'value': -1},
            {'name': 'family_cnt', 'value': -1},
            {'name': 'app_family', 'value': tx.run(cql_app_family).data()[0]["cnt"]},
            {'name': 'app_count', 'value': tx.run(cql_app).data()[0]["app_count"]},
            {'name': 'os_family', 'value': tx.run(cql_os_family).data()[0]["cnt"]},
            {'name': 'os_count', 'value': tx.run(cql_os).data()[0]["os_count"]},
            {'name': 'hw_family', 'value': tx.run(cql_hw_family).data()[0]["cnt"]},
            {'name': 'hw_count', 'value': tx.run(cql_hw).data()[0]["hw_count"]},
        ],
        'exploit': [
            {'name': 'exploit_count', 'value': tx.run(cql_atk).data()[0]["exploit_count"]},
        ],
    }
    result['vul'][1]['value'] = result['vul'][2]['value'] + result['vul'][3]['value'] + result['vul'][4]['value']
    result['asset'][1]['value'] = result['asset'][2]['value'] + result['asset'][4]['value'] + result['asset'][6][
        'value']
    result['asset'][0]['value'] = result['asset'][3]['value'] + result['asset'][5]['value'] + result['asset'][7][
        'value']

    return result


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


def get_symbol_size(_type, cnt=0) -> int:
    if _type == 'v' or _type == 'e':
        base_size = 50
    elif _type == 'af':
        base_size = 30
    else:
        base_size = 20
    # _symbol_size_map = {
    #     'Vulnerability': 30,
    #     'Family': 20,
    #     'Asset': 10,
    #     'Application': 10,
    #     'OperatingSystem': 10,
    #     'Hardware': 10,
    #     'Exploit': 30,
    # }
    # return int(base_size + sqrt(cnt))
    return int(base_size + 5 * sqrt(cnt))


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


vul_label_settings: dict = {
    'show': True,
    'position': 'inside',
    'fontSize': 14,
    'overflow': 'break',
    'fontWeight': 'bold',
    'textBorderColor': 'inherit',
    'textBorderWidth': '2',
}
af_label_settings: dict = {
    'show': True,
    'position': 'inside',
    'fontSize': 10,
    'overflow': 'break',
    'fontWeight': 'bold',
    'textBorderColor': 'inherit',
    'textBorderWidth': '2',
}
e_label_settings = {
    'show': True,
    'position': 'inside',
    'fontSize': 10,
    'overflow': 'break',
    'fontWeight': 'bold',
    'textBorderColor': 'inherit',
    'textBorderWidth': '2',
}
category_map: dict = {
    'Vulnerability': {'name': '漏洞'},
    'Family': {'name': '家族'},
    'Asset': {'name': '资产'},
    'Application': {'name': '应用程序'},
    'OperatingSystem': {'name': '操作系统'},
    'Hardware': {'name': '硬件'},
    'Exploit': {'name': '利用'},
}


def get_category_list():
    return list(category_map.values())


def _retrieve_v_af(tx, cve_id):
    cql = 'MATCH (v:Vulnerability)-[r]-(af:Asset:Family) ' \
          'WHERE v.cve_id=$cve_id ' \
          'RETURN v,r,af'
    _res = tx.run(cql, cve_id=cve_id)
    v_map, r_map, af_map = {}, {}, {}
    for entry in _res:
        '''convert Vulnerability'''
        for i in [0]:
            _convert_node(entry, i, v_map)
        '''convert AssetFamily'''
        for i in [2]:
            _convert_node(entry, i, af_map)
        '''convert Relationship'''
        for i in [1]:
            _convert_link(entry, i, r_map)

    '''add label, and calculate node size with asset_cnt'''
    for node_entry in v_map.items():
        node_cnt = 0
        for rel_entry in r_map.items():
            if rel_entry[0].startswith(node_entry[1]['name']):
                node_cnt += rel_entry[1]['asset_cnt']
        node_entry[1]['label'] = vul_label_settings
        node_entry[1]['symbolSize'] = get_symbol_size('v', node_cnt)
    for node_entry in af_map.items():
        node_cnt = 0
        for rel_entry in r_map.items():
            if rel_entry[0].startswith(node_entry[1]['name']):
                node_cnt += rel_entry[1]['asset_cnt']
        node_entry[1]['label'] = af_label_settings
        node_entry[1]['symbolSize'] = get_symbol_size('af', node_cnt)

    return v_map, r_map, af_map


def _retrieve_v_af_a(tx, cve_id):
    cql = 'MATCH (v:Vulnerability)-[r1]-(af:Asset:Family)-[r2]-(a:Asset) ' \
          'WHERE v.cve_id=$cve_id ' \
          'RETURN v,r1,af,r2,a'
    _res = tx.run(cql, cve_id=cve_id)
    v_map, r1_map, af_map, r2_map, a_map = {}, {}, {}, {}, {}
    for entry in _res:
        '''convert Vulnerability'''
        _convert_node(entry, 0, v_map)
        '''convert AssetFamily'''
        _convert_node(entry, 2, af_map)
        '''convert Asset'''
        _convert_node(entry, 4, a_map)
        '''convert Relationship'''
        _convert_link(entry, 1, r1_map)
        _convert_link(entry, 3, r2_map)

    '''calculate size_cnt with asset_cnt'''
    for _r in r1_map.values():
        _key = _r['name'].split('->')[0]
        if _key.startswith('CVE'):
            v_map[_key]['size_cnt'] += _r['asset_cnt']
        elif _key.startswith('cpe'):
            af_map[_key]['size_cnt'] += _r['asset_cnt']
    '''add label, calculate node size with size_cnt'''
    for _v in v_map.values():
        _v['label'] = vul_label_settings
        _v['symbolSize'] = get_symbol_size('v', _v['size_cnt'])
    for _af in af_map.values():
        _af['label'] = af_label_settings
        _af['symbolSize'] = get_symbol_size('af', _af['size_cnt'])
    for _a in a_map.values():
        _a['symbolSize'] = get_symbol_size('a')

    return v_map, r1_map, af_map, r2_map, a_map


def _convert_link(entry, i, rel_map):
    rel = {'name': entry[i]['rid'], 'category': entry[i].type}
    for _tuple in entry[i].items():
        rel[_tuple[0]] = _tuple[1]
    rel['source'], rel['target'] = rel['rid'].split('->')
    '''graph related'''
    rel['lineStyle'] = {
        'curveness': (i - 2) / 8
    }
    rel_map[rel['name']] = rel


def _convert_node(entry, i, node_map):
    name = entry[i][label_to_id_field(list(entry[i].labels)[0])]
    if name not in node_map:
        node = {'type': list(entry[i].labels), 'name': name}
        for _tuple in entry[i].items():
            node[_tuple[0]] = _tuple[1]
        '''graph related'''
        node['category'] = get_node_category(node['type'])
        node['size_cnt'] = 0
        node_map[node['name']] = node


def _retrieve_af_a(tx, af23uri):
    cql = 'MATCH (af:Asset:Family)-[r]-(a:Asset) ' \
          'WHERE af.cpe23uri=$af23uri ' \
          'RETURN af,r,a'
    _res = tx.run(cql, af23uri=af23uri)
    af_map, r_map, a_map = {}, {}, {}
    for entry in _res:
        '''convert AssetFamily'''
        for i in [0]:
            _convert_node(entry, i, af_map)
        '''convert Asset'''
        for i in [2]:
            _convert_node(entry, i, a_map)
        '''part for relationship'''
        for i in [1]:
            _convert_link(entry, i, r_map)

    return af_map, r_map, a_map


def _retrieve_af_e(tx, af23uri, cve_id):
    cql = 'MATCH (af:Asset:Family)-[r]-(e:Exploit) ' \
          'WHERE af.cpe23uri=$af23uri AND $cve_id IN e.cve_ids ' \
          'RETURN af,r,e'
    _res = tx.run(cql, af23uri=af23uri, cve_id=cve_id)
    af_map, r_map, e_map = {}, {}, {}
    for entry in _res:
        '''convert AssetFamily'''
        for i in [0]:
            _convert_node(entry, i, af_map)
        '''convert Asset'''
        for i in [2]:
            _convert_node(entry, i, e_map)
        '''part for relationship'''
        for i in [1]:
            _convert_link(entry, i, r_map)

    return af_map, r_map, e_map


def _retrieve_v_e_af(tx, cve_id):
    cql = 'MATCH (v:Vulnerability)-[r1]-(e:Exploit)-[r2]-(af:Asset:Family) ' \
          'WHERE v.cve_id=$cve_id ' \
          'RETURN v,r1,e,r2,af'
    _res = tx.run(cql, cve_id=cve_id)
    v_map, r1_map, e_map, r2_map, af_map = {}, {}, {}, {}, {}
    for entry in _res:
        '''convert Vulnerability'''
        _convert_node(entry, 0, v_map)
        '''convert AssetFamily'''
        _convert_node(entry, 2, e_map)
        '''convert Asset'''
        _convert_node(entry, 4, af_map)
        '''convert Relationship'''
        _convert_link(entry, 1, r1_map)
        _convert_link(entry, 3, r2_map)

    for _e in e_map.values():
        _e['label'] = e_label_settings
        _e['symbolSize'] = get_symbol_size('e')

    return v_map, r1_map, e_map, r2_map, af_map


# def _retrieve_graph_w_limit(tx, _limit):
#     cql_vuln = "match (v:Vulnerability) return v.cve_id as cve_id limit $limit"
#     result = tx.run(cql_vuln, limit=_limit).data()
#     cve_id_list, nodes, links = [item['cve_id'] for item in result], [], []
#     node_map, rel_map = {}, {}
#     for cve_id in cve_id_list:
#         cql_get_count = 'match (v:Vulnerability)-[r1]-(af:Family)-[r2]-(a:Asset) where v.cve_id = $cve_id return count(distinct(a)) as a'
#         cnt = tx.run(cql_get_count, cve_id=cve_id).data()[0]['a']
#         # if cnt > 200:
#         #     continue
#         cql_get_assets = 'match (v:Vulnerability)-[r1]-(af:Family)-[r2]-(a:Asset) where v.cve_id = $cve_id return v,r1,af,r2,a'
#         result = tx.run(cql_get_assets, cve_id=cve_id)
#         for entry in result:
#             '''part for nodes'''
#             for i in [0, 2, 4]:
#                 name = entry[i][label_to_id_field(list(entry[i].labels)[0])]
#                 if name not in node_map:
#                     node = {'type': list(entry[i].labels),
#                             'name': name}
#                     for _tuple in entry[i].items():
#                         node[_tuple[0]] = _tuple[1]
#                     '''graph related'''
#                     node['category'] = get_node_category(node['type'])
#                     # node['symbolSize'] = get_symbol_size(node['type'][0])
#                     if 'Vulnerability' in node['type']:
#                         node['label'] = vul_label_settings
#                         node['symbolSize'] = get_symbol_size('v', cnt)
#                     elif 'Family' in node['type']:
#                         node['label'] = af_label_settings
#                         node['symbolSize'] = get_symbol_size('af', cnt)
#                     node_map[node['name']] = node
#
#             '''part for relationship'''
#             for i in [1, 3]:
#                 rel = {'name': entry[i]['rid'], 'category': entry[i].type}
#                 for _tuple in entry[i].items():
#                     rel[_tuple[0]] = _tuple[1]
#                 rel['source'], rel['target'] = rel['rid'].split('->')
#                 '''graph related'''
#                 rel['lineStyle'] = {
#                     'curveness': (i - 2) / 8
#                 }
#                 rel_map[rel['name']] = rel
#
#     return {'categories': list(category_map.values()), "nodes": list(node_map.values()),
#             "links": list(rel_map.values())}

def _retrieve_cve(tx, cve_id):
    n_map, r_map = {}, {}
    v_map, r1_map, af_map, r2_map, a_map = _retrieve_v_af_a(tx, cve_id=cve_id)
    n_map = {**v_map, **af_map, **a_map, **n_map}
    r_map = {**r1_map, **r2_map, **r_map}
    _, r1_map, e_map, r2_map, _ = _retrieve_v_e_af(tx, cve_id=cve_id)
    n_map = {**e_map, **n_map}
    r_map = {**r1_map, **r2_map, **r_map}
    return {'categories': get_category_list(), "nodes": list(n_map.values()), "links": list(r_map.values())}


def _retrieve_cpe(tx, cpe23uri):
    return {}


def _retrieve_graph_w_limit(tx, _limit):
    cql_vuln = "match (v:Vulnerability) return v.cve_id as cve_id limit $limit"
    result = tx.run(cql_vuln, limit=_limit).data()
    cve_ids, nodes, links = [item['cve_id'] for item in result], [], []
    n_map, r_map = {}, {}
    for cve_id in cve_ids:
        v_map, r1_map, af_map, r2_map, a_map = _retrieve_v_af_a(tx, cve_id=cve_id)
        n_map = {**v_map, **af_map, **a_map, **n_map}
        r_map = {**r1_map, **r2_map, **r_map}
        _, r1_map, e_map, r2_map, _ = _retrieve_v_e_af(tx, cve_id=cve_id)
        n_map = {**e_map, **n_map}
        r_map = {**r1_map, **r2_map, **r_map}

    return {'categories': get_category_list(), "nodes": list(n_map.values()), "links": list(r_map.values())}
    # return {'categories': get_category_list(), "nodes": nodes, "links": links}


if __name__ == '__main__':
    # res = neo.get_session().read_transaction(_retrieve_v_af, cve_id='CVE-2015-4551')
    # res = neo.get_session().read_transaction(_retrieve_af_a, af23uri='cpe:2.3:o:redhat:linux:')
    res = neo.get_session().read_transaction(_retrieve_graph_w_limit, 10)
    # res = neo.get_session().read_transaction(_retrieve_v_af_a, cve_id='CVE-2015-4551')
    # res = neo.get_session().read_transaction(_retrieve_v_e_af, cve_id='CVE-1999-0002')
    print(res)
