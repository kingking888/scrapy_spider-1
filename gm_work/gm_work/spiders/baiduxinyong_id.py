# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
import json


class BaiduxinyongSpider(RedisSpider):
    name = 'baiduxinyong_id'
    allowed_domains = ['baidu.com']
    start_urls = ['https://xin.baidu.com/']
    redis_key = "baiduxinyong_id:start_url"


    # def start_requests(self):
    #     url = "https://www.baidu.com"
    #     headers = self.get_headers(1)
    #     yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)
    def make_requests_from_url(self, url):
        headers = self.get_headers(1)
        id = url.replace("http://","")
        url_new = "https://xin.baidu.com/s?q={}&t=0&fl=1&castk=LTE%3D".format(id)
        return scrapy.Request(url=url_new, method="GET", headers=headers, meta={"id": id}, dont_filter=True)#这里需要return

    # def sort_all(self,response):
    #     headers = self.get_headers(1)
    #     if response.status == 200:
    #         with open(r"C:\Users\Administrator\Desktop\baidu_id.txt","r",encoding="utf-8") as f:
    #             for i in f:
    #                 data = i.strip().split(",")
    #                 url = "https://xin.baidu.com/s?q={}&t=0&fl=1&castk=LTE%3D".format(data[0])
    #                 yield scrapy.Request(url=url,method="GET",headers=headers,meta={"id":data[0]},dont_filter=True)
    #     else:
    #         try_result = self.try_again(response, url=response.request.url)
    #         yield try_result


    def parse(self, response):
        meta = response.meta
        id = meta.get("id")
        youxiao = re.search('(zx-list-item-url|zx-list-op-wrap)',response.text)
        if youxiao:
            company = response.css(".zx-list-item-url").xpath("./text()").get()
            legal_person = response.css(".legal-txt").xpath("./text()").get()
            area = response.css(".zx-ent-props").xpath("./span/span[contains(text(),'地址')]/../text()").get()
            id_s = response.css(".zx-ent-hit-reason-text").xpath("./em/text()").get()
            item = GmWorkItem()
            item["id"] = id
            item["company"] = company
            item["legal_person"] = legal_person
            item["area"] = area
            item["id_s"] = id_s
            yield item
        else:
            print("{}错误了".format(id))
            try_result = self.try_again(response, id=id)
            yield try_result

    def try_again(self,rsp,**kwargs):
        max_num = 1
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
