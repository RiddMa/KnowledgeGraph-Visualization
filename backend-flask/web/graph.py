import json
import time
from pprint import pprint

from flask import Blueprint

from db import neo, mg
from web.data_converter import assemble_graph_data, _retrieve_graph_stats, _retrieve_graph_w_limit

bp = Blueprint('graph', __name__, url_prefix='/api/graph')


@bp.route('/')
def retrieve_graph_stats():
    t0 = time.time()

    res = neo.get_session().read_transaction(_retrieve_graph_stats)
    res['exploit'].extend(mg.get_exploit_stats())

    print("time elapsed:" + str(time.time() - t0))
    return json.dumps(res)


@bp.route('/<limit>')
# returned Node: id, labels, items()
def retrieve_graph(limit):
    t0 = time.time()

    limit = min(200, int(limit))
    res = neo.get_session().read_transaction(_retrieve_graph_w_limit, limit)
    print("time elapsed:" + str(time.time() - t0))
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
    def search_cve(tx):
        cql1 = "match (asset:Asset)-[has]->(vuln:Vulnerability{cve_id:$keyword'}) return asset,has,vuln"
        # cql2 = "match (vuln:Vulnerability{cve_id:'" + keyword + "'})-[cause]->(exploit:Attack) return exploit,cause,vuln"
        result = tx.run(cql1,keyword=keyword).data()
        return assemble_graph_data(result)

    def search_cpe(tx):
        pass


    if keyword.startswith('CVE'):
        res = neo.get_session().read_transaction(search_cve, keyword)
    elif keyword.startswith('cpe'):
        res = neo.get_session().read_transaction(search_cve, keyword)
    else:
        res = ''
    return res
