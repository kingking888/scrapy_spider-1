# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
from urllib.parse import quote


class FruugoSpider(RedisSpider):
    name = 'data_city_zhejiang'
    allowed_domains = ['zj.gov.cn']
    start_urls = ['']
    redis_key = "data_city_zhejiang:start_url"

    def start_requests(self):
        url = "http://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web3077/site/flash/tjj/Reports1/2019%E5%B9%B4%E7%BB%9F%E8%AE%A1%E5%B9%B4%E9%89%B4%E5%85%89%E7%9B%9820200121_2146/html/cn/index.html"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers)

    def sort_all(self,response):
        req_url = response.request.url
        if response.status == 200:
            headers = self.get_headers(1)
            all_node = response.css("#foldinglist").xpath("./li/a")
            for i in all_node:
                url = i.xpath("./@href").get().encode("latin1").decode("gbk")
                url = url.replace(".\\","/")
                url = url.replace("\\","/")
                url = url.replace("html","xls")
                url = url.replace("htm","xls")
                name = i.xpath("./text()").get().encode("latin1").decode("gbk")
                name = name.strip()
                last_url = "http://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web3077/site/flash/tjj/Reports1/2019年统计年鉴光盘20200121_2146/excel/cn"
                url_next = last_url + url
                meta = {"title":name}
                yield scrapy.Request(url=url_next, method="GET", headers=headers,meta=meta)
        else:
            self.try_again(response,url=req_url)

    def parse(self, response):
        title = response.meta.get("title")
        req_url = response.request.url
        if response.status == 200:
            a = response.body
            with open(r"C:\Users\Administrator\Desktop\数据中国\浙江年鉴\{}.xls".format(title), "wb") as f:
                f.write(a)
        else:
            self.try_again(response,url=req_url)


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
            headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cache-Control: no-cache
Connection: keep-alive
Host: zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn
Pragma: no-cache
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
                        accept-encoding: gzip, deflate, br
                        accept-language: zh-CN,zh;q=0.9
                        upgrade-insecure-requests: 1
                        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)
