import scrapy

from CVE_Bot.items import CveBotItem
from bot_root_dir import get_source_data_dir


def simplify_description(description):
    description = ''.join(description)
    description = re.sub('\t', '', str(description))
    description = re.sub('\n', ' ', str(description))
    return description


class CVEDetailSpider(scrapy.Spider):
    name = 'CVEDetail'
    allowed_domains = ['cvedetails.com']
    start_urls = []

    def __init__(self, **kwargs):
        """初始化方法"""
        super().__init__(**kwargs)
        self.start_urls.append('https://www.cvedetails.com/cve/CVE-1999-0001')

    def parse(self, response):
        filename = 'CVE-1999-0001.html'
        # open(get_source_data_dir().joinpath(filename), 'wb+').write(response.body)
        CveBotItem.cve_id = 'CVE-1999-0001'
        vuln_desc = simplify_description(response.xpath('//*[@id="cvedetails"]/div[1]/text()').extract())

        # cvss_score = response.xpath('//*[@id="cvssscorestable"]/tbody/tr[1]/td/div').extract()
        cvss_score = response.xpath("//table[@id='cvssscorestable']/tr/td/div/text()").extract_first()
        print(vuln_desc, cvss_score)
        pass

    # def cve_parse(self, response):
    #     basic_url = 'https://www.cvedetails.com/'
    #     trs = response.xpath("//div[@id='searchresults']/table[@id='vulnslisttable']/tr[@class='srrowns']")
    #     for tr in trs:
    #         try:
    #             link = tr.xpath("td")[1].xpath("a/@href").extract_first()
    #             if link is not None:
    #                 yield response.follow(basic_url + link, self.vul_parse)
    #         except:
    #             print("link %s scrap fails", str(response.url))
    #
    # def vul_parse(self, response):
    #     vendors = []
    #     affected_products = []
    #     link = response.url
    #     # part for severity
    #     severity_score = response.xpath("//table[@id='cvssscorestable']/tr/td/div/text()").extract_first()
    #     severity = self.handle_severity(severity_score)
    #
    #     # part for CVE
    #     CVE = response.xpath("//td[@id='cvedetails']/h1/a/text()").extract_first()
    #     # part for description
    #     raw_description = response.xpath("//td[@id='cvedetails']/div/text()").extract()
    #     description = self.simplify_description(raw_description)
    #     # part for publish date and modify date
    #     Date = response.xpath("//td[@id='cvedetails']/div[@class='cvedetailssummary']/span/text()").extract_first()
    #     publish_date = re.findall(r'(\d+-\d+-\d+)', re.sub('\s+', '', str(Date)))[0]
    #     last_update_date = re.findall(r'(\d+-\d+-\d+)', re.sub('\s+', '', str(Date)))[1]
    #     # part for products and vendors
    #     parse_products = response.xpath("//table[@id='vulnprodstable']/tr")[1:]
    #     for parse_product in parse_products:
    #         vendor = parse_product.xpath("td/a")[0].css("::text").extract_first()
    #         vendors.append(vendor + ',') if (vendor + ',') not in vendors else None
    #         affected_product = parse_product.xpath("td/a")[1].css("::text").extract_first()
    #         if affected_product[0] == '[':
    #             affected_product = parse_product.xpath("td/a/@title").extract()[1].split()[-1]
    #         affected_version = parse_product.xpath("td")[4].css("::text").extract_first()
    #         update = parse_product.xpath("td")[5].css("::text").extract_first()
    #         edition = parse_product.xpath("td")[6].css("::text").extract_first()
    #         if update:
    #             affected_version = affected_version + update
    #         if edition:
    #             affected_version = affected_version + edition
    #         affected_version = re.sub("~", '', affected_version)
    #         if str(affected_product) not in affected_products:
    #             if len(affected_products) == 0:
    #                 affected_products.append(str(affected_product))
    #                 affected_products.append('(')
    #             else:
    #                 if affected_products[-1][-1] == ',':
    #                     affected_products[-1] = affected_products[-1][:-1]
    #                 affected_products.append('),')
    #                 affected_products.append(str(affected_product))
    #                 affected_products.append('(')
    #             affected_products.append(affected_version + ',')
    #         else:
    #             affected_products.append(affected_version + ',')
    #     additional_vendors = response.xpath("//div[@id='addvendsuppdata']/table/tr/td/a/text()").extract()
    #     if additional_vendors:
    #         for additional_vendor in additional_vendors:
    #             vendors.append(additional_vendor + ',')
    #     vendors = self.sub_blank(vendors)
    #     affected_products = self.formatting(self.sub_blank(affected_products)) + ')'
    #
    #     yield {
    #         'title': self.formatting(CVE),
    #         'url': self.formatting(link),
    #         'severity': self.formatting(severity),
    #         'cve': self.formatting(CVE),
    #         'said': self.formatting(CVE),
    #         'publishedDate': self.formatting(publish_date),
    #         'modifiedDate': self.formatting(last_update_date),
    #         'vendor': self.formatting(vendors),
    #         'affectedProducts': self.formatting(affected_products),
    #         'description': self.formatting(description),
    #         'workaround': None,
    #         'solution': None
    #     }
    #
    # def sub_blank(self, contents):
    #     content = ''.join(contents)
    #     content = re.sub('\s+', '', content)
    #     content = re.sub('\t', '', content)
    #     content = re.sub('\n', '', content)
    #     return content
    #
    # def handle_severity(self, content):
    #     if int(content[0]) == 0:
    #         severity = 'Information'
    #     elif int(content[0]) < 4:
    #         severity = 'Low'
    #     elif int(content[0]) < 7:
    #         severity = 'Medium'
    #     elif int(content[0]) < 9:
    #         severity = 'High'
    #     else:
    #         severity = 'Critical'
    #     return severity
    #
    # def simplify_description(self, description):
    #     description = ''.join(description)
    #     description = re.sub('\t', '', str(description))
    #     description = re.sub('\n', ' ', str(description))
    #     return description
    #
    # def formatting(self, content):
    #     if isinstance(content, list):
    #         content = ''.join(content).strip()
    #     else:
    #         content = content.strip()
    #     if content[-1] is ',':
    #         content = content[:-1]
    #     return content
