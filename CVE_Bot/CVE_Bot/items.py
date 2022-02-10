# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CveBotItem(scrapy.Item):
    # define the fields for your item here like:
    cve_id = scrapy.Field()
    vuln_desc = scrapy.Field()
    cvss_score = scrapy.Field()

    pass
