# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
import json


class BusinessSpider(RedisSpider):
    name = 'business_address'
    allowed_domains = ['amap.com']
    start_urls = ['http://amap.com']
    redis_key = "business_address:start_url"
    ak_g = "5a418c9ee2b9e049469a512917f8e190"
    ak_b = "8OUnXVy4hbNBS67V9v7PltluwYwvzEw5"

    type = 0
    def start_requests(self):
        url = "https://www.baidu.com"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)

    def sort_all(self,response):
        baidu_geode = input("请输入跑类型（高德：1 百度 2）：")
        headers = self.get_headers(1)
        if response.status == 200:
            with open(r"C:\Users\Administrator\Desktop\company_address.txt","r",encoding="utf-8") as f:
                for i in f:
                    data = i.strip().split(",")
                    company = data[0]
                    address = data[1]
                    if self.baidu_geode == 1:
                        url = "https://restapi.amap.com/v3/geocode/geo?address={}&output=json&key={}&output=json".format(address,self.ak_g)
                        if address:
                            yield scrapy.Request(url=url,method="GET",headers=headers,meta={"company":company,"address":address})
                    else:
                        url = "http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}".format(address,self.ak_b)
                        if address:
                            yield scrapy.Request(url=url,callback=self.baidu_first,method="GET",headers=headers,meta={"company":company,"address":address},dont_filter=True)
        else:
            try_result = self.try_again(response, url=response.request.url)
            yield try_result

    def baidu_first(self,response):
        meta = response.meta
        company = meta.get("company")
        address = meta.get("address")
        headers = self.get_headers(1)
        youxiao = re.search('("status":0)',response.text)
        if youxiao:
            data_json = json.loads(response.text)
            result = data_json.get("result")
            location =result.get("location")
            lng = location.get("lng")
            lat =location.get("lat")
            url = "http://api.map.baidu.com/reverse_geocoding/v3/?ak={}&output=json&location={},{}".format(self.ak_b,lat,lng)
            yield scrapy.Request(url=url, method="GET", headers=headers, callback=self.baidu_second, meta={"company": company, "address": address},dont_filter=True)
        else:
            print("百度第1步{}错误了".format(company))
            # try_result = self.try_again(response, company=company, address=address)
            # yield try_result

    def baidu_second(self,response):
        meta = response.meta
        company = meta.get("company")
        address = meta.get("address")
        youxiao = re.search('("status":0)',response.text)
        if youxiao:
            data_json = json.loads(response.text)
            result = data_json.get("result")
            addressComponent = result.get("addressComponent")
            province = addressComponent.get("province")
            city = addressComponent.get("city")
            district = addressComponent.get("district")
            item = GmWorkItem()
            item["company"] = company
            item["address"] = address
            item["province"] = province
            item["city"] = city
            item["district"] = district
            yield item
        else:
            print("百度第一步{}错误了".format(company))
            try_result = self.try_again(response, company=company,address=address)
            yield try_result


    def parse(self, response):
        meta = response.meta
        company = meta.get("company")
        address = meta.get("address")
        youxiao = re.search('("status":"1")',response.text)
        if youxiao:
            data_json = json.loads(response.text)
            geocodes = data_json.get("geocodes")
            if geocodes:
                data = geocodes[0]
                province = data.get("province")
                city = data.get("city")
                district = data.get("district")
                item = GmWorkItem()
                item["company"] = company
                item["address"] = address
                item["province"] = province
                item["city"] = city
                item["district"] = district
                yield item
        else:
            print("{}错误了".format(company))
            try_result = self.try_again(response, company=company,address=address)
            yield try_result


    def try_again(self,rsp,**kwargs):
        max_num = 5
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
