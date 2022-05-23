# from py2neo import RelationshipMatcher, NodeMatcher
#
# from db import neo
# from logger_factory import mylogger_p
# from vuln_kg.init_kg_p import get_node_stats
import re

from py2neo import NodeMatcher, RelationshipMatcher

# from db import neo
from db import neo

if __name__ == '__main__':
    # print(f"Neo4j stat:\n{get_node_stats()}")
    # vuln_node = neo.get_node('Vulnerability', cve_id='CVE-2003-0003').first()
    # rels = RelationshipMatcher(neo.graph).match([vuln_node], r_type='Affects')
    # pass
    # print([i for i in range(0, int(get_node_stats()['Vuln']), 10000)])
    # print([i for i in range(0, 16384, 10000)])

    # neo.add_asset_family_node('cpe:2.3:a:\@thi.ng\/egf_project:\@thi.ng\/egf:')

    # cursor = NodeMatcher(neo.graph).match("Asset").skip(0).limit(30)
    # family_cnt = 0
    # for asset_node in cursor:
    #     asset_cnt = 0
    #     neo.add_asset_family_node(dict(asset_node)['cpe23uri'])
    # print(int((0 / 16) - 1))
    # print(
    #     neo.add_rel_cql_vaf('CVE-1999-0001', 'cpe:2.3:o:freebsd:freebsd:', 'CVE-1999-0001->cpe:2.3:o:freebsd:freebsd:'))
    # print('cpe:2.3:a:emc:rsa_certificate_manager:*:*:*:*:*:*:*:*'.split(':')[2])

    # cursor = NodeMatcher(neo.graph).match("Exploit")
    # for exploit_node in cursor:
    #     cve_ids = exploit_node['cve_ids']
    #     for cve_id_no in cve_ids:
    #         cve_id = f'CVE-{cve_id_no}'
    #         vuln_node = neo.get_node('Vulnerability', cve_id=cve_id).first()
    #         if vuln_node is not None:
    #             neo.add_rel_cql_ev(edb_id=exploit_node['edb_id'], cve_id=cve_id)
    # neo.close_db()

    # neo.add_rel_cql_vaf_cnt(cve_id='CVE-2009-3456')
    # cql = 'MATCH (v:Vulnerability {cve_id:$cve_id})-[r]->(af:Family) RETURN r.assets'
    # res = neo.get_session().run(cql, cve_id='CVE-2009-3456').values()[0][0]
    # print(res)

    # cql = "match (a:Asset) where a.cpe23uri starts with 'cpe:2.3:a:google:chrome:1.0' return a"
    # res = neo.get_session().run(cql).values()
    # res = [entry['a'] for entry in res if re.match(pattern, entry['a']['cpe23uri'])]
    # print(res)

    # cql = 'MATCH (v:Vulnerability {cve_id:$cve_id})-[r]->(af:Family) RETURN r.assets as assets, r.rid as rid'
    # res = neo.get_session().run(cql, cve_id='CVE-2015-6435').data()
    # print(res)
    # for af in res:
    #     for cpe23uri in af['assets']:
    #         print(cpe23uri)
    #         prefix = cpe23uri[:cpe23uri.find('*')]
    #         pass

    # neo.add_rel_cql_vaf_cnt('CVE-2015-6435')
    # a = 'cpe:2.3:a:cisco:unified_computing_system:->CVE-2015-6435'.split('->')
    # b = a[1] + '->' + a[0]
    # pass
    a = {'1': 1}
    b = {'2': 2}
    c = {'3': 3}
    d = {'3': 3}
    a = {**a, **b, **c, **d}
    print(a)
    b = {}
    c = {}
    d = {}
    a = {**a, **b, **c, **d}
    print(a)
    # neo.get_rel_cql_vaf('CVE-2014-1859')
