# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import hashlib
import json
from gm_work.items import GmWorkItem



class FlcrmSpider(RedisSpider):
    name = 'flcrm'
    #allowed_domains = ['baidu.com']

    redis_key = "flcrm:start_url"
    def start_requests(self):
        url = "http://www.baidu.com"
        yield scrapy.Request(url, dont_filter=True, method="GET")

    def parse(self,response):
        for i in range(0,160):
            url = "https://market-api.sitebuilding.cn/api/v1/customer_open_list"
            prama = '''{"header":{"app":"console","ver":"v1","sign":"format_kuohao"},"body":{"page":format_num,"params":{"centerId":10,"mountId":null,"name":null},"rows":100}}'''
            prama_new = self.get_prama(prama,i)
            yield scrapy.FormRequest(url,dont_filter=True,method="POST",callback=self.get_id,headers=self.get_headers(1),body=prama_new)

    def get_prama(self,prama,num):
        prama = prama
        prama_md5 = prama.replace("format_kuohao", "")
        prama_md5 = prama_md5.replace("format_num", str(num))
        md5_pra = prama_md5 + "Sou1GY1UW2eX2N4sH8zhpdoDSuMFvt3R"
        m2 = hashlib.md5()
        m2.update(md5_pra.encode('utf-8'))
        md5_mima = m2.hexdigest()
        md5_mima = md5_mima.upper()
        prama_new = prama.replace("{", "{{")
        prama_new = prama_new.replace("}", "}}")
        prama_new = prama_new.replace("format_num", str(num))
        prama_new = prama_new.replace("format_kuohao", "{}")
        prama_new = prama_new.format(md5_mima)
        return prama_new

    def get_id(self,response):


        json_data = json.loads(response.text)
        header = json_data.get("header")
        code = header.get("code")

        data = json_data.get("data")
        data_list = data.get("data")
        for company_data in data_list:
            company_name = company_data.get("name")
            email = company_data.get("email")
            address = company_data.get("address")
            products = company_data.get("products")
            area = company_data.get("area")
            sourceName = company_data.get("sourceName")
            promoterName = company_data.get("promoterName")
            state = company_data.get("state")
            levelValue = company_data.get("levelValue")
            createTime = company_data.get("createTime")
            site = company_data.get("site")
            industryName = company_data.get("industryName")

            meta = {
                "company_name": company_name,
                "email": email,
                "address": address,
                "products": products,
                "area": area,
                "sourceName": sourceName,
                "promoterName": promoterName,
                "state": state,
                "levelValue": levelValue,
                "createTime": createTime,
                "site": site,
                "industryName": industryName,
            }

            userId = company_data.get("userId")
            url = "https://market-api.sitebuilding.cn/api/v1/linkman_list"
            prama = '''{"header":{"app":"console","ver":"v1","sign":"format_kuohao"},"body":{"page":1,"params":{"centerId":10,"customerId":format_num},"rows":10}}'''
            prama_new = self.get_prama(prama,userId)

            yield scrapy.FormRequest(url,dont_filter=True,method="POST",callback=self.get_link,headers=self.get_headers(1),body=prama_new,meta=meta)

    def get_link(self,response):

        json_data = json.loads(response.text)
        header = json_data.get("header")
        code = header.get("code")

        company_data =response.meta
        company_name = company_data.get("company_name")
        email = company_data.get("email")
        address = company_data.get("address")
        products = company_data.get("products")
        area = company_data.get("area")
        sourceName = company_data.get("sourceName")
        promoterName = company_data.get("promoterName")
        state = company_data.get("state")
        levelValue = company_data.get("levelValue")
        createTime = company_data.get("createTime")
        site = company_data.get("site")
        industryName = company_data.get("industryName")

        data = json_data.get("data")
        data_list = data.get("data")
        jobName = ""
        name = ""
        mobile = ""
        telphone = ""
        if len(data_list)>0:
            data_list =data_list[0]
            jobName =data_list.get("jobName")
            name =data_list.get("name")
            mobile =data_list.get("mobile")
            telphone =data_list.get("telphone")
        item = flcrm()
        item["company_name"] = company_name
        item["email"] = str(email)
        item["address"] = address
        item["products"] = products
        item["area"] = area
        item["sourceName"] = sourceName
        item["promoterName"] = promoterName
        item["state"] = str(state)
        item["levelValue"] = levelValue
        item["createTime"] = str(createTime)
        item["site"] = site
        item["industryName"] = industryName
        item["jobName"] = jobName
        item["name"] = name
        item["mobile"] = str(mobile)
        item["telphone"] = str(telphone)
        return item


    def get_headers(self,num):
        if num == 1:
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection":"keep-alive",
                "Host": "market-api.sitebuilding.cn",
                "Content-Type": "application/json",
                "Referer": "https://market.sitebuilding.cn/",
                "token": "G8LPwrpFd7rPS9TZN3rOTR03OseM3Z9T",
                "Origin": "https://market.sitebuilding.cn",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
            }
        return headers



