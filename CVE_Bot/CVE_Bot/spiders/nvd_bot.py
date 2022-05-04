import logging

import pandas as pd
import scrapy

from CVE_Bot.items import NvdItem
from CVE_Bot.utils.csv_parser import cve_all_clean_csv_exist, get_cve_all_clean_csv_path
from CVE_Bot.utils.db import mg
from bot_root_dir import get_source_data_dir
from nvd_api_key import api_key


class NvdBot(scrapy.Spider):
    name = 'NvdBot'
    allowed_domains = ['nvd.nist.gov']
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         'CVE_Bot.pipelines.NvdPipeline': 300,
    #     }
    # }

    def start_requests(self):
        if not cve_all_clean_csv_exist(get_source_data_dir()):
            self.logger.error('cve_all_clean.csv does not exist!')
            return None
        # 分块迭代读取文件，每次读入chunk-size行
        in_file = get_cve_all_clean_csv_path()
        df = pd.read_csv(in_file, encoding='utf-8', iterator=True, chunksize=1000, header=0,nrows=3)
        for chunk in df:
            cve_ids = chunk['Name']
            for cve_id in cve_ids:
                url = 'https://services.nvd.nist.gov/rest/json/cve/1.0/' + cve_id + '?apiKey=' + api_key
                self.logger.info('Start request ' + url)
                yield scrapy.Request(url=url, callback=self.parse)  # 将url传递给engine

    def parse(self, response, **kwargs):
        res_json = response.json()
        if "result" not in res_json:
            logging.warning('Result is empty!')
            return None

        item = NvdItem()
        # get cve_id
        item['cve_id'] = res_json["result"]["CVE_Items"][0]['cve']['CVE_data_meta']['ID']

        # noinspection PyBroadException
        try:
            mg.save_nvd_json_src(item['cve_id'], res_json)
        except BaseException:
            self.logger.error('Save nvd_json_src to Mongo failed!')
        finally:
            pass
