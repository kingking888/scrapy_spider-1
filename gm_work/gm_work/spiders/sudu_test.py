# -*- coding: utf-8 -*-
import scrapy
from tools.tools_r.header_tool import headers_todict
from gm_work.items import GmWorkItem
from scrapy_redis.spiders import RedisSpider



class SuduTestSpider(RedisSpider):
    name = 'sudu_test'
    allowed_domains = ['']
    start_urls = ['']
    redis_key = "sudu_test:start_url"

    def start_requests(self):
        yield scrapy.Request(url="https://m.aliexpress.com/store/v3/home.html?sellerId=234730236&pagePath=allProduct.htm",dont_filter=True)

    def parse(self, response):
        for i in range(20000, 20001):
            headers_str = '''User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36
        accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
        accept-encoding: gzip, deflate, br
        accept-language: zh-CN,zh;q=0.9
        user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'''
            headers = headers_todict(headers_str)
            url = "https://www.aliexpress.com/store/feedback-score/{}.html".format(i)
            yield scrapy.Request(url=url, callback=self.smt_saomiao, method="GET", headers=headers,dont_filter=True)

    def smt_saomiao(self,response):
        text = response.text
        url = response.url
        Seller = response.css("tit1le").xpath("./text()").get()
        Feedback = "fsdf\nfsdfs"
        Since = 1
        item = GmWorkItem()
        item["url"] = url
        item["Seller"] =Seller
        # item["Feedback"] =Feedback
        # item["Since"] = Since
        item["source_code"] = text
        yield item
