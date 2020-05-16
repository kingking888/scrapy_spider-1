# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re


class AmazongsSpider(RedisSpider):
    name = 'amazon_goodstoshop'
    allowed_domains = ['alibaba.com']
    start_urls = ['http://www.amazon.com/']
    redis_key = "amazon_goodstoshop:start_url"
    headers = headers_todict('''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36''')

    def start_requests(self):
        url = "https://www.baidu.com/"
        yield scrapy.Request(url=url,method="GET",callback=self.seed_request,headers=self.headers,dont_filter=True)
    def seed_request(self,response):

        path = r"C:/Users\admin/Desktop/"
        file_name = "{6_1排行榜_offer有效}[goodsid].txt_去重 - 副本.txt"
        with open(path+file_name,"r",encoding="utf-8") as f:
            for i in f:
                i = i.strip()
                page_num = 0
                url = "https://www.amazon.co.uk/gp/aw/ol/{}".format(i)
                yield scrapy.Request(url=url, method="GET", headers=self.headers,meta={"page_num":page_num,"key":i})

    def parse(self, response):
        youxiao = re.search("(olpOfferList|olpProduct)",response.text)
        key = response.meta.get("key")
        if youxiao:
            item_s = GmWorkItem()
            item_s["key"] = key
            item_s["source_code"] = response.text
            yield item_s
            shop_list = response.css(".a-section.a-spacing-double-large").xpath(
                "./div//h3[@class='a-spacing-none olpSellerName']/a")
            if not shop_list:
                item = GmWorkItem()
                item["key"] = key
                item["name"] = ""
                item["url"] = ""
                item["seller_id"] = ""
                yield item
            for i in shop_list:
                name = i.xpath("./text()").get()
                if name:
                    name = name.strip()
                url = i.xpath("./@href").get()
                seller_id = ""
                match = re.search('(s|seller)=(.*?)($|[&])',url)
                if match:
                    seller_id = match.group(2)
                item = GmWorkItem()
                item["key"] = key
                item["name"] = name
                item["url"] = url
                item["seller_id"] = seller_id
                yield item
            next_url = response.css("li.a-last").xpath("./a/@href").get()
            if next_url:
                next_url = "https://www.amazon.co.uk"+next_url
                yield scrapy.Request(url=next_url, method="GET", headers=self.headers, meta={"key": key})
        else:
            try_result = self.try_again(response,key)
            yield try_result

    def try_again(self,rsp,key):
        max_num = 10
        meta = rsp.meta
        try_num = meta.get("try_num",0)
        if try_num < max_num:
            try_num += 1
            request = rsp.request
            request.dont_filter = True
            request.meta["try_num"] = try_num
            return request
        else:
            item_e = GmWorkItem()
            item_e["error_id"] = 1
            item_e["key"] = key
            return item_e