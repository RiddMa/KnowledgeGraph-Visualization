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
import logging
from datetime import datetime
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from lxml import etree

from CVE_Bot.utils.db import mg
from CVE_Bot.utils.gz import un_gz
from bot_root_dir import get_cpe_data_dir
from custom_logger import setup_logger, mylogger


def download_file(url):
    file_path = get_cpe_data_dir().joinpath(url.split("/")[-1])
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response, uncomment if and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    mylogger("cpe").info("Download {fname} complete.".format(fname=file_path))
    return file_path


def parse_cpe_xml(file_path):
    """
    Parse cpe xml, extract cpe-item to MongoDB.

    :param file_path: Path to xml file.
    :return: None
    """
    mylogger('cpe').info(f'Parsing CPE XML {file_path}')
    context = etree.iterparse(file_path, tag='{http://cpe.mitre.org/dictionary/2.0}generator')
    timestamp = 'Undefined'
    for event, element in context:
        if element.tag.endswith('generator'):
            for child in element:
                if child.tag.endswith('timestamp'):
                    timestamp = child.text
    mylogger('cpe').info(f'Timestamp of this file: {timestamp}.')

    context = etree.iterparse(file_path, tag='{http://cpe.mitre.org/dictionary/2.0}cpe-item')
    for event, element in context:
        cpe = {'timestamp': timestamp}
        for child in element:
            tag = child.tag.split('}')[1]
            if tag == 'title':
                cpe['title'] = child.text
            elif tag == 'references':
                cpe['references'] = [{'tag': ref.text, 'href': ref.attrib['href']} for ref in child]
            elif tag == 'cpe23-item':
                cpe['cpe23uri'] = child.attrib['name']
        field_list = cpe['cpe23uri'].split(':')
        # cpe:<cpe_version>:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>
        cpe['field'] = {
            'part': field_list[2],
            'vendor': field_list[3],
            'product': field_list[4],
            'version': field_list[5],
            'update': field_list[6],
            'edition': field_list[7],
            'language': field_list[8],
            'sw_edition': field_list[9],
            'target_sw': field_list[10],
            'target_hw': field_list[11],
            'other': field_list[12]
        }
        mylogger('cpe').info(f'Parsed {cpe["title"]} xml.')
        mg.save_cpe(cpe['cpe23uri'], cpe)
        element.clear()


if __name__ == "__main__":
    cpe_dict_url = "https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml.gz"
    cpe_schema_url = "https://csrc.nist.gov/schema/cpe/2.3/cpe-dictionary_2.3.xsd"
    filepath = un_gz(download_file(cpe_dict_url))
    download_file(cpe_schema_url)
    parse_cpe_xml(file_path=filepath)

    # parse_cpe_xml(
    #     '/mnt/C2000PRO/GitRepos/KnowledgeGraphVisualization-Main/KnowledgeGraph-Visualization/CVE_Bot/source_data/cpe_data/official-cpe-dictionary_v2.3.xml')
    # parse_cpe_xml(
    #     '/mnt/C2000PRO/GitRepos/KnowledgeGraphVisualization-Main/KnowledgeGraph-Visualization/CVE_Bot/source_data/cpe_data/cpe-test.xml')
