# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CveBotItem(scrapy.Item):
    # define the fields for your item here like:
    cve_id = scrapy.Field()
    publish_date = scrapy.Field()
    last_update_date = scrapy.Field()
    vuln_desc = scrapy.Field()
    cvss_score = scrapy.Field()
    cvss_severity = scrapy.Field()
    confidentiality_impact = scrapy.Field()
    integrity_impact = scrapy.Field()
    availability_impact = scrapy.Field()
    access_complexity = scrapy.Field()
    authentication = scrapy.Field()
    gained_access = scrapy.Field()
    vulnerability_types = scrapy.Field()
    cwe_id = scrapy.Field()
    affected_products = scrapy.Field()
    references = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    pass


# class AffectedProduct:
#     type = ''
#     vendor = ''
#     name = ''
#     version = ''
#
#     def __init__(self, _type, _vendor, _name, _version):
#         self.type = _type
#         self.vendor = _vendor
#         self.name = _name
#         self.version = _version
