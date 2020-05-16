# -*- coding: utf-8 -*-
import scrapy
from gm_work.items import GmWorkItem
from scrapy_redis.spiders import RedisSpider
from tools.tools_r.header_tool import headers_todict
from scrapy.http.response import Response



class SmtGoodsSpider(RedisSpider):
    "校验sellerid是否有爬取的手机页面"
    goods_num = 0
    name = 'smt_sellerid'
    allowed_domains = ['aliexpress.com']
    start_urls = ['http://m.aliexpress.com']
    redis_key = "smt_sellerid:start_url"
    seeds_file = r"C:\Users\admin\Desktop\{smt_shopid_201910_有效}[店铺ID,卖家ID].txt"
    def start_requests(self):
        for i in self.from_file(self.seeds_file):
            i = i.strip()
            if "," in i:
                shop_id = i.split(",",1)[0]
                seller_id = i.split(",",1)[1]
                url = "https://m.aliexpress.com/store/v3/home.html?shopId={}&sellerId={}&pagePath=allProduct.htm"
                url = url.format(shop_id,seller_id)
                headers = self.get_headers()
                meta = {"shop_id":shop_id,"seller_id":seller_id}
                yield scrapy.Request(url=url, callback=self.get_sellerid, method="GET", headers=headers, meta=meta)


    def get_sellerid(self, response):
        meta = response.meta
        seller_id = meta.get("seller_id")
        shop_id = meta.get("shop_id")
        status = response.status
        if status == 200:
            if "allProducts" not in response.text:
                print(shop_id,seller_id)
            item = GmWorkItem()
            item["shop_id"] = shop_id
            item["seller_id"] = seller_id
            yield item
        else:
            yield
            print("302:",shop_id, seller_id)

    def get_headers(self):
        headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: m.aliexpress.com
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'''
        headers = headers_todict(headers)
        return headers

    def from_file(self,file_name):
        with open(file_name,"r",encoding="utf-8") as f:
            for i in f:
                yield i


    def try_again(self,response,max_num=5,priority_adjust=0):
        try_num = response.meta.get("try_num", 0) + 1
        if try_num < max_num:
            retryreq = response.request.copy()
            retryreq.meta['try_num'] = try_num
            retryreq.dont_filter = True
            retryreq.priority = response.request.priority + priority_adjust
            return retryreq
        else:
            print("错误大于5次")
