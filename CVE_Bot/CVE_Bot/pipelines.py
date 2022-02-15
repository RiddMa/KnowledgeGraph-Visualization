# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter

from bot_root_dir import get_cve_data_dir


class CveBotPipeline:
    def process_item(self, item, spider):
        spider.logger.info('Processing ' + item['cve_id'])
        # dump json string
        with open(get_cve_data_dir().joinpath(item['cve_id'] + '.json'), 'w+') as f:
            # json.dump(item, f, indent=4, sort_keys=False, default=dump_obj)
            json.dump(ItemAdapter(item).asdict(), f, indent=4, sort_keys=False, default=dump_obj)
        # # dump cve item as .pkl pickle file
        # with open(get_cve_data_dir().joinpath(item['cve_id'] + '.pkl'), 'wb+') as f:
        #     pickle.dump(item, f)
        return item


def dump_obj(obj):
    return obj.__dict__
