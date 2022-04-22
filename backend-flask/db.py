import logging

from flask import g
from neo4j import (GraphDatabase, basic_auth)

import secret

driver = GraphDatabase.driver(secret.neo_driver_url,
                              auth=basic_auth(secret.neo_username, secret.neo_password))


class NEO:
    def __init__(self):
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

    def get_movie(self):
        def work(tx):
            cql1 = "match (vuln:Vulnerability) return count(vuln) as vuln_count"
            cql2 = "match (asset:Asset) return count(asset) as asset_count"
            result = {"vuln_count": tx.run(cql1).data()[0]["vuln_count"],
                      "asset_count": tx.run(cql2).data()[0]["asset_count"]}
            return result

        with self.get_session() as session:
            return session.read_transaction(work)


neo = NEO()


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
