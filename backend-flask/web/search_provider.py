from db import neo
from web.data_converter import _retrieve_cve, _retrieve_cpe


def basic_neo_search(keyword):
    # def search_cve(tx):
    #     cql1 = "match (asset:Asset)-[has]->(vuln:Vulnerability{cve_id:$keyword'}) return asset,has,vuln"
    #     # cql2 = "match (vuln:Vulnerability{cve_id:'" + keyword + "'})-[cause]->(exploit:Attack) return exploit,cause,vuln"
    #     result = tx.run(cql1, keyword=keyword).data()
    #     return
    #
    # def search_cpe(tx):
    #     pass

    if keyword.startswith('CVE'):
        res = neo.get_session().read_transaction(_retrieve_cve, keyword)
    elif keyword.startswith('cpe'):
        res = neo.get_session().read_transaction(_retrieve_cpe, keyword)
    else:
        res = ''
    return res
