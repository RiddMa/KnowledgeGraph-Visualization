import logging
from pprint import pprint

from CVE_Bot.pipelines import NvdPipeline
from CVE_Bot.utils.db import mg
from custom_logger import mylogger

if __name__ == "__main__":
    pipeline = NvdPipeline()
    cve_map = {}
    cursor = mg.get_nvd_json()
    mylogger.info("Creating map for existing nvd entry.")
    for doc in cursor:
        cve_map[doc['cve_id']] = True
    mylogger.info("Created map for existing nvd entry.")

    cursor = mg.get_nvd_json_src()
    cnt_skip, cnt_done = 0, 0
    mylogger.info("Converting nvd_json_src to nvd_json.")
    for doc in cursor:
        cve_id = doc['content']['result']['CVE_Items'][0]['cve']['CVE_data_meta']['ID']
        if cve_id in cve_map and cve_map[cve_id]:
            mylogger.info('Skipping ' + cve_id)
            cnt_skip += 1
            continue
        entry = pipeline.process_item(doc['content'])
        mg.save_nvd_json(entry['vuln']['cve_id'], entry)
        cnt_done += 1

    mylogger.info('Converted nvd_json_src to nvd_json, ' + str(cnt_done) + ' done, ' + str(cnt_skip) + ' skipped.')

    # doc = mongo.get_nvd_json_src('CVE-2019-13603')
    # entry = NvdPipeline().process_item(doc)
    # print(entry)
