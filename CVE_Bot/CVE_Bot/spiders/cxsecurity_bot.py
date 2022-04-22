import asyncio
import html
import json
import logging
import sys
from datetime import datetime

import simplejson

import scrapy
from bs4 import BeautifulSoup

from CVE_Bot.utils.db import mongo
from bot_root_dir import get_log_dir
from custom_logger import setup_logger
from playwright.async_api import async_playwright


async def get_total_page_num():
    async with async_playwright() as p:
        # browser = await p.firefox.launch(headless=False)
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto("https://cxsecurity.com/wlb/1")
        await page.locator('#glowna > center > div > div:nth-child(4) > ul > li:nth-child(13) > a').click()
        total = int(page.url.strip('https://cxsecurity.com/wlb/'))
        await browser.close()
        return total


class CxSecurityBot(scrapy.Spider):
    name = 'CxSecurityBot'
    allowed_domains = ['cxsecurity.com']
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 0.5
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        log_filename = 'cxsecurity-' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.log'
        self.mylogger = setup_logger('CxSecurity', log_filename, level_stdout=logging.INFO)
        self.mylogger.info('Logging to file ' + str(get_log_dir().joinpath(log_filename)))

        self.mylogger.info('Getting total page num with Playwright...')
        self.page_num = asyncio.run(get_total_page_num())
        self.mylogger.info('Total page num: ' + str(self.page_num))

    def start_requests(self):
        indices = [i for i in range(100, self.page_num + 1)]
        for i in indices:
            url = 'https://cxsecurity.com/wlb/' + str(i)
            self.mylogger.info('Start request ' + url)
            yield scrapy.Request(url)
        # yield scrapy.Request('https://cxsecurity.com/issue/WLB-2022040078')

    def parse(self, response, **kwargs):
        delay = self.crawler.engine.downloader.slots["cxsecurity.com"].delay
        concurrency = self.crawler.engine.downloader.slots["cxsecurity.com"].concurrency
        self.mylogger.info("Delay {}, concurrency {} for request {}".format(delay, concurrency, response.request))

        soup = BeautifulSoup(response.body, 'html.parser')
        # parse index pages
        if response.url.startswith('https://cxsecurity.com/wlb/'):
            table = soup.select_one(
                '#glowna > center > div > div:nth-child(5) > table.table.table-striped.table-hover')
            links = [tr.select('td')[1].a['href'] for tr in table.find_all('tr') if tr.select('td') != []]
            for link in links:
                mongo.save_cxsecurity_index(link.strip('https://cxsecurity.com/issue/'), link)
                # self.mylogger.info('Start issue request ' + link)
                # yield scrapy.Request(link)

            # if int(response.url.strip('https://cxsecurity.com/wlb/')) < self.page_num:
            #     url = 'https://cxsecurity.com/wlb/' + str(
            #         int(response.url.strip('https://cxsecurity.com/wlb/')) + 1)
            #     self.mylogger.info('Start next page request ' + url)
            #     yield scrapy.Request(url)

        # parse issue detail pages
        if response.url.startswith('https://cxsecurity.com/issue/'):
            exploit_id = response.url.strip('https://cxsecurity.com/issue/')
            self.mylogger.info('Parsing ' + exploit_id)
            mongo.save_cxsecurity_html(exploit_id, json.dumps(response.text))
            try:
                info = soup.find('div', class_='panel-body')
                exploit = {
                    'exploit_id': exploit_id,
                    'title': soup.select_one('#glowna>center>table>tr>td>div>center>h4>b').text,
                    # get exploit info
                    'date': info.select_one('div>div>div>div>b').text,
                    'credit': info.select_one('div>div>div>div:nth-child(2)>div>b>a').text,
                    'credit_link': info.select_one('div>div>div>div:nth-child(2)>div>b>a')['href'],
                    'risk': info.select_one('div>div>div.col-xs-5.col-md-3>div>b>span').text,
                    'local': info.select_one('div>div>div.col-xs-3.col-md-3>div>b').text,
                    'remote': info.select_one('div>div>div.col-xs-4.col-md-3>div>b').text,
                    'cve_ids': [item.text for item in info.select('div>div.row>div:nth-child(6)>div>b') if
                                item.text != 'N/A'],
                    'cwe_ids': [item.text for item in info.select_one('div>div>div:nth-child(7)>div>b') if
                                item.text != 'N/A' and item.text != ' '],
                    # get exploit code
                    'code': json.dumps(soup.find('div', class_="well well-sm premex").text)
                }
                mongo.save_cxsecurity_json(exploit_id, exploit)
            except BaseException as err:
                self.mylogger.error(exploit_id + ': ' + str(err))
            finally:
                pass

        if response.url.startswith('https://cxsecurity.com/ids/block/'):
            self.mylogger.error('!! Blocked !!')
