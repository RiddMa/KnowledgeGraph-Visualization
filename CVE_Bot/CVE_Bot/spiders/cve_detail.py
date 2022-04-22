import re

import pandas as pd
import scrapy
from bs4 import BeautifulSoup

from CVE_Bot.items import CveBotItem
from CVE_Bot.utils.csv_parser import cve_all_clean_csv_exist, get_cve_all_clean_csv_path
from CVE_Bot.utils.db import mongo
from bot_root_dir import get_source_data_dir


class CVEDetailSpider(scrapy.Spider):
    name = 'CVEDetail'
    allowed_domains = ['cvedetails.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'CVE_Bot.pipelines.CveDetailPipeline': 300,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.mongo = MongoInstance

    def start_requests(self):
        if not cve_all_clean_csv_exist(get_source_data_dir()):
            self.logger.error('cve_all_clean.csv does not exist!')

        # 分块迭代读取文件，每次读入chunk-size行
        in_file = get_cve_all_clean_csv_path()
        df = pd.read_csv(in_file, encoding='utf-8', iterator=True, chunksize=1000, header=0)
        for chunk in df:
            cve_ids = chunk['Name']
            for cve_id in cve_ids:
                url = 'https://www.cvedetails.com/cve/' + cve_id
                self.logger.info('Start request ' + url)
                yield scrapy.Request(url=url, callback=self.parse)  # 将url传递给engine

    def parse(self, response, **kwargs):
        item = CveBotItem()
        soup = BeautifulSoup(response.body, 'html.parser')

        # get cve_id
        cve_id = ''
        try:
            cve_id = soup.select_one('#cvedetails > h1 > a').get_text()
        except AttributeError as e:
            self.logger.error('cve_id not found in page!' + repr(e))
        finally:
            item['cve_id'] = cve_id
            self.logger.info('Parsing ' + cve_id)
        # # save html to disk
        # html_out_path = get_cve_data_dir().joinpath(item['cve_id'] + '.html')
        # try:
        #     open(html_out_path, 'wb+').write(response.body)
        # except Exception:
        #     self.logger.error('Save html to disk failed!')
        # finally:
        #     pass
        try:
            mongo.save_cvedetails_html(item['cve_id'], repr(response.body))
        except Exception:
            self.logger.error('Save html to Mongo failed!')
        finally:
            pass

        # get vuln_desc and vuln_dates
        vuln_desc = ''
        vuln_desc_dates = ['', '']
        try:
            vuln_desc_div = soup.select_one('#cvedetails > div.cvedetailssummary')
            vuln_desc = vuln_desc_div.get_text().split('\t\n')[0].strip('\n\t')
            vuln_desc_dates_raw = vuln_desc_div.select_one('span').get_text().strip('\n').strip('\t')
            vuln_desc_dates = re.findall(r'(\d+-\d+-\d+)', re.sub('\s+', '', str(vuln_desc_dates_raw)))
        except Exception:
            pass
        finally:
            item['vuln_desc'] = vuln_desc
            item['publish_date'] = vuln_desc_dates[0]
            item['last_update_date'] = vuln_desc_dates[1]

        # get cvss_score and severity
        cvss_score = -1
        cvss_severity = ''
        try:
            table = soup.select_one('#cvssscorestable')
            cvss_score = float(table.select_one('tr:nth-child(1) > td').get_text())
            cvss_severity = calculate_severity(cvss_score)
        except Exception:
            pass
        finally:
            item['cvss_score'] = cvss_score
            item['cvss_severity'] = cvss_severity

        # get vulnerability types
        confidentiality_impact_text = confidentiality_impact_desc = ''
        try:
            confidentiality_impact_div = table.select_one('tr:nth-child(2) > td')
            confidentiality_impact_text = confidentiality_impact_div.select_one('span:nth-child(1)').get_text()
            confidentiality_impact_desc = prettify(
                confidentiality_impact_div.select_one('span:nth-child(2)').get_text())
        except Exception:
            pass
        finally:
            item['confidentiality_impact'] = {'text': confidentiality_impact_text, 'desc': confidentiality_impact_desc}

        integrity_impact_text = integrity_impact_desc = ''
        try:
            integrity_impact_div = table.select_one('tr:nth-child(3) > td')
            integrity_impact_text = integrity_impact_div.select_one('span:nth-child(1)').get_text()
            integrity_impact_desc = prettify(integrity_impact_div.select_one('span:nth-child(2)').get_text())
        except Exception:
            pass
        finally:
            item['integrity_impact'] = {'text': integrity_impact_text, 'desc': integrity_impact_desc}

        availability_impact_text = availability_impact_desc = ''
        try:
            availability_impact_div = table.select_one('tr:nth-child(4) > td')
            availability_impact_text = availability_impact_div.select_one('span:nth-child(1)').get_text()
            availability_impact_desc = prettify(availability_impact_div.select_one('span:nth-child(2)').get_text())
        except Exception:
            pass
        finally:
            item['availability_impact'] = {'text': availability_impact_text, 'desc': availability_impact_desc}

        access_complexity_text = access_complexity_desc = ''
        try:
            access_complexity_div = table.select_one('tr:nth-child(5) > td')
            access_complexity_text = access_complexity_div.select_one('span:nth-child(1)').get_text()
            access_complexity_desc = prettify(access_complexity_div.select_one('span:nth-child(2)').get_text())
        except Exception:
            pass
        finally:
            item['access_complexity'] = {'text': access_complexity_text, 'desc': access_complexity_desc}

        authentication_text = authentication_desc = ''
        try:
            authentication_div = table.select_one('tr:nth-child(6) > td')
            authentication_text = authentication_div.select_one('span:nth-child(1)').get_text()
            authentication_desc = authentication_div.select_one('span:nth-child(2)').get_text()
        except Exception:
            pass
        finally:
            item['authentication'] = {'text': authentication_text, 'desc': authentication_desc}

        gained_access = ''
        try:
            gained_access = table.select_one('tr:nth-child(7) > td > span').get_text()
        except Exception:
            pass
        finally:
            item['gained_access'] = gained_access

        vulnerability_types = ''
        try:
            vulnerability_types = table.select_one('tr:nth-child(8) > td > span').get_text()
        except Exception:
            pass
        finally:
            item['vulnerability_types'] = vulnerability_types

        # get cwe_id
        cwe_id = -1
        try:
            cwe_id = int(table.select_one('tr:nth-child(9) > td > a').get_text())
        except Exception:
            pass
        finally:
            item['cwe_id'] = cwe_id

        # get affected products
        item['affected_products'] = []
        try:
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
        except Exception:
            pass
        finally:
            pass

        # get references
        references = []
        try:
            refs = soup.select('#vulnrefstable > tr')
            for ref in refs:
                ref_link = ''
                try:
                    ref_link = ref.select_one('td > a')['href']
                    references.append(ref_link)
                except Exception:
                    pass
                finally:
                    pass
        except Exception:
            pass
        finally:
            item['references'] = references

        yield item


def calculate_severity(content):
    severity = ''
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
