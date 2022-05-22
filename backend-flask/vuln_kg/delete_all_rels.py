from db import mg, neo

if __name__ == "__main__":
    cursor = mg.get_nvd()
    for doc in cursor:
        cve_id = doc['content']['vuln']['cve_id']
        neo.delete_rel(cve_id)

