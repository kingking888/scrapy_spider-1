# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import response
from ant_app.items import test

class TestSpider(scrapy.Spider):
    name = 'cookie_headers'
    allowed_domains = ['hz.lianjia.com']
    start_urls = ['https://hz.lianjia.com/ershoufang/']
    custom_settings = {"COOKIES_ENABLED":True}
    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0],callback=self.second_request,method="GET",meta={"cookiejar":"ershoufan"},
                             cookies={"hhhhh":"xxxxx","xxxx1":"cccc"},headers=self.get_headers(1))

    def parse(self, response):
        state = response.status
        content = response.text
        url = response.url
        url = None
        url = url.strim()
        item = test()
        item["state"] = state
        item["content"] = content
        item["url"] = url
        return item
    def second_request(self,respone):
        url = "https://hz.lianjia.com/ershoufang/xihu/"
        yield scrapy.Request(url,method="GET",cookies={"fsdgs":"sgsdgsf"})

    def get_headers(self,type):
        if type == 1:
            headers = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, br",
                "Accept-Language":"zh-CN,zh;q=0.9",
                "Host":"hz.lianjia.com",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                "Cookie":"EuCookie='this site uses cookies'; __utma=235730399.1295424692.1421928359.1447763419.1447815829.20; s_fid=2945BB418F8B3FEE-1902CCBEDBBA7EA2; __atuvc=0%7C37%2C0%7C38%2C0%7C39%2C0%7C40%2C3%7C41; __gads=ID=44b4ae1ff8e30f86:T=1423626648:S=ALNI_MalhqbGv303qnu14HBk1HfhJIDrfQ; __utmz=235730399.1447763419.19.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; TrackJS=c428ef97-432b-443e-bdfe-0880dcf38417; OLProdServerID=1026; JSESSIONID=441E57608CA4A81DFA82F4C7432B400F.f03t02; WOLSIGNATURE=7f89d4e4-d588-49a2-9f19-26490ac3cdd3; REPORTINGWOLSIGNATURE=7306160150857908530; __utmc=235730399; s_vnum=1450355421193%26vn%3D2; s_cc=true; __utmb=235730399.3.10.1447815829; __utmt=1; s_invisit=true; s_visit=1; s_prevChannel=JOURNALS; s_prevProp1=TITLE_HOME; s_prevProp2=TITLE_HOME"
            }
        return headers
