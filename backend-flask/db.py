import logging
import re
from datetime import datetime
from uuid import uuid4
import pymongo as pymongo
from flask import g
from neo4j import (GraphDatabase, basic_auth)
import pymongo
from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
from py2neo.cypher import cypher_escape
import secret
from logger_factory import mylogger, mylogger_p

driver = GraphDatabase.driver(secret.neo_driver_url,
                              auth=basic_auth(secret.neo_username, secret.neo_password))


class MyMongo:

    def __init__(self):
        self.client = pymongo.MongoClient(secret.mongo_uri)
        if "cve_bot" not in self.client.list_database_names():
            mylogger('db').info('Database "cve_bot" does not exist.')
        self.data_db = self.client["cve_bot"]
        self.json = self.data_db["json"]
        self.nvd_json_src = self.data_db['nvd_json_src']
        self.nvd_json = self.data_db['nvd_json']
        self.edb_html = self.data_db['edb_html']
        self.edb_json = self.data_db['edb_json']
        self.cpe = self.data_db['cpe']

        self.web_db = self.client['vul_kg_web']
        self.graph_data = self.web_db['graph_data']

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def save_json(self, cve_id, content):
        doc = {"cve_id": cve_id, "content": content}
        # doc_id = self.json.insert_one(doc).inserted_id
        self.json.update_one({"cve_id": cve_id}, {"$set": doc}, upsert=True)
        mylogger('db').info(cve_id + ".json saved to MongoDB.")

    def get_all_cve(self) -> object:
        cursor = self.json.find({}, {"content": 1, "_id": 0})
        return cursor

    def get_nvd(self, cve_id=None):
        if cve_id is None:
            cursor = self.nvd_json.find({}, {"content": 1, "_id": 0})
            return cursor
        else:
            pass

    def get_cpe(self, cpe23uri=None):
        if cpe23uri is None:
            cursor = self.cpe.find({}, {"_id": 0})
            return cursor
        else:
            doc = self.cpe.find_one({"cpe23uri": cpe23uri}, {"_id": 0})
            return doc

    def get_edb(self, edb_id=None):
        if edb_id is None:
            cursor = self.edb_json.find({}, {"content": 1, "_id": 0})
            return cursor
        else:
            doc = self.edb_json.find_one({"edb_id": edb_id}, {"content": 1, "_id": 0})
            return doc

    def check_index(self):
        self.graph_data.create_index([('timestamp', pymongo.DESCENDING)], name='timestamp_index')

    def save_graph_data(self, doc=None):
        timestamp = datetime.utcnow()
        self.graph_data.update_one({"timestamp": timestamp}, {"$set": doc}, upsert=True)
        mylogger('db').info(str(timestamp) + f".json saved to MongoDB {self.graph_data.name}.")

    def get_graph_data(self):
        doc = self.graph_data.find_one({}, {})
        return doc

    def get_exploit_stats(self):
        doc = self.edb_json.aggregate([
            {"$group": {"_id": "$content.type", "value": {"$sum": 1}}}
        ])
        doc = [{'name': entry['_id'], 'value': entry['value']} for entry in doc]
        sort_order = {'webapps': 0, 'remote': 1, 'local': 2, 'dos': 3}
        doc.sort(key=lambda val: sort_order[val['name']])
        return doc


mg = MyMongo()


class MyNeo:
    def __init__(self):
        # for py2neo
        self.graph = Graph(secret.neo_uri,
                           name=secret.db_name,
                           auth=(secret.neo_username, secret.neo_password))
        mylogger('db').info('py2neo connected')
        # for neo4j
        self.driver = GraphDatabase.driver(secret.neo_driver_url,
                                           auth=basic_auth(secret.neo_username, secret.neo_password))
        mylogger('db').info('neo4j connected')
        self.session = self.driver.session(database=secret.neo_db)
        mylogger('db').info("neo4j created session")
        self.session.run("match (n) return n limit 1")
        mylogger('db').info("neo4j run init query")
        self.index_map = {
            'Vulnerability': 'cve_id',
            'Asset': 'cpe23uri',
            'Application': 'cpe23uri',
            'OperatingSystem': 'cpe23uri',
            'Hardware': 'cpe23uri',
            'Exploit': 'edb_id'
        }
        self.part_type_map = {
            'a': 'Application',
            'o': 'OperatingSystem',
            'h': 'Hardware'
        }

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_db()

    def get_session(self):
        """
        Used for getting singleton session for neo4j.

        :return: neo4j driver session
        """

        if self.session is None:
            self.session = self.driver.session(database=secret.neo_db)
            mylogger('db').info("neo4j created session")
        return self.session

    def get_node(self, *args, **kwargs):
        """

        :param args: argument for label
        :param kwargs: argument for matching conditions
        :return:
        """
        cursor = NodeMatcher(self.graph).match(*args, **kwargs)
        if cursor.first() is None:
            mylogger('init_kg').warning(f"{args} node {kwargs} not found")
        return cursor

    def match_asset(self, pattern: str):
        def work_prefix(tx):
            cql = "MATCH (a:Asset) WHERE a.cpe23uri STARTS WITH $prefix RETURN a"
            match_list = tx.run(cql, prefix=pattern[:pattern.find('.*')]).data()
            res = [entry['a'] for entry in match_list if re.match(pattern, entry['a']['cpe23uri'])]
            return res

        def work_re(tx):
            cql = "MATCH (a:Asset) WHERE a.cpe23uri =~ $pattern RETURN a"
            res = tx.run(cql, pattern=pattern)
            return res

        with self.get_session() as session:
            # return session.read_transaction(work_re)
            return session.read_transaction(work_prefix)

    def match_asset_family(self, pattern: str):
        def work_prefix(tx):
            cql = "MATCH (a:Family) WHERE a.cpe23uri STARTS WITH $prefix RETURN a"
            match_list = tx.run(cql, prefix=pattern[:pattern.find('.*')]).data()
            res = [entry['a'] for entry in match_list if re.match(pattern, entry['a']['cpe23uri'])]
            return res

        def work_exact_match(tx):
            cql = "MATCH (a:Family {cpe23uri:$pattern}) RETURN a"
            res = tx.run(cql, pattern=pattern).data()[0]['a']
            return res

        with self.get_session() as session:
            # return session.read_transaction(work_re)
            return session.read_transaction(work_exact_match)

    def add_asset_family_node(self, cpe23uri):
        def check_work(tx):
            cql = 'MATCH (a:Asset:Family {cpe23uri:$cpe23uri}) RETURN COUNT(a) as cnt'
            cnt = tx.run(cql, cpe23uri=family_cpe23uri).data()[0]['cnt']
            return cnt

        def add_work(tx):
            cqls = {
                'a': 'CREATE (a:Asset:Application:Family {cpe23uri:$family_cpe23uri}) RETURN a',
                'o': 'CREATE (a:Asset:OperatingSystem:Family {cpe23uri:$family_cpe23uri}) RETURN a',
                'h': 'CREATE (a:Asset:Hardware:Family {cpe23uri:$family_cpe23uri}) RETURN a'
            }
            _res = tx.run(cqls[cpe23uri.split(':')[2]], family_cpe23uri=family_cpe23uri).data()
            return _res

        arr = cpe23uri.split(':')
        family_cpe23uri = ''
        for i in range(0, 5):
            family_cpe23uri += (arr[i] + ':')
        # label = self.part_type_map[]
        with self.get_session() as session:
            if session.read_transaction(check_work) == 0:
                res = session.write_transaction(add_work)
                mylogger('db').info(f"Added asset family {family_cpe23uri}")
                return 1
            else:
                mylogger('db').info(f"Exist asset family {family_cpe23uri}")
                return 0

    def fix_asset_family_label(self, cpe23uri):
        def fix_work(tx):
            cqls = {
                'a': 'MATCH (a:Asset:Family {cpe23uri:$cpe23uri}) SET a:Application',
                'o': 'MATCH (a:Asset:Family {cpe23uri:$cpe23uri}) SET a:OperatingSystem',
                'h': 'MATCH (a:Asset:Family {cpe23uri:$cpe23uri}) SET a:Hardware'
            }
            return tx.run(cqls[cpe23uri.split(':')[2]], cpe23uri=family_cpe23uri)

        arr = cpe23uri.split(':')
        family_cpe23uri = ''
        for i in range(0, 5):
            family_cpe23uri += (arr[i] + ':')
        # label = self.part_type_map[cpe23uri.split(':')[2]]
        with self.get_session() as session:
            try:
                session.write_transaction(fix_work)
                return 1
            except BaseException as _e:
                mylogger_p('error').error(_e, exc_info=True)
                return 0

    def add_node(self, labels: list, props: dict) -> Node:
        """
        Add node of given labels and props to neo4j. A 'eid' attribute is auto generated for node identification.

        :param labels: neo4j labels for the node
        :param props: props for the node
        :return: Py2neo Node object
        """
        props['eid'] = str(uuid4())  # add unique identification for entity
        node = Node(*labels, **props)
        tx = self.graph.begin()
        tx.create(node)
        tx.commit()
        mylogger('db').info(f'Node {repr(labels)} {props["eid"]} added to {tx.graph.name} neo4j database')
        return node

    def add_relationship(self, start, type_, end, props=None):
        """
        Add relationship (start)-[type_]->(end) to neo4j database, if not exists.
        If rel already exist, won't add.

        :param start: start Node obj
        :param type_: relationship type as string
        :param end: end Node obj
        :param props: props for relationship
        :return: 1 if added new rel, 0 if rel exists
        """
        if RelationshipMatcher(neo.graph).match([start, end], r_type=type_).first() is not None:
            mylogger('db').info(
                f"Exist relationship {start[self.index_map[list(start.labels)[0]]]}--{type_}->{end[self.index_map[list(end.labels)[0]]]}")
            return 0

        if props is None:
            props = {}
        props['rid'] = str(uuid4())
        rel = Relationship(start, type_, end, **props)
        tx = self.graph.begin()
        tx.create(rel)
        tx.commit()
        mylogger('db').info(
            f"Added relationship {start[self.index_map[list(start.labels)[0]]]}--{type_}->{end[self.index_map[list(end.labels)[0]]]} to {tx.graph.name} neo4j database")
        return 1

    def add_rel_cql_va(self, cve_id, cpe23uri, props=None):
        # def check_rel(tx):
        #     cql = "MATCH (v:Vulnerability {cve_id:$cve_id})-[r:Affects]->(a:Asset {cpe23uri:$cpe23uri}) RETURN count(r)"
        #     res = tx.run(cql, cve_id=cve_id, cpe23uri=cpe23uri).data()
        #     return res

        def add_rel(tx):
            cql = "MATCH (v:Vulnerability {cve_id:$cve_id}),(a:Asset {cpe23uri:$cpe23uri})" \
                  "MERGE (v)-[r1:Affects {rid:$rid1}]->(a)" \
                  "MERGE (a)-[r2:Has {rid:$rid2}]->(v)"
            res = tx.run(cql, cve_id=cve_id, cpe23uri=cpe23uri, rid1=f'{cve_id}->{cpe23uri}',
                         rid2=f'{cpe23uri}->{cve_id}')
            return res

        with self.get_session() as session:
            # if session.read_transaction(check_rel) > 0:
            #     return 0
            # else:
            #
            # return 2
            num = session.write_transaction(add_rel)._summary.counters.relationships_created
            if num:
                mylogger('db').info(
                    f"Added relationship {cve_id}-[Affects]->{cpe23uri}")
                mylogger('db').info(
                    f"Added relationship {cve_id}<-[Has]-{cpe23uri}")
            else:
                mylogger('db').info(f"Exist relationship {cve_id}<-[r]->{cpe23uri}")
            return num

    def get_rel_cql_vaf(self, cve_id):
        def get_rel(tx):
            cql = 'MATCH (v:Vulnerability {cve_id:$cve_id})-[r]->(af:Family) RETURN r.assets as assets,r.asset_cnt as cnt, af.cpe23uri as target'
            return tx.run(cql, cve_id=cve_id).data()

        with self.get_session() as session:
            res = session.read_transaction(get_rel)
            return res

    def add_rel_cql_vaf(self, cve_id, cpe23uri):
        """

        :param cve_id: cve_id for vulnerability entry
        :param cpe23uri: full cpe23uri for asset
        :return:
        """

        def add_rel(tx):
            cql1 = "MATCH (v:Vulnerability {cve_id:$cve_id}),(a:Family {cpe23uri:$family_cpe23uri}) " \
                   "MERGE (a)-[r1:Has {rid:$rid1}]->(v) " \
                   "ON CREATE SET r1.assets = [$cpe23uri] SET r1.asset_cnt=0 " \
                   "WITH r1, apoc.coll.contains(r1.assets, $cpe23uri) AS r1e " \
                   "WHERE r1e = false " \
                   "SET r1.assets = r1.assets + $cpe23uri " \
                   "RETURN r1.assets "
            cql2 = "MATCH (v:Vulnerability {cve_id:$cve_id}),(a:Family {cpe23uri:$family_cpe23uri}) " \
                   "MERGE (v)-[r2:Affects {rid:$rid2}]->(a) " \
                   "ON CREATE SET r2.assets = [$cpe23uri] SET r2.asset_cnt=0 " \
                   "WITH r2, apoc.coll.contains(r2.assets, $cpe23uri) AS r2e " \
                   "WHERE r2e = false " \
                   "SET r2.assets = r2.assets + $cpe23uri " \
                   "RETURN r2.assets "
            tx.run(cql1, cve_id=cve_id, family_cpe23uri=family_cpe23uri, rid1=f'{family_cpe23uri}->{cve_id}',
                   cpe23uri=cpe23uri)
            res = tx.run(cql2, cve_id=cve_id, family_cpe23uri=family_cpe23uri, rid2=f'{cve_id}->{family_cpe23uri}',
                         cpe23uri=cpe23uri)
            return res

        arr = cpe23uri.split(':')
        family_cpe23uri = ''
        for i in range(0, 5):
            family_cpe23uri += (arr[i] + ':')
        with self.get_session() as session:
            num = session.write_transaction(add_rel)._summary.counters.relationships_created
            if num:  # if num == 1 then 2 edges created, weird though
                mylogger('db').info(
                    f"Added relationship {cve_id}-[Affects]->{family_cpe23uri}")
                mylogger('db').info(
                    f"Added relationship {cve_id}<-[Has]-{family_cpe23uri}")
                return 2
            else:
                mylogger('db').info(f"Exist relationship {cve_id}<-[r]->{family_cpe23uri}")
                return 0

    def add_rel_cql_vaf_cnt(self, cve_id):
        def find_rel(tx):
            cql = 'MATCH (v:Vulnerability {cve_id:$cve_id})-[r]->(af:Family) RETURN r.assets as assets, r.rid as rid, r.asset_cnt as cnt'
            return tx.run(cql, cve_id=cve_id).data()

        def find_asset(tx, _prefix):
            cql = 'match (a:Asset) where a.cpe23uri starts with $prefix return count(a)'
            return tx.run(cql, prefix=_prefix).values()[0][0]

        def add_cnt(tx, _rid, _cnt):
            # cql = 'MATCH ()-[r {rid:$_rid}]->() SET r.asset_cnt=r.asset_cnt+$_cnt'
            cql = 'MATCH ()-[r {rid:$_rid}]->() SET r.asset_cnt=$_cnt'
            return tx.run(cql, _rid=_rid, _cnt=_cnt)

        with self.get_session() as session:
            arr = session.read_transaction(find_rel)
            g_cnt = 0
            for af in arr:
                cnt = 0
                if af['cnt'] > 0:
                    continue
                for cpe23uri in af['assets']:
                    prefix = cpe23uri[:cpe23uri.find('*')]
                    cnt += session.read_transaction(find_asset, _prefix=prefix)
                session.write_transaction(add_cnt, _rid=af['rid'], _cnt=cnt)
                _tmp = af['rid'].split('->')
                session.write_transaction(add_cnt, _rid=f'{_tmp[1]}->{_tmp[0]}', _cnt=cnt)
                g_cnt += cnt
                mylogger('db').info(f"Added {cnt} relationship_cnt for {af['rid']}")
            mylogger('db').info(f"Added {g_cnt} relationship_cnt for {cve_id}")
            return g_cnt

    def add_rel_cql_afa(self, asset_uri):
        def work(tx):
            cql = 'MATCH (af:Asset:Family) WHERE af.cpe23uri = $prefix ' \
                  'MATCH (a:Asset) WHERE a.cpe23uri = $cpe23uri ' \
                  'MERGE (af)-[r1:ParentOf {rid:$rid1}]->(a) ' \
                  'MERGE (a)-[r2:ChildOf {rid:$rid2}]->(af)'
            return tx.run(cql, prefix=family_cpe23uri, cpe23uri=asset_uri, rid1=f'{family_cpe23uri}->{asset_uri}',
                          rid2=f'{asset_uri}->{family_cpe23uri}')

        arr = asset_uri.split(':')
        family_cpe23uri = ''
        for i in range(0, 5):
            family_cpe23uri += (arr[i] + ':')
        with self.get_session() as session:
            num = session.write_transaction(work)._summary.counters.relationships_created
            if num:
                mylogger('db').info(
                    f"Added relationship {family_cpe23uri}-[ParentOf]->{asset_uri}")
                mylogger('db').info(
                    f"Added relationship {family_cpe23uri}<-[ChildOf]-{asset_uri}")
            else:
                mylogger('db').info(f"Exist relationship {family_cpe23uri}<-[r]->{asset_uri}")
            return num

    def add_rel_cql_ev(self, edb_id, cve_id):
        """
        Exploit-[r]-Vulnerability
        :param edb_id:
        :param cve_id:
        :return:
        """

        def work(tx):
            cql = 'MATCH (e:Exploit) WHERE e.edb_id = $edb_id ' \
                  'MATCH (v:Vulnerability) WHERE v.cve_id = $cve_id ' \
                  'MERGE (e)-[r1:Exploits {rid:$rid1}]->(v) ' \
                  'MERGE (v)-[r2:ExploitedBy {rid:$rid2}]->(e)'
            return tx.run(cql, edb_id=edb_id, cve_id=cve_id, rid1=f'{edb_id}->{cve_id}', rid2=f'{cve_id}->{edb_id}')

        with self.get_session() as session:
            num = session.write_transaction(work)._summary.counters.relationships_created
            if num:  # if num == 1 then 2 edges created, weird though
                mylogger('db').info(
                    f"Added relationship {cve_id}-[ExploitedBy]->{edb_id}")
                mylogger('db').info(
                    f"Added relationship {cve_id}<-[Exploits]-{edb_id}")
                return 2
            else:
                mylogger('db').info(f"Exist relationship {cve_id}<-[r]->{edb_id}")
                return 0

    def add_rel_cql_eaf(self, edb_id, cpe23uri, assets, asset_cnt):
        """
        Exploit-[r]-AssetFamily
        :param edb_id:
        :param cpe23uri:
        :return:
        """

        def work(tx):
            cql = 'MATCH (e:Exploit) WHERE e.edb_id = $edb_id ' \
                  'MATCH (af:Asset:Family) WHERE af.cpe23uri = $cpe23uri ' \
                  'MERGE (e)-[r1:Attacks {rid:$rid1,assets:$assets,asset_cnt:$asset_cnt}]->(af) ' \
                  'MERGE (af)-[r2:AttackedBy {rid:$rid2,assets:$assets,asset_cnt:$asset_cnt}]->(e)'
            return tx.run(cql, edb_id=edb_id, cpe23uri=cpe23uri, rid1=f'{edb_id}->{cpe23uri}',
                          rid2=f'{cpe23uri}->{edb_id}', asset_cnt=asset_cnt, assets=assets)

        with self.get_session() as session:
            num = session.write_transaction(work)._summary.counters.relationships_created
            if num:  # if num == 1 then 2 edges created, weird though
                mylogger('db').info(
                    f"Added relationship {cpe23uri}-[AttackedBy]->{edb_id}")
                mylogger('db').info(
                    f"Added relationship {cpe23uri}<-[Attacks]-{edb_id}")
                return 2
            else:
                mylogger('db').info(f"Exist relationship {cpe23uri}<-[r]->{edb_id}")
                return 0

    def get_movie(self):
        def work(tx):
            cql1 = "match (vuln:Vulnerability) return count(vuln) as vuln_count"
            cql2 = "match (asset:Asset) return count(asset) as asset_count"
            result = {"vuln_count": tx.run(cql1).data()[0]["vuln_count"],
                      "asset_count": tx.run(cql2).data()[0]["asset_count"]}
            return result

        with self.get_session() as session:
            return session.read_transaction(work)

    def check_node_index(self):
        """
        Make sure node index exist
        See https://neo4j.com/docs/cypher-manual/current/indexes-for-search-performance/#administration-indexes-types

        :return: None
        """
        # self.get_session().run("CREATE INDEX vuln_index IF NOT EXISTS FOR (n:Vulnerability) ON (n.cve_id)")
        self.get_session().run(
            "CREATE CONSTRAINT vuln_con IF NOT EXISTS FOR (n:Vulnerability) REQUIRE n.cve_id IS UNIQUE")
        mylogger('db').info('Checked vuln_index on cve_id for neo4j')

        # self.get_session().run("CREATE INDEX asset_index IF NOT EXISTS FOR (n:Asset) ON (n.cpe23uri)")
        self.get_session().run("CREATE CONSTRAINT asset_con IF NOT EXISTS FOR (n:Asset) REQUIRE n.cpe23uri IS UNIQUE")
        mylogger('db').info('Checked asset_index on cpe23uri for neo4j')

        # self.get_session().run("CREATE INDEX exploit_index IF NOT EXISTS FOR (n:Exploit) ON (n.edb_id)")
        self.get_session().run("CREATE CONSTRAINT exploit_con IF NOT EXISTS FOR (n:Exploit) REQUIRE n.edb_id IS UNIQUE")
        mylogger('db').info('Checked exploit_index on edb_id for neo4j')

        self.get_session().run("CREATE LOOKUP INDEX node_label_lookup_index IF NOT EXISTS FOR (n) ON EACH labels(n)")
        self.get_session().run("CREATE LOOKUP INDEX rel_type_lookup_index IF NOT EXISTS FOR ()-[r]-() ON EACH type(r)")
        mylogger('db').info('Checked lookup index for neo4j')

    def check_rel_index(self):
        """
        Make sure relationship index exist
        See https://neo4j.com/docs/cypher-manual/current/indexes-for-search-performance/#administration-indexes-types

        :return:
        """
        self.get_session().run("CREATE INDEX rel_has_index IF NOT EXISTS FOR ()-[r:Has]-() ON (r.rid)")
        self.get_session().run("CREATE INDEX rel_affects_index IF NOT EXISTS FOR ()-[r:Affects]-() ON (r.rid)")
        self.get_session().run("CREATE INDEX rel_exploits_index IF NOT EXISTS FOR ()-[r:Exploits]-() ON (r.rid)")
        self.get_session().run(
            "CREATE INDEX rel_exploited_by_index IF NOT EXISTS FOR ()-[r:ExploitedBy]-() ON (r.rid)")
        self.get_session().run("CREATE INDEX rel_parent_of_index IF NOT EXISTS FOR ()-[r:ParentOf]-() ON (r.rid)")
        self.get_session().run("CREATE INDEX rel_child_of_index IF NOT EXISTS FOR ()-[r:ChildOf]-() ON (r.rid)")
        self.get_session().run("CREATE INDEX rel_attacks_index IF NOT EXISTS FOR ()-[r:Attacks]-() ON (r.rid)")
        self.get_session().run("CREATE INDEX rel_attacked_by_index IF NOT EXISTS FOR ()-[r:AttackedBy]-() ON (r.rid)")
        mylogger('db').info('Checked rel_index for neo4j')
        # cql_affects = "CREATE INDEX rel_affects_index IF NOT EXISTS FOR ()-[r:Affects]-() ON (r.rid)"
        # self.get_session().run(cql_affects)
        # cql_affects = "CREATE INDEX rel_affects_index IF NOT EXISTS FOR ()-[r:Affects]-() ON (r.rid)"
        # self.get_session().run(cql_affects)

    def delete_rel(self, cve_id=""):
        # def work(tx):
        #      = tx.run()
        #     # tx.run('match (v:Vulnerability {cve_id:$cve_id})<-[r]-(a) delete r',cve_id=cve_id)
        #
        #     return res

        with self.get_session() as session:
            res = session.run('match (v:Vulnerability {cve_id:$cve_id})-[r]-(a) delete r', cve_id=cve_id)
            mylogger('db').info(f'Deleted all rels for {cve_id}')
            return

    def close_db(self):
        """
        Shut down neo4j driver. Remember to call this before quit

        :return: None
        """
        mylogger('db').info('Shutting down neo4j driver...')
        self.driver.close()


neo = MyNeo()

# @click.command('init-neo')
# @with_appcontext
# def init_neo_command():
#     """get neo4j conn"""
#     get_neo()
#     click.echo('Connected with neo4j.')
#
#
# def init_app(app):
#     # app.teardown_appcontext(close_db)
#     app.cli.add_command(init_neo_command)
if __name__ == "__main__":
    # neo.create_node_index()
    # node = neo.get_node('Asset', cpe23uri='cpe:2.3:a:\@thi.ng\/egf_project:\@thi.ng\/egf:-:*:*:*:*:node.js:*:*').first()
    # print(node)
    # neo.close_db()
    pass
