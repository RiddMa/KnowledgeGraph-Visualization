# import pprint
#
# import scrapy
#
# from CVE_Bot.items import GzFileItem
# from CVE_Bot.pipelines import GzFilePipeline
#
#
# class CpeSpider(scrapy.Spider):
#     name = 'cpe'
#     allowed_domains = ['nvd.nist.gov']
#     start_urls = ['https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml.gz']
#     # start_urls = ['https://nvd.nist.gov/products/cpe']
#     custom_settings = {
#         'ITEM_PIPELINES': {
#             'CVE_Bot.pipelines.CpeFilePipeline': 300,
#             # 'CVE_Bot.pipelines.GzFilePipeline': 300,
#         }
#     }
#
#     def parse(self, response, **kwargs):
#         pass
import requests

from CVE_Bot.utils.gz import un_gz
from bot_root_dir import get_cpe_data_dir


def download_file(url):
    filepath = get_cpe_data_dir().joinpath(url.split("/")[-1])
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response, uncomment if and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return filepath


if __name__ == "__main__":
    cpe_dict_url = "https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml.gz"
    cpe_schema_url = "https://csrc.nist.gov/schema/cpe/2.3/cpe-dictionary_2.3.xsd"
    un_gz(download_file(cpe_dict_url))
    download_file(cpe_schema_url)
