from db import neo


def work(tx):
    cql = 'MATCH ()-[r:Affects]-() WHERE r.rid IS NULL SET r.rid=r.rid2 REMOVE r.rid2'
    tx.run(cql)


def work1(tx):
    cql = 'MATCH ()-[r:Has]-() WHERE r.rid IS NULL SET r.rid=r.rid1 REMOVE r.rid1'
    tx.run(cql)


if __name__ == "__main__":
    neo.get_session().write_transaction(work1)
