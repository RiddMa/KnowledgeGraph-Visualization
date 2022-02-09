import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['cvedetails.com/']
    start_urls = ['http://example.com/']

    def parse(self, response):
        pass
