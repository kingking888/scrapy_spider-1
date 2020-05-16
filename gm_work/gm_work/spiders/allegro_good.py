# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re
import json


class AllegroSpider(RedisSpider):
    name = 'allegro_good'
    allowed_domains = ['allegro.pl']
    start_urls = ['http://allegro.pl/']
    redis_key = "allegro_good:start_url"

    def start_requests(self):
        headers = self.get_headers(1)
        url = "https://www.baidu.com"
        yield scrapy.Request(url=url, method="GET",callback=self.seed_request, headers=headers,dont_filter=True)

    def seed_request(self, response):
        # url = "https://allegro.pl/oferta/zestaw-czyszczacy-9w1-do-aparatu-optyki-sciereczka-8906638228?bi_s=ads&bi_m=listing%3Adesktop%3Acategory&bi_c=OTJjMzUwM2QtZWM4Yy00M2MzLWJiOGUtMzE0YTJlYzNiNDJkAA&bi_t=ape&referrer=proxy&emission_unit_id=95d32e58-fb01-4fd4-bbfa-c1d42e8eab51"
        headers = self.get_headers(1)
        with open(r"W:\scrapy_xc\allegro_good-error_合并.txt","r",encoding="utf-8") as f:
            for i in f:
                url = i.strip()
                yield scrapy.Request(url=url, method="GET", callback=self.sort_all, headers=headers, dont_filter=True)
    def sort_all(self,response):
        youxiao = re.search("(About seller|Sprzedający)",response.text)
        url = response.request.url
        if youxiao:
            seller_id = ""
            positive_number = ""
            bad_number = ""
            match = re.search('"sellerId":"(.*?)"',response.text)
            if match:
                seller_id = match.group(1)
            positive_feedback = response.css(".a7caa336.d7c56f78._476b319e").xpath("./text()").get()
            number = response.css(".fa4668cc").xpath("./text()").getall()
            if len(number) == 2:
                positive_number = number[0]
                bad_number = number[1]
            year = response.css("._1604f5d6._82f13583").xpath("./div/div/text()").get()
            match = re.search('({"leftLink".*?"hideContact":.*?})',response.text)
            regon = ""
            nip = ""
            company_data = []
            if match:
                data_str = match.group(1)
                try:
                    data = json.loads(data_str)
                    company_data = data.get("companyData")
                    for i in company_data:
                        if "REGON" in i:
                            regon = i
                        if "NIP" in i:
                            nip = i
                except:
                    pass
            # else:
            #     try_result = self.try_again(response, url=url)
            #     yield try_result
            item = GmWorkItem()
            item["seller_id"] = seller_id
            item["positive_feedback"] = positive_feedback
            item["positive_number"] = positive_number
            item["bad_number"] = bad_number
            item["year"] = year
            item["regon"] = regon
            item["nip"] = nip
            item["company_data"] = str(company_data)
            yield item
        else:
            try_result = self.try_again(response, url=url)
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
