# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re


class QichachaSpider(RedisSpider):
    name = 'qichacha_id'
    allowed_domains = ['qichacha.com/']
    start_urls = ['https://www.qichacha.com/']
    redis_key = "qichacha_id:start_url"


    def start_requests(self):
        url = "https://www.baidu.com"
        headers = self.get_headers(2)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_all,headers=headers,dont_filter=True)

    def sort_all(self,response):
        headers = self.get_headers(1)
        if response.status == 200:
            with open(r"C:\Users\Administrator\Desktop\company_id.txt","r",encoding="utf-8") as f:
                for i in f:
                    data = i.strip().split(",")
                    headers["Referer"] = "https://www.qichacha.com/search?key={}".format(data[0])
                    url = "https://www.qichacha.com/gongsi_mindlist?type=mind&searchKey={}&searchType=0".format(data[0])
                    yield scrapy.Request(url=url,method="GET",headers=headers,meta={"id":data[0]},dont_filter=True)
        else:
            try_result = self.try_again(response, url=response.request.url)
            yield try_result


    def parse(self, response):
        meta = response.meta
        id = meta.get("id")
        youxiao = re.search('(keyMoveItem)',response.text)
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
            headers = '''Accept: */*
                        Accept-Encoding: gzip, deflate, br
                        Accept-Language: zh-CN,zh;q=0.9
                        Connection: keep-alive
                        Cookie: QCCSESSID=s840r5rdj2rbck69tc7plc7i40; UM_distinctid=170a9c662216a-0d96b081e7094c-b791237-240000-170a9c66222d11; zg_did=%7B%22did%22%3A%20%22170a9c662b13ee-076880bdb17784-b791237-240000-170a9c662b268f%22%7D; _uab_collina=158339631590820690201933; acw_tc=73dc082415833963157051353e9213409bbbf2078f2453340d24defabe; hasShow=1; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1583396316,1583396373,1583459671,1583470013; CNZZDATA1254842228=1004506580-1583391724-https%253A%252F%252Fsp0.baidu.com%252F%7C1583472798; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201583474054515%2C%22updated%22%3A%201583474054687%2C%22info%22%3A%201583396315830%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22%22%2C%22cuid%22%3A%20%229c1d7cbd2e6e44ca53f5b36a49bdee3d%22%2C%22zs%22%3A%200%2C%22sc%22%3A%200%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1583474055
                        Host: www.qichacha.com
                        Referer: https://www.qichacha.com/search?key=92429005MA4DC7B27E
                        Sec-Fetch-Dest: empty
                        Sec-Fetch-Mode: cors
                        Sec-Fetch-Site: same-origin
                        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.16 Safari/537.36
                        X-Requested-With: XMLHttpRequest'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
            accept-encoding: gzip, deflate, br
            accept-language: zh-CN,zh;q=0.9
            upgrade-insecure-requests: 1
            user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)
