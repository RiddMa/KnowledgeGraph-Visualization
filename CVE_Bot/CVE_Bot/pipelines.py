# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
import logging
import os
import pprint
from urllib.parse import urlparse

import scrapy
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline

from CVE_Bot.utils.db import mongo


# import cve_searchsploit as cs

# @Misc{cve_searchsploit,
#   author       = {Andrea Fioraldi},
#   howpublished = {GitHub},
#   month        = jun,
#   title        = {{CVE SearchSploit}},
#   year         = {2017},
#   url          = {https://github.com/andreafioraldi/cve_searchsploit},
# }


class CveDetailPipeline:

    def __init__(self):
        self.mongo = mongo

    def process_item(self, item, spider):
        spider.mylogger.info('Processing ' + item['cve_id'])
        mongo.save_cvedetails_json(item['cve_id'], ItemAdapter(item).asdict())
        # # dump json string
        # with open(get_cve_data_dir().joinpath(item['cve_id'] + '.json'), 'w+') as f:
        #     # json.dump(item, f, indent=4, sort_keys=False, default=dump_obj)
        #     json.dump(ItemAdapter(item).asdict(), f, indent=4, sort_keys=False, default=dump_obj)
        return item


class GzFilePipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        return 'files/' + os.path.basename(urlparse(request.url).path)

    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        for file_url in adapter['file_urls']:
            yield scrapy.Request(file_url)

    def process_item(self, item, spider):
        spider.mylogger.info('process HELLO!!!!!!!!!!!!!')

    def item_completed(self, results, item, info):
        print("complete HELLO!!!!!!!!!!!!!!!!!!!!")
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            raise DropItem("Item contains no files")
        adapter = ItemAdapter(item)
        adapter['file_paths'] = file_paths
        return item


class CpeFilePipeline:

    def process_item(self, item, spider):
        spider.mylogger.info('HELLO!!!!!!!!!!!!!')
        print("start process")
        adapter = ItemAdapter(item)
        pprint.pprint(adapter)
        return item


class NvdPipeline:
    def process_item(self, item):
        logging.getLogger('Nvd').info(
            'NvdPipeline processing item ' + item['result']['CVE_Items'][0]['cve']['CVE_data_meta'][
                'ID'] + ' from MongoDB......')
        entry = {'version': 'nvd_v1', 'timestamp': item['result']['CVE_data_timestamp'], 'vuln': None, 'assets': [],
                 'exploit': None}
        item = item['result']['CVE_Items'][0]  # NOTE THIS!!!
        # on converting cvss scores:
        # https://security.stackexchange.com/questions/127335/how-to-convert-risk-scores-cvssv1-cvssv2-cvssv3-owasp-risk-severity
        try:
            cwe_id = item['cve']['problemtype']['problemtype_data'][0]['description'][0]['value']
        except BaseException as err:
            cwe_id = None
            logging.getLogger('Nvd').error(item['cve']['CVE_data_meta']['ID'] + ':cwe_id_error: ' + str(err))
        try:
            entry['vuln'] = {
                'cve_id': item['cve']['CVE_data_meta']['ID'],
                'cwe_id': cwe_id,
                'desc': item['cve']['description']['description_data'][0]['value'],
                'impact': {
                    'baseMetricV3': item['impact']['baseMetricV3'] if 'baseMetricV3' in item['impact'] else None,
                    'baseMetricV2': item['impact']['baseMetricV2'] if 'baseMetricV2' in item['impact'] else None
                },
                'references': item['cve']['references']['reference_data'],
                'publish_date': item['publishedDate'],
                'last_update_date': item['lastModifiedDate'],
            }
            entry['assets'] = item['configurations']['nodes']
        except BaseException as err:
            logging.getLogger('Nvd').error(item['cve']['CVE_data_meta']['ID'] + ': ' + str(err))

        return entry


# class EdbPipeline:
#     def process_item(self):
#         cs.update_db()

class CxSecurityPipeline:
    def process_item(self, item):
        logging.getLogger('CxSecurity').info('CxSecurityPipeline processing item ')


def dump_obj(obj):
    return obj.__dict__
