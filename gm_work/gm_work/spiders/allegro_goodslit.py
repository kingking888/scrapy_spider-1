# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
import json


class AllegroSpider(RedisSpider):
    name = 'allegro_goodlist'
    allowed_domains = ['allegro.pl']
    start_urls = ['http://allegro.pl/']
    redis_key = "allegro_goodlist:start_url"

    def start_requests(self):
        url = "https://allegro.pl/kategoria/literatura-i-instrukcje-124882"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)

    def sort_all(self,response):
        youxiao = re.search("(StoreState_base)",response.text)
        url = response.url
        if youxiao:
            match = re.search("StoreState_base'] = ({.*?});</script>",response.text)
            if match:
                data_str = match.group(1)
                try:
                    data = json.loads(data_str)
                    items = data.get("items")
                    items_groups = items.get("itemsGroups",{})
                    for i in items_groups:
                        good_list = i.get("items")
                        for j in good_list:
                            good_id = j.get("id")
                            good_url = j.get("url")
                            location = j.get("location",{})
                            city = location.get("city")
                            title = j.get("title",{})
                            good_name = title.get("text")
                            status = j.get("type")
                            price_json = j.get("price",{})
                            normal = price_json.get("normal",{})
                            price = normal.get("amount")
                            sales = j.get("bidInfo")
                            seller = j.get("seller",{})
                            shop_id = seller.get("id")
                            shop_super = seller.get("superSeller")
                            shop_name = seller.get("login")
                            sort_id = j.get("categoryPath")
                            item = GmWorkItem()
                            item["id"] = good_id
                            item["goods_url"] = good_url
                            item["city"] = city
                            item["good_name"] = good_name
                            item["status"] = status
                            item["price"] = price
                            item["sales_num"] = sales
                            item["shop_id"] = shop_id
                            item["shop_super"] = shop_super
                            item["shop_name"] = shop_name
                            item["sort_id"] = sort_id
                            yield item
                except:
                    try_result = self.try_again(response, url=url)
                    yield try_result
            else:
                try_result = self.try_again(response, url=url)
                yield try_result

            # list_all = response.css(".b659611")
            # for i in list_all:
                # good_name = i.xpath(".//h2[@='ebc9be2']/a/font/font/text()").get()
                # good_url = i.xpath(".//h2[@='ebc9be2']/a/@href").get()
                # price_totle = i.xpath(".//div[@='_26a9f30']/div/i/font/font/text()").get()
                # status = i.xpath(".//div[@='fe6e937']/div/dl/dd/font/font/text()").get()
                # sales = i.xpath(".//span[@='_41ddd69']/font/font/text()").get()
                # shop = i.xpath(".//div[@='_26a9f30']/div/i/font/font/text()").get()
                # sort_url = i.xpath("./small/a/@href").get()
                # if sort_url:
                #     sort_url = "https://allegro.pl"+sort_url
                #     item = GmWorkItem()
                #     item["url"] = sort_url
                # else:
                #     print("sort_all有url没有选取")


    def try_again(self,rsp,**kwargs):
        max_num = -1
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
            for i in kwargs:
                item_e[i] = kwargs[i]
            return item_e

    def get_headers(self,type = 1):
        if type == 1:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
            accept-encoding: gzip, deflate, br
            accept-language: zh-CN,zh;q=0.9
            upgrade-insecure-requests: 1
            user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
                        accept-encoding: gzip, deflate, br
                        accept-language: zh-CN,zh;q=0.9
                        upgrade-insecure-requests: 1
                        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)
