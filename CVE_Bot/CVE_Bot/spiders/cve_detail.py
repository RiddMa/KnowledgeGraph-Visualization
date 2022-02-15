import logging
import re

import pandas as pd
import scrapy
from bs4 import BeautifulSoup

from CVE_Bot.items import CveBotItem, AffectedProduct
from CVE_Bot.utils.csv_parser import cve_all_clean_csv_exist, get_clean_csv_path
from bot_root_dir import get_source_data_dir


class CVEDetailSpider(scrapy.Spider):
    name = 'CVEDetail'
    allowed_domains = ['cvedetails.com']
    item = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item = CveBotItem()
        self.item['affected_products'] = []

    def start_requests(self):
        if not cve_all_clean_csv_exist(get_source_data_dir()):
            logging.error('cve_all_clean.csv does not exist!')
        in_file = get_clean_csv_path()
        # 分块迭代读取文件，每次读入chunk-size行
        csv_iterator = pd.read_csv(in_file, encoding='utf-8', iterator=True, chunksize=1000, header=0, index_col=0)
        for chunk in csv_iterator:
            cve_ids = chunk['Name']
            for cve_id in cve_ids:
                url = 'https://www.cvedetails.com/cve/' + cve_id
                yield scrapy.Request(url=url, callback=self.parse)  # 将url传递给engine

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.body, 'html.parser')

        # get cve_id
        self.item['cve_id'] = soup.select_one('#cvedetails > h1 > a').get_text()

        # get vuln_desc and vuln_dates
        vuln_desc_div = soup.select_one('#cvedetails > div.cvedetailssummary')
        self.item['vuln_desc'] = vuln_desc_div.get_text().split('\t\n')[0].strip('\n\t')
        vuln_desc_dates_raw = vuln_desc_div.select_one('span').get_text().strip('\n').strip('\t')
        vuln_desc_dates = re.findall(r'(\d+-\d+-\d+)', re.sub('\s+', '', str(vuln_desc_dates_raw)))
        self.item['publish_date'] = vuln_desc_dates[0]
        self.item['last_update_date'] = vuln_desc_dates[1]

        # get cvss_score and severity
        table = soup.select_one('#cvssscorestable')
        self.item['cvss_score'] = float(table.select_one('tr:nth-child(1) > td').get_text())
        self.item['cvss_severity'] = calculate_severity(self.item['cvss_score'])

        # get vulnerability types
        confidentiality_impact_text = table.select_one('tr:nth-child(2) > td > span:nth-child(1)').get_text()
        confidentiality_impact_desc = prettify(table.select_one('tr:nth-child(2) > td > span:nth-child(2)').get_text())
        self.item['confidentiality_impact'] = {'text': confidentiality_impact_text, 'desc': confidentiality_impact_desc}
        integrity_impact_text = table.select_one('tr:nth-child(3) > td > span:nth-child(1)').get_text()
        integrity_impact_desc = prettify(table.select_one('tr:nth-child(3) > td > span:nth-child(2)').get_text())
        self.item['integrity_impact'] = {'text': integrity_impact_text, 'desc': integrity_impact_desc}
        availability_impact_text = table.select_one('tr:nth-child(4) > td > span:nth-child(1)').get_text()
        availability_impact_desc = prettify(table.select_one('tr:nth-child(4) > td > span:nth-child(2)').get_text())
        self.item['availability_impact'] = {'text': availability_impact_text, 'desc': availability_impact_desc}
        access_complexity_text = table.select_one('tr:nth-child(5) > td > span:nth-child(1)').get_text()
        access_complexity_desc = prettify(table.select_one('tr:nth-child(5) > td > span:nth-child(2)').get_text())
        self.item['access_complexity'] = {'text': access_complexity_text, 'desc': access_complexity_desc}
        authentication_text = table.select_one('tr:nth-child(6) > td > span:nth-child(1)').get_text()
        authentication_desc = table.select_one('tr:nth-child(6) > td > span:nth-child(2)').get_text()
        self.item['authentication'] = {'text': authentication_text, 'desc': authentication_desc}
        self.item['gained_access'] = table.select_one('tr:nth-child(7) > td > span').get_text()
        self.item['vulnerability_types'] = table.select_one('tr:nth-child(8) > td > span').get_text()

        # get cwe_id
        cwe_id_text = table.select_one('tr:nth-child(9) > td > a').get_text()
        if cwe_id_text != 'CWE id is not defined for this vulnerability':
            self.item['cwe_id'] = int(cwe_id_text)
        else:
            self.item['cwe_id'] = -1

        # get affected products
        affected_products_tr = soup.select('#vulnprodstable > tr')[1:]
        for product in affected_products_tr:
            product_type = product.select_one('td:nth-child(2)').get_text().strip('\n').strip('\t')
            product_vendor = product.select_one('td:nth-child(3) > a').get_text()
            product_name = product.select_one('td:nth-child(4) > a').get_text()
            product_version = product.select_one('td:nth-child(5)').get_text().strip('\n').strip('\t')
            product_object = AffectedProduct(product_type, product_vendor, product_name, product_version)
            self.item['affected_products'].append(product_object)

        # open(self.item['cve_id'] + '.html', 'wb+').write(response.body)
        
        yield self.item


def calculate_severity(content):
    if int(content) == 0:
        severity = 'Information'
    elif int(content) < 4:
        severity = 'Low'
    elif int(content) < 7:
        severity = 'Medium'
    elif int(content) < 9:
        severity = 'High'
    else:
        severity = 'Critical'
    return severity


def prettify(raw: str):
    return raw.strip('(').strip(')').strip(' ').strip('.') + '.'
