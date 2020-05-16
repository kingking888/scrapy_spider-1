# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy_redis.spiders import RedisSpider
import scrapyd
from ant_app.items import AntAppItem
from scrapy.http import Response
from urllib.parse import urljoin
import re

class LazadaSpider(RedisSpider):
    name = 'lazada'
    allowed_domains = ['www.lazada.sg']
    start_urls = ['https://www.lazada.sg/']
    redis_key = "lazada:start_url"

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0],method="GET",headers=self.get_headers(1),dont_filter=True)

    def parse(self, response):
        #location = response.headers.get("server").decode("utf-8")
        scecond_list = response.css(".lzd-site-menu-root").xpath("./ul/li")
        url_list = []
        for i in scecond_list:
            url = i.xpath("./a/@href").get()
            third_list = i.xpath("./ul/li/a/@href").getall()

            if len(third_list)==0:
                url_list.append(url)
            else:
                url_list.extend(third_list)
        # for i in url_list:
        #     child_url = urljoin("https://www.lazada.sg/",i)
        for i in range(100):
            url_page = "https://www.lazada.sg/shop-mobiles/"+"?page="+str(i)
            yield scrapy.Request(url=url_page, method="GET", headers=self.get_headers(1),callback=self.get_detailurl)

    def get_detailurl(self, response):
        text = response.text
        pagedata = re.search("window.pageData=([\s\S]*?)</script>",text)
        if "验证" in response.text:
            print("出现验证页面")
        else:
            try:
                data_json = json.loads(pagedata.group(1))
                mods = data_json.get("mods")
                listItems = mods.get("listItems")
                for i in listItems:
                    name = i.get("name")
                    productUrl = i.get("productUrl")
                    #originalPriceShow = i.get("originalPriceShow")
                    #priceShow = i.get("priceShow")
                    #discount = i.get("discount")
                    #review = i.get("review")
                item = AntAppItem()
                item["name"] = name
                #item["productUrl"] = productUrl

                yield item
            except Exception as e:
                print("网址出错了")
                print(e)


    def get_headers(self,num):
        if num == 1:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection":"keep-alive",
                "Upgrade-Insecure-Requests":"1",
                "cookies":"Hm_lvt_7cd4710f721b473263eed1f0840391b4=1564414866; Hm_lpvt_7cd4710f721b473263eed1f0840391b4=1564419137; lzd_cid=531e327d-97ff-48c3-d085-46428daa35e2; t_uid=531e327d-97ff-48c3-d085-46428daa35e2; t_fv=1564419148132; t_sid=JDTD2oA1mhczuScJLJUysQTrihEGvvAc; utm_channel=NA; hng=SG|en-SG|SGD|702; userLanguageML=en; _m_h5_tk=13131d769e1d0ad4372fde6a5aea0c0d_1564428867477; _m_h5_tk_enc=e874d3000109afd0259d869b4d4e2bbc; lzd_sid=13e06ccb06fcb5a1c9ae8332fced2dc2; anon_uid=bef2985c004c9499f6274934207e9247; _tb_token_=334688351d90b; _bl_uid=a4jj5yhgo4nmF1r97qnzlw0ugnF5; cna=bCFXFcDwyh8CAX137X2qBExG; JSESSIONID=B659384DD2FCF073D702745D5DB044EC; criteo_write_test=ChUIBBINbXlHb29nbGVSdGJJZBgBIAE; cto_lwid=fff81760-67b6-4ca7-8eff-452869dececd; _ga=GA1.2.717693781.1564419174; _gid=GA1.2.743770771.1564419174; _gat_UA-49088239-1=1; _fbp=fb.1.1564419174680.104023857; l=cBaurOXPqrEkpNQDBOCZlurza77OSIRYhuPzaNbMi_5C16L1bGQOk2DMjFp62jWdODYB4k6UXwe9-etkiWLfDLv1Lis5.; isg=BCIimBwvi0IsgZeNnajcwNCac6iEcyaNyIRdKmy7QBVAP8K5VABLnYmtbDtmVZ4l",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            }
        return headers


