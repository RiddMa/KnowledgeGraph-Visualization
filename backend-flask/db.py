import logging
from uuid import uuid4
import pymongo as pymongo
from flask import g
from neo4j import (GraphDatabase, basic_auth)
import pymongo
from py2neo import Node, Relationship, Graph, NodeMatcher
from py2neo.cypher import cypher_escape
import secret
from logger_factory import mylogger

driver = GraphDatabase.driver(secret.neo_driver_url,
                              auth=basic_auth(secret.neo_username, secret.neo_password))


class MyMongo:

    def __init__(self):
        self.client = pymongo.MongoClient(secret.mongo_uri)
        if "cve_bot" not in self.client.list_database_names():
            mylogger('db').info('Database "cve_bot" does not exist.')
        self.db = self.client["cve_bot"]
        self.json = self.db["json"]
        self.nvd_json_src = self.db['nvd_json_src']
        self.nvd_json = self.db['nvd_json']
        self.edb_html = self.db['edb_html']
        self.edb_json = self.db['edb_json']
        self.cpe = self.db['cpe']

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

    def add_relationship(self, start, type_, end, props):
        rel = Relationship(start, type_, end, props)
        tx = self.graph.begin()
        tx.create(rel)
        tx.commit()
        mylogger('db').info(f"Relationship {start}--{type_}->{end} added to {tx.graph.name} neo4j database")

    def get_movie(self):
        def work(tx):
            cql1 = "match (vuln:Vulnerability) return count(vuln) as vuln_count"
            cql2 = "match (asset:Asset) return count(asset) as asset_count"
            result = {"vuln_count": tx.run(cql1).data()[0]["vuln_count"],
                      "asset_count": tx.run(cql2).data()[0]["asset_count"]}
            return result

        with self.get_session() as session:
            return session.read_transaction(work)

    def create_node_index(self):
        """
        See https://neo4j.com/docs/cypher-manual/current/indexes-for-search-performance/#administration-indexes-types

        :return: None
        """
        cql_vuln = "CREATE INDEX vuln_index IF NOT EXISTS FOR (n:Vulnerability) ON (n.cve_id)"
        self.get_session().run(cql_vuln)
        mylogger('db').info('Created vuln_index on cve_id for neo4j')
        cql_asset = "CREATE INDEX asset_index IF NOT EXISTS FOR (n:Asset) ON (n.cpe23uri)"
        self.get_session().run(cql_asset)
        mylogger('db').info('Created asset_index on cpe23uri for neo4j')
        cql_exploit = "CREATE INDEX exploit_index IF NOT EXISTS FOR (n:Exploit) ON (n.edb_id)"
        self.get_session().run(cql_exploit)
        mylogger('db').info('Created exploit_index on edb_id for neo4j')

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
    node = neo.get_node('Asset', cpe23uri='cpe:2.3:a:\@thi.ng\/egf_project:\@thi.ng\/egf:-:*:*:*:*:node.js:*:*').first()
    print(node)
    neo.close_db()
