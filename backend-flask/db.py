import logging
from uuid import uuid4
import pymongo as pymongo
from flask import g
from neo4j import (GraphDatabase, basic_auth)
import pymongo
from py2neo import Node, Relationship, Graph
from py2neo.cypher import cypher_escape
import secret

driver = GraphDatabase.driver(secret.neo_driver_url,
                              auth=basic_auth(secret.neo_username, secret.neo_password))


class MyMongo:

    def __init__(self):
        self.client = pymongo.MongoClient(secret.mongo_uri)
        if "cve_bot" not in self.client.list_database_names():
            logging.info('Database "cve_bot" does not exist.')
        self.db = self.client["cve_bot"]
        self.json = self.db["json"]
        self.nvd_json_src = self.db['nvd_json_src']
        self.nvd_json = self.db['nvd_json']
        self.edb_html = self.db['edb_html']
        self.edb_json = self.db['edb_json']


    def save_json(self, cve_id, content):
        doc = {"cve_id": cve_id, "content": content}
        # doc_id = self.json.insert_one(doc).inserted_id
        self.json.update_one({"cve_id": cve_id}, {"$set": doc}, upsert=True)
        logging.info(cve_id + ".json saved to MongoDB.")

    def get_all_cve(self) -> object:
        cursor = self.json.find({}, {"content": 1, "_id": 0})
        return cursor

    def get_nvd(self, cve_id=None):
        if cve_id is None:
            cursor = self.nvd_json.find({}, {"content": 1, "_id": 0})
            return cursor
        else:
            pass


mg = MyMongo()


class MyNeo:
    def __init__(self):
        # for py2neo
        self.graph = Graph(secret.neo_uri,
                           name=secret.db_name,
                           auth=(secret.neo_username, secret.neo_password))
        # for neo4j
        self.driver = GraphDatabase.driver(secret.neo_driver_url,
                                           auth=basic_auth(secret.neo_username, secret.neo_password))
        logging.info("NEO created driver")
        self.session = self.driver.session(database=secret.neo_db)
        logging.info("NEO created session")
        self.session.run("match (n) return n limit 1")
        logging.info("NEO run init query")

    def get_session(self):
        if self.session is None:
            self.session = self.driver.session(database=secret.neo_db)
            logging.info("NEO created session")
        return self.session

    def add_node(self, labels, props):
        props['eid'] = str(uuid4())  # add unique identification for entity
        node = Node(*labels, **props)
        tx = self.graph.begin()
        tx.create(node)
        tx.commit()
        return node

    def get_movie(self):
        def work(tx):
            cql1 = "match (vuln:Vulnerability) return count(vuln) as vuln_count"
            cql2 = "match (asset:Asset) return count(asset) as asset_count"
            result = {"vuln_count": tx.run(cql1).data()[0]["vuln_count"],
                      "asset_count": tx.run(cql2).data()[0]["asset_count"]}
            return result

        with self.get_session() as session:
            return session.read_transaction(work)


neo = MyNeo()


def get_neo():
    if 'neo_driver' not in g:
        g.neo_driver = driver
        print("got driver")
    if 'neo' not in g:
        g.neo = g.neo_driver.session(database=secret.neo_db)
        print("created session")
    return g.neo


def close_neo():
    pass

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
