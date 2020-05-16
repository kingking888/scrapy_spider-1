# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import AmazonItem
from tools.tools_r.header_tool import headers_todict
import urllib



class AmazonPhSpider(RedisSpider):
    name = 'amazon_ph'
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

    def start_requests(self):
        url = "https://www.amazon.com/销售排行榜/zgbs/ref=zg_bs_unv_0_1045024_4?language=zh_CN"
        deep = 1
        yield scrapy.Request(url=url,method="GET",headers=self.headers,dont_filter=True,meta={"deep":deep})

    def parse(self, response):
        catelog = response.meta.get("catelog_name")
        deep = response.meta.get("deep",1)
        catelog_url = response.url
        xpath_str = ".{}/li".format("/ul"*deep)
        url_catalog = response.css("#zg_browseRoot").xpath(xpath_str)
        second_url = response.css(".a-last").xpath("./a/@href").get()
        if second_url:
            yield scrapy.Request(url=second_url, method="GET", headers=self.headers,meta={"catelog_name":catelog,"deep": deep})
        for i in url_catalog:
            url_next = i.xpath("./a/@href").get()
            catelog_name = i.xpath("./a/text()").get()

            if url_next:
                deep_next = deep+1
                yield scrapy.Request(url=url_next,method="GET",headers=self.headers,meta={"catelog_name":catelog_name,"deep":deep_next})
        goods_list = response.css("#zg-ordered-list").xpath("./li")
        for i in goods_list:
            url = i.xpath("./span/div/span/a/@href").get()
            if url:
                url = "https://www.amazon.com"+url
            good_name = i.xpath("./span/div/span/a/div/text()").get()
            if good_name:
                good_name = good_name.strip()
            level = i.xpath("./span/div/span/div[1]/a[1]/i/span/text()").get()
            if level:
                level = level.replace(" out of 5 stars","")
            evaluates = i.xpath("./span/div/span/div[1]/a[2]/text()").get()
            if evaluates:
                evaluates = evaluates.replace(",","")
            price = i.xpath("./span/div/span/div[2]/a/span/span/text()").get()
            if price:
                price = price.replace("$","")

            item = AmazonItem()
            item["url"] = url
            item["good_name"] = good_name
            item["level"] = level
            item["evaluates"] = evaluates
            item["price"] = price
            item["catelog_name"] = catelog
            item["catelog_url"] = catelog_url
            item["deep"] = deep

            yield item


