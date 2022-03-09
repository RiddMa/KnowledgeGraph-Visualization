# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
import os
import pprint
from urllib.parse import urlparse

import scrapy
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from CVE_Bot.utils.db import MongoInstance
from scrapy.pipelines.files import FilesPipeline


class CveDetailPipeline:

    def __init__(self):
        self.mongo = MongoInstance

    def process_item(self, item, spider):
        spider.logger.info('Processing ' + item['cve_id'])
        MongoInstance.save_json(item['cve_id'], ItemAdapter(item).asdict())
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
        spider.logger.info('process HELLO!!!!!!!!!!!!!')

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
        spider.logger.info('HELLO!!!!!!!!!!!!!')
        print("start process")
        adapter = ItemAdapter(item)
        pprint.pprint(adapter)
        return item


def dump_obj(obj):
    return obj.__dict__
