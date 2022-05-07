from py2neo import RelationshipMatcher

from db import neo
from logger_factory import mylogger_p
from vuln_kg.init_kg_p import get_node_stats

if __name__ == '__main__':
    # print(f"Neo4j stat:\n{get_node_stats()}")
    vuln_node = neo.get_node('Vulnerability', cve_id='CVE-2003-0003').first()
    rels = RelationshipMatcher(neo.graph).match([vuln_node], r_type='Affects')
    pass
