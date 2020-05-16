# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re


class AllegroSpider(RedisSpider):
    name = 'allegro_sort'
    allowed_domains = ['allegro.pl']
    start_urls = ['http://allegro.pl/']
    redis_key = "allegro_sort:start_url"

    def start_requests(self):
        url = "https://allegro.pl/mapa-strony/kategorie"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)

    def sort_all(self,response):
        if response.status == 200:
            headers = self.get_headers(1)
            sort_all = response.css(".container-header._1s2v1._n2pii._sdhee")
            for i in sort_all:
                sort_url = i.xpath("./small/a/@href").get()
                if sort_url:
                    sort_url = "https://allegro.pl"+sort_url
                    item = GmWorkItem()
                    item["url"] = sort_url
                    yield scrapy.Request(url=sort_url,method="GET",headers=headers,dont_filter=True)
                else:
                    print("sort_all有url没有选取")

    def parse(self, response):
        youxiao = re.search("(gS4GqiXvRSi8oJgNBVklGA)",response.text)
        url = response.url
        if youxiao:
            item_s = GmWorkItem()
            item_s["url"] = url
            item_s["source_code"] = response.text
            yield item_s
            shop_list = response.xpath("//div[@data-box-id='gS4GqiXvRSi8oJgNBVklGA==']/div/ul//a")
            if not shop_list:
                print("shop_list有url没有选取")
            for i in shop_list:
                url = i.xpath("./@href").get()
                name = i.xpath("./text()").get()
                url = "https://allegro.pl"+url
                item = GmWorkItem()
                item["name"] = name
                item["url"] = url
                yield item

        else:
            try_result = self.try_again(response,url=url)
            yield try_result

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
