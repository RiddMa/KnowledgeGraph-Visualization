# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter

from CVE_Bot.utils.db import MongoInstance


class CveBotPipeline:
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


def dump_obj(obj):
    return obj.__dict__
