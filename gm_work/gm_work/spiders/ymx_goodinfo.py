# -*- coding: utf-8 -*-
import re

import scrapy
from gm_work.items import AmazonItem

class YmxInfoSpider(scrapy.Spider):
    name = 'ymx_goodinfo'
    allowed_domains = ['amazon.co.uk']
    base_host = 'https://www.amazon.co.uk'
    host = 'https://www.amazon.co.uk/s?me=%s'
    def start_requests(self):
        # with open(r'C:\Users\admin\Desktop/amazon_uk_seller_id.txt', 'r', encoding='utf-8') as f:
            seller_ids = ['A34X5978LKLGQN']#f.readlines()
            for id in seller_ids:
                id = id.replace('\n','')
                real_url = self.host % id
                yield scrapy.Request(url=real_url,
                                     callback=self.parse,
                                     meta={'seller_id': id})

    def parse(self, response):
        html = response.text
        try:
            good_urls = response.xpath('//div[contains(@data-cel-widget, "search_result")]//span[@class="rush-component"]/a/@href | //div[contains(@class, "sg-col-inner")]//span[@class="rush-component"]/a/@href').getall()
            good_urls = [self.base_host + url for url in good_urls]
        except:
            good_urls = []

        for url in good_urls:
            try:
                good_id = re.search(r'dp/(\w+)/ref', url).group(1)
            except:
                good_id = ''

            item = AmazonItem(good_id=good_id)
            yield item

        # 下一页
        next_page = response.xpath('//li[@class="a-last"]/a/@href').get()
        if next_page:
            next_page = self.base_host + next_page
            yield scrapy.Request(url=next_page,
                                 callback=self.parse)
