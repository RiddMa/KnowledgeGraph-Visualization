import logging
import pymongo
from py2neo import Node, Relationship, Graph
from py2neo.cypher import cypher_escape

import secret


class MG:

    def __init__(self):
        self.client = pymongo.MongoClient(secret.mongo_uri)
        if "cve_bot" not in self.client.list_database_names():
            logging.info('Database "cve_bot" does not exist.')
        self.db = self.client["cve_bot"]
        self.json = self.db["json"]

    def save_json(self, cve_id, content):
        doc = {"cve_id": cve_id, "content": content}
        # doc_id = self.json.insert_one(doc).inserted_id
        self.json.update_one({"cve_id": cve_id}, {"$set": doc}, upsert=True)
        logging.info(cve_id + ".json saved to MongoDB.")

    def get_all_cve(self) -> object:
        cursor = self.json.find({}, {"content": 1, "_id": 0})
        return cursor


mongo = MG()


class NEO:

    def __init__(self):
        self.graph = Graph(secret.neo_uri,
                           name=secret.db_name,
                           auth=(secret.neo_username, secret.neo_password))

    def add_node(self, labels, props):
        node = Node(*labels, **props)
        tx = self.graph.begin()
        tx.create(node)
        tx.commit()
        return node

    def add_relationship(self):
        r = Relationship


neo = NEO()


def find_dict(graph, label, key_value=None, limit=None):
    """ Iterate through a set of labelled nodes, optionally filtering
    by property key/value dictionary
    """
    if not label:
        raise ValueError("Empty label")

    if key_value is None:
        statement = "MATCH (n:%s) RETURN n,labels(n)" % cypher_escape(label)
    else:
        # quote string values
        d = {
            k: "'{}'".format(v) if isinstance(v, str) else v
            for k, v in key_value.items()
        }

        cond = ""
        for prop, value in d.items():
            if not isinstance(value, tuple):
                value = ('=', value)

            if cond == "":
                cond += "n.{prop}{value[0]}{value[1]}".format(
                    prop=prop,
                    value=value,
                )
            else:
                cond += " AND n.{prop}{value[0]}{value[1]}".format(
                    prop=prop,
                    value=value,
                )

        statement = "MATCH (n:%s ) WHERE %s RETURN n,labels(n)" % (
            cypher_escape(label), cond)
    if limit:
        statement += " LIMIT %s" % limit
    response = graph.cypher.post(statement)
    for record in response.content["data"]:
        dehydrated = record[0]
        dehydrated.setdefault("metadata", {})["labels"] = record[1]
        yield graph.hydrate(dehydrated)
    response.close()


def find_dict_one(graph, label, key_value=None):
    """ Find a single node by label and optional property. This method is
    intended to be used with a unique constraint and does not fail if more
    than one matching node is found.
    """
    for node in find_dict(graph, label, key_value, limit=1):
        return node
