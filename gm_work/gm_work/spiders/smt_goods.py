# -*- coding: utf-8 -*-
import scrapy
from tools.tools_r.smt.smt_getcid import get_cid,get_prama
from gm_work.items import GmWorkItem
import json
from scrapy_redis.spiders import RedisSpider


class SmtGoodsSpider(RedisSpider):
    goods_num = 0
    name = 'smt_goods'
    allowed_domains = ['aliexpress.com']
    start_urls = ['http://m.aliexpress.com']
    redis_key = "smt_goods:start_url"
    seeds_file = r"C:\Users\admin\Desktop\{smt_shopid_201910_有效}[店铺ID,卖家ID].txt"
    def start_requests(self):
        yield scrapy.Request(url="https://www.baidu.com",dont_filter=True)

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

    def parse(self,response):
        for i in self.from_file(self.seeds_file):
            i = i.strip()
            if "," in i:
                shop_id = i.split(",",1)[0]
                seller_id = i.split(",",1)[1]
                page_id = get_prama(get_cid())
                cookies = "aefeMsite=amp--wRru0loiCNZjcQEqYc1Ew; ali_apache_id=11.180.122.26.1575437527682.392996.5; isg=BDEx-5kOyCf7m2SmkQaxvTBcQL0LtqIM-G1_rBNGL_giOlOMW256Y8wcWIj58j3I"
                num = 0
                url = "https://m.aliexpress.com/api/search/products/items?pageId={}&searchType=storeSearch&sellerAdminSeq={}&storeId={}&infiniteScroll=true&start={}&shipToCountry=US&__amp_source_origin=https%3A%2F%2Fm.aliexpress.com"
                Referer_str = "https://m.aliexpress.com/storesearch/list/.html?sortType=TC3_D&searchType=storeSearch&trace=store2mobilestoreNew&storeId={}"
                Referer = Referer_str.format(shop_id)
                url = url.format(page_id,seller_id,shop_id,num)
                headers = self.get_headers()
                headers["Cookie"] = cookies
                headers["Referer"] = Referer
                meta = {"page_id":page_id,
                        "seller_id":seller_id,
                        "shop_id":shop_id}
                yield scrapy.Request(url=url,callback=self.get_detail,method="GET",headers=headers,meta=meta)

    def get_detail(self, response):
        meta = response.meta
        json_str = response.text
        req_url = response.url
        seller_id = meta.get("seller_id")
        shop_id = meta.get("shop_id")
        page_id = meta.get("page_id")
        if json_str.startswith('{"'):
            item_s = GmWorkItem()
            item_s["source_code"] = json_str
            yield item_s
            json_data = json.loads(json_str)
            # success = json_data.get("success")
            data = json_data.get("data")
            # nextUrl = data.get("nextUrl")
            items = data.get("items")
            # if not items:
            #     print("item为空",shop_id,req_url)


            trace = data.get("trace")
            page = trace.get("page")

            aem_count = int(page.get("aem_count")) if page.get("aem_count") else 0
            if aem_count:
                self.goods_num += aem_count
                if self.goods_num%100000==1:
                    print(self.goods_num)


                for i in range(20, aem_count, 20):
                    url = "https://m.aliexpress.com/api/search/products/items?pageId={}&searchType=storeSearch&sellerAdminSeq={}&storeId={}&infiniteScroll=true&start={}&shipToCountry=US&__amp_source_origin=https%3A%2F%2Fm.aliexpress.com"
                    Referer_str = "https://m.aliexpress.com/storesearch/list/.html?sortType=TC3_D&searchType=storeSearch&trace=store2mobilestoreNew&storeId={}"
                    cookies = "aefeMsite=amp--wRru0loiCNZjcQEqYc1Ew; ali_apache_id=11.180.122.26.1575437527682.392996.5; isg=BDEx-5kOyCf7m2SmkQaxvTBcQL0LtqIM-G1_rBNGL_giOlOMW256Y8wcWIj58j3I"

                    Referer = Referer_str.format(shop_id)
                    url = url.format(page_id,seller_id,shop_id,i)
                    headers = self.get_headers()
                    headers["Cookie"] = cookies
                    headers["Referer"] = Referer
                    meta = {"page_id": page_id,
                            "seller_id": seller_id,
                            "shop_id": shop_id}
                    yield scrapy.Request(url=url, callback=self.get_detail, method="GET", headers=headers, meta=meta)

            for good in items:
                item = GmWorkItem()
                goods_url = good.get("action")
                averageStarStr = good.get("averageStarStr")
                imgUrl = good.get("imgUrl")

                price = good.get("price")
                price1 = price.get("price")
                price_currency = price1.get("currency")
                price_value = price1.get("value")
                productId = good.get("productId")
                subject = good.get("subject")

                item["shop_id"] = shop_id
                item["seller_id"] = seller_id
                item["goods_url"] = goods_url
                item["average_score"] = averageStarStr
                item["img_url"] = imgUrl
                item["currency"] = price_currency
                item["price"] = price_value
                item["goods_id"] = productId
                item["subject"] = subject
                item["shop_id"] = shop_id
                item["aem_count"] = aem_count

                item["pipeline_level"] = "smt商品列表"
                yield item
        else:
            yield self.try_again(response)

    def get_headers(self):
        headers = {
            "Host": "m.vi.aliexpress.com",
            "Connection": "keep-alive",
            "Accept": "application/json",
            "AMP-Same-Origin": "true",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": "isg=BLe25me9pv6r8iJyBJaO7Y-BRqvB1IxEwYs0IwllWgHzuNT6FU0TLoLWnlhDUGNW"
        }
        return headers

    def from_file(self,file_name):
        with open(file_name,"r",encoding="utf-8") as f:
            for i in f:
                yield i
