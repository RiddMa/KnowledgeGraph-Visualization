import json
import time
from pprint import pprint

from flask import Blueprint

from db import neo, mg
from web.data_converter import assemble_graph_data, _retrieve_graph_stats, _retrieve_graph_w_limit
from web.search_provider import basic_neo_search

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
    return basic_neo_search(keyword)
