from py2neo import RelationshipMatcher, NodeMatcher

from db import neo
from logger_factory import mylogger_p
from vuln_kg.init_kg_p import get_node_stats

if __name__ == '__main__':
    # print(f"Neo4j stat:\n{get_node_stats()}")
    # vuln_node = neo.get_node('Vulnerability', cve_id='CVE-2003-0003').first()
    # rels = RelationshipMatcher(neo.graph).match([vuln_node], r_type='Affects')
    # pass
    # print([i for i in range(0, int(get_node_stats()['Vuln']), 10000)])
    # print([i for i in range(0, 16384, 10000)])

    # neo.add_asset_family_node('cpe:2.3:a:\@thi.ng\/egf_project:\@thi.ng\/egf:')

    cursor = NodeMatcher(neo.graph).match("Asset").skip(0).limit(30)
    family_cnt = 0
    for asset_node in cursor:
        asset_cnt = 0
        neo.add_asset_family_node(dict(asset_node)['cpe23uri'])
