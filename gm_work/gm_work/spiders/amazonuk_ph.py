# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import AmazonItem
from tools.tools_r.header_tool import headers_todict
import re


class AmazonPhSpider(RedisSpider):
    name = 'amazonuk_ph'
    allowed_domains = ['amazon.co.uk']
    start_urls = ['http://www.amazon.co.uk/']
    redis_key = "amazon_ph:start_url"
    headers = headers_todict('''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    cache-control: no-cache
    pragma: no-cache
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36''')
    def start_requests(self):
        # url = "https://www.amazon.co.uk/Best-Sellers-Welcome/zgbs/ref=zg_bsnr_tab"
        # url = "https://www.amazon.co.uk/gp/movers-and-shakers/ref=zg_bsnr_tab"
        url = "https://www.amazon.ae/gp/bestsellers/ref=zg_bsnr_tab"
        deep = 1
        key = "start"
        yield scrapy.Request(url=url,method="GET",headers=self.headers,meta={"deep":deep,"key":key},dont_filter=True)

    def parse(self, response):
        catelog = response.meta.get("catelog_name")
        deep = response.meta.get("deep",1)
        page_num = response.meta.get("page_num",1)
        key = catelog
        youxiao = re.search("zg_browseRoot|Your browsing history",response.text)
        if youxiao:
            catelog_url = response.url
            if page_num == 1:
                second_url = response.css(".a-last").xpath("./a/@href").get()#第二页
                if second_url:
                    yield scrapy.Request(url=second_url, method="GET", headers=self.headers,meta={"catelog_name":catelog,"deep": deep,"page_num":2},dont_filter=True)
                xpath_str = ".{}/li".format("/ul"*deep)
                url_catalog = response.css("#zg_browseRoot").xpath(xpath_str)#列表页
                for i in url_catalog:
                    url_next = i.xpath("./a/@href").get()
                    catelog_name = i.xpath("./a/text()").get()
                    if url_next:
                        deep_next = deep+1
                        yield scrapy.Request(url=url_next,method="GET",headers=self.headers,meta={"catelog_name":catelog_name,"deep":deep_next},dont_filter=True)
            goods_list = response.css("#zg-ordered-list").xpath("./li")
            for i in goods_list:#商品列表解析
                url = i.xpath("./span/div/span/a/@href").get()
                goodid = ""
                if url:
                    url = "https://www.amazon.ae"+url
                    match = re.search("/dp/(.*?)/",url)
                    if match:
                        goodid = match.group(1)
                good_name = i.xpath("./span/div/span/a/div/text()").get()
                if good_name:
                    good_name = good_name.strip()
                level = i.xpath('.//span[@class="a-icon-alt"]').xpath("string(.)").get()
                if level:
                    level = level.replace(" out of 5 stars","")
                # evaluates = i.xpath("./span/div/span/div[1]/a[2]/text()").get()
                evaluates = i.css(".a-size-small.a-link-normal").xpath("./text()").get()
                if evaluates:
                    evaluates = evaluates.replace(",","")
                # price = i.xpath("./span/div/span/div[2]/a/span/span/text()").get()
                price = i.xpath('.//span[@class="p13n-sc-price"]/text()').get()
                if price:
                    price = price.replace("£","")
                offer_from = i.xpath('.//span[@class="a-color-secondary"]/text()').get()
                if offer_from:
                    offer_from = offer_from.strip()

                item = AmazonItem()
                item["url"] = url
                item["goodid"] = goodid
                item["good_name"] = good_name
                item["level"] = level
                item["evaluates"] = evaluates
                item["price"] = price
                item["catelog_name"] = catelog
                item["catelog_url"] = catelog_url
                item["deep"] = deep
                item["offer_from"] = offer_from

                yield item
        else:
            try_result = self.try_again(response,key)
            yield try_result

    def try_again(self,rsp,key):
        max_num = 3
        meta = rsp.meta
        try_num = meta.get("try_num",0)
        if try_num < max_num:
            try_num += 1
            request = rsp.request
            request.dont_filter = True
            request.meta["try_num"] = try_num
            return request
        else:
            print(key)
            item_e = AmazonItem()
            item_e["error_id"] = 1
            item_e["key"] = key
            return item_e