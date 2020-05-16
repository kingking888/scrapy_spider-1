# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import AmazonItem
from tools.tools_r.header_tool import headers_todict




class AmazonukSpider(RedisSpider):
    name = 'amazon_uk'
    allowed_domains = ['www.amazon.com']
    start_urls = ['http://www.amazon.com/']
    redis_key = "amazon_ph:start_url"
    headers = headers_todict('''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    cache-control: no-cache
    pragma: no-cache
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36''')

    # def make_requests_from_url(self, url):(self):
    #     url = "https://www.amazon.com/销售排行榜/zgbs/ref=zg_bs_unv_0_1045024_4?language=zh_CN"
    #     deep = 1
    #     yield scrapy.Request(url=url,method="GET",headers=self.headers,dont_filter=True,meta={"deep":deep})
    #
    # def parse(self, response):