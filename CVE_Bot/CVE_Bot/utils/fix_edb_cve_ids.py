from CVE_Bot.utils.db import mg
import re

if __name__ == "__main__":
    cursor = mg.get_edb_json()
    pattern = '\d+-\d+'
    for doc in cursor:
        edb_id = doc['edb_id']
        li = re.findall(pattern, doc['content']['cve_id'])
        print(li)
        mg.edb_json.update_one({'edb_id': edb_id}, {"$set": {'content.cve_id': li}}, upsert=True)

    mg.edb_json.update_many({}, {'$rename': {'content.cve_id': 'content.cve_ids'}})
