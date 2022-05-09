import json
import time
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
        result["asset_count"] = result['app_count'] + result['os_count'] + result['hw_count']
        result["affected_asset"] = result['affected_app'] + result['affected_os'] + result['affected_hw']
        result["family_cnt"] = result['app_family'] + result['os_family'] + result['hw_family']
        return result

    res = neo.get_session().read_transaction(work)
    # res = neo.get_movie()
    print("time elapsed:" + str(time.time() - t0))
    return res


@bp.route('/<limit>')
# returned Node: id, labels, items()
def retrieve_graph(limit):
    def work(tx, limit_):
        cql_vuln = "match (vuln:Vulnerability) return vuln.eid limit $limit_"
        result = tx.run(cql_vuln, limit_=limit_).data()
        eid_list = []
        for item in result:
            eid_list.append(item["vuln.eid"])

        cql_get_asset = "match (asset)-[r]->(vuln:Vulnerability) where vuln.eid in " + str(
            eid_list) + " return asset, r, vuln"
        cql_get_exploit = "match (vuln:Vulnerability)-[r]->(exploit:Attack) where vuln.eid in " + str(
            eid_list) + "return exploit,r,vuln"
        nodes, links = [], []

        result = tx.run(cql_get_asset).data()
        graph_data = assemble_graph_data(assets=[d["asset"] for d in result], vulns=[d["vuln"] for d in result],
                                         rels=[d["r"] for d in result])
        nodes.extend(graph_data["nodes"])
        links.extend(graph_data["links"])

        result = tx.run(cql_get_exploit).data()
        graph_data = assemble_graph_data(exploits=[d["exploit"] for d in result], rels=[d["r"] for d in result])
        nodes.extend(graph_data["nodes"])
        links.extend(graph_data["links"])

        return {"nodes": nodes, "links": links}

    limit = min(100, int(limit))
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
