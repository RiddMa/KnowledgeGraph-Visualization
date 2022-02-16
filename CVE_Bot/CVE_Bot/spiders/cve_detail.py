import logging
import re

import pandas as pd
import scrapy
from bs4 import BeautifulSoup

from CVE_Bot.items import CveBotItem
from CVE_Bot.utils.csv_parser import cve_all_clean_csv_exist, get_cve_all_clean_csv_path
from bot_root_dir import get_source_data_dir, get_cve_data_dir


class CVEDetailSpider(scrapy.Spider):
    name = 'CVEDetail'
    allowed_domains = ['cvedetails.com']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self):
        if not cve_all_clean_csv_exist(get_source_data_dir()):
            logging.error('cve_all_clean.csv does not exist!')
        in_file = get_cve_all_clean_csv_path()
        # 分块迭代读取文件，每次读入chunk-size行
        df = pd.read_csv(in_file, encoding='utf-8', iterator=True, chunksize=1000, header=0)
        for chunk in df:
            cve_ids = chunk['Name']
            for cve_id in cve_ids:
                url = 'https://www.cvedetails.com/cve/' + cve_id
                logging.info('Start request ' + url)
                yield scrapy.Request(url=url, callback=self.parse)  # 将url传递给engine
        # yield scrapy.Request(url='https://www.cvedetails.com/cve/CVE-2010-1219', callback=self.parse)

    def parse(self, response, **kwargs):
        item = CveBotItem()
        soup = BeautifulSoup(response.body, 'html.parser')

        # get cve_id
        cve_id = soup.select_one('#cvedetails > h1 > a').get_text()
        item['cve_id'] = cve_id
        logging.info('Parsing ' + cve_id)

        # save html to disk
        html_out_path = get_cve_data_dir().joinpath(item['cve_id'] + '.html')
        open(html_out_path, 'wb+').write(response.body)

        # get vuln_desc and vuln_dates
        vuln_desc_div = soup.select_one('#cvedetails > div.cvedetailssummary')
        item['vuln_desc'] = vuln_desc_div.get_text().split('\t\n')[0].strip('\n\t')
        vuln_desc_dates_raw = vuln_desc_div.select_one('span').get_text().strip('\n').strip('\t')
        vuln_desc_dates = re.findall(r'(\d+-\d+-\d+)', re.sub('\s+', '', str(vuln_desc_dates_raw)))
        if len(vuln_desc_dates) > 0:
            item['publish_date'] = vuln_desc_dates[0]
        if len(vuln_desc_dates) > 1:
            item['last_update_date'] = vuln_desc_dates[1]

        # get cvss_score and severity
        cvss_score = -1
        cvss_severity = ''
        table = soup.select_one('#cvssscorestable')
        if table.select_one('tr:nth-child(1) > td') is not None:
            cvss_score = float(table.select_one('tr:nth-child(1) > td').get_text())
            cvss_severity = calculate_severity(cvss_score)
        item['cvss_score'] = cvss_score
        item['cvss_severity'] = cvss_severity

        # get vulnerability types
        confidentiality_impact_text = confidentiality_impact_desc = ''
        confidentiality_impact_div = table.select_one('tr:nth-child(2) > td')
        if confidentiality_impact_div is not None:
            confidentiality_impact_text = confidentiality_impact_div.select_one('span:nth-child(1)').get_text()
            confidentiality_impact_desc = prettify(
                confidentiality_impact_div.select_one('span:nth-child(2)').get_text())
        item['confidentiality_impact'] = {'text': confidentiality_impact_text, 'desc': confidentiality_impact_desc}

        integrity_impact_text = integrity_impact_desc = ''
        integrity_impact_div = table.select_one('tr:nth-child(3) > td')
        if integrity_impact_div is not None:
            integrity_impact_text = integrity_impact_div.select_one('span:nth-child(1)').get_text()
            integrity_impact_desc = prettify(integrity_impact_div.select_one('span:nth-child(2)').get_text())
        item['integrity_impact'] = {'text': integrity_impact_text, 'desc': integrity_impact_desc}

        availability_impact_text = availability_impact_desc = ''
        availability_impact_div = table.select_one('tr:nth-child(4) > td')
        if availability_impact_div is not None:
            availability_impact_text = availability_impact_div.select_one('span:nth-child(1)').get_text()
            availability_impact_desc = prettify(availability_impact_div.select_one('span:nth-child(2)').get_text())
        item['availability_impact'] = {'text': availability_impact_text, 'desc': availability_impact_desc}

        access_complexity_text = access_complexity_desc = ''
        access_complexity_div = table.select_one('tr:nth-child(5) > td')
        if access_complexity_div is not None:
            access_complexity_text = access_complexity_div.select_one('span:nth-child(1)').get_text()
            access_complexity_desc = prettify(access_complexity_div.select_one('span:nth-child(2)').get_text())
        item['access_complexity'] = {'text': access_complexity_text, 'desc': access_complexity_desc}

        authentication_text = authentication_desc = ''
        authentication_div = table.select_one('tr:nth-child(6) > td')
        if authentication_div is not None:
            authentication_text = authentication_div.select_one('span:nth-child(1)').get_text()
            authentication_desc = authentication_div.select_one('span:nth-child(2)').get_text()
        item['authentication'] = {'text': authentication_text, 'desc': authentication_desc}

        gained_access = ''
        gained_access_div = table.select_one('tr:nth-child(7) > td > span')
        if gained_access_div is not None:
            gained_access = gained_access_div.get_text()
        item['gained_access'] = gained_access

        vulnerability_types = ''
        vulnerability_types_div = table.select_one('tr:nth-child(8) > td > span')
        if vulnerability_types_div is not None:
            vulnerability_types = vulnerability_types_div.get_text()
        item['vulnerability_types'] = vulnerability_types

        # get cwe_id
        cwe_id_div = table.select_one('tr:nth-child(9) > td > a')
        if cwe_id_div is None:
            item['cwe_id'] = -1
        else:
            item['cwe_id'] = int(cwe_id_div.get_text())

        # get affected products
        item['affected_products'] = []
        err_div = soup.select_one('#vulnprodstable > tr:nth-child(2) > td > div')
        if err_div is not None and err_div.has_attr('class') and err_div['class'][0] == 'errormsg':
            yield item
        else:
            affected_products_tr = soup.select('#vulnprodstable > tr')[1:]
            for product in affected_products_tr:
                product_type = product.select_one('td:nth-child(2)').get_text().strip('\n').strip('\t')
                product_vendor = product.select_one('td:nth-child(3) > a').get_text()
                product_name = product.select_one('td:nth-child(4) > a').get_text()
                product_version = product.select_one('td:nth-child(5)').get_text().strip('\n').strip('\t')
                product_object = {'type': product_type,
                                  'vendor': product_vendor,
                                  'name': product_name,
                                  'version': product_version}
                item['affected_products'].append(product_object)
            yield item


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
