from pprint import pprint

from CVE_Bot.pipelines import NvdPipeline
from CVE_Bot.utils.db import mongo

if __name__ == "__main__":
    item = mongo.get_nvd_json_src('CVE-2021-44228')
    pprint(item)
    res = NvdPipeline().process_item(item)
    print('\n\n\n\n')
    pprint(res)
