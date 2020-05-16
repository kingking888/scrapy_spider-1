# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import json
from gm_work.items import softtime

class SorftimeSpider(RedisSpider):
    name = 'softtime_sort'
    start_urls = ['']
    redis_key = "softtime_sort:start_url"

    def start_requests(self):
        url = "https://api.sorftime.com/home/sortData"
        headers = self.get_headers(1)
        auth = "eyJjcHVJZCI6Ik9EazVPRGxCTURBdE1EaEdOUzB4TVVVNUxUazVPVEV0TmpRMFFVTkdSamt6UkRBdyIsIm1hY2hpbmVDb2RlIjoiTkdORmVHTk5NVXRWV0RndlZUQldNRXBPY0VaS05VNTNNWFpIZVdsbVRVTlhWM1ZLS3paVk5teHBRbE5XV1ZsRUt6RmlaMkpyVDBOaVoxUk9Sa2x6VVE9PSIsImNoZWNrQ29kZSI6Ik1qQXlNREF6TURJeE1USXhOVFkwTmpVPSIsInNlcmlhbE5vIjoiT1VVNU1qRTVRMFJDT1RFd1FqWkVOUT09IiwidWNvZGUiOiI4OTFiNDgzYzI4Yjg0N2FkYmVmYmI5OTFlZTY4YWRiZSJ9"
        headers["Referer"] = "https://api.sorftime.com/?lang=zh-CN&auth="+auth
        headers["Cookie"] = "LanguageCulture=zh-CN"
        prama = "auth="+auth+"&lang=zh-CN"
        yield scrapy.FormRequest(url, method="POST", headers=headers, body=prama, dont_filter=True,callback=self.parse_fenlei)

    def parse_fenlei(self, response):
        key = "softtime_sort"
        try:
            sort_data = json.loads(response.text)
            data_list = sort_data.get("Data")
            for i in data_list:
                item = softtime()
                id = i.get("id")
                pid = i.get("pId")
                NodeId = i.get("NodeId")
                name = i.get("name")
                SaleCount = i.get("SaleCount")
                BrandCount = i.get("BrandCount")
                Url = i.get("Url")
                item["id"] =str(id)
                item["pid"] =str(pid)
                item["NodeId"] =str(NodeId)
                item["name"] =str(name)
                item["SaleCount"] =str(SaleCount)
                item["BrandCount"] =str(BrandCount)
                item["Url"] =str(Url)
                yield item
            item_s = softtime()
            item_s["key"] = key
            item_s["source_code"] = response.text
            yield item_s
        except Exception as e:
            self.try_again(response,key=key)
            print(e)


    def get_headers(self,num):
        if num == 1:
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection":"keep-alive",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Host": "api.sorftime.com",
                "Origin": "https://api.sorftime.com",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
            }
            return headers

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
            item_e = softtime()
            item_e["error_id"] = 1
            for i in kwargs:
                item_e[i] = kwargs[i]
            return item_e
