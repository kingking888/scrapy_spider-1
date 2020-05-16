# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import json
from gm_work.items import BeidianItem
import re
from urllib import parse


class BeidianSpider(RedisSpider):
    name = 'beidian'
    allowed_domains = ['beidian.com']
    start_urls = ['http://beidian.com/']
    redis_key = "smt_goods:start_url"

    def start_requests(self):
        "https://m.beidian.com/search/search_category.html?shop_id="
        url = "https://api.beidian.com/mroute.html?method=beidian.item.category.get&_airborne_channel=beidian&_airborne_channel=beidian&_abr_=01fc2256a299e1b72d75460e26ad04f414870d3def5d9feac8"
        yield scrapy.Request(url=url,dont_filter=True)

    def parse(self, response):
        text = response.text
        data_json = json.loads(text)#添加检查和错误代码
        items = BeidianItem()
        items["source_code"] = data_json
        yield items
        success = data_json.get("success")
        if success:
            main_categorys = data_json.get("main_categorys")
            for main_category in main_categorys:
                category_name = main_category.get("category_name")
                blocks = main_category.get("blocks")
                for block in blocks:
                    block_name = block.get("block_name")
                    subdivision_categorys = block.get("subdivision_categorys")
                    for subdivision_category in subdivision_categorys:
                        title = subdivision_category.get("title")
                        img = subdivision_category.get("img")
                        url = subdivision_category.get("h5_target")
                        item = BeidianItem()
                        # item["category_name"] = category_name
                        # item["block_name"] = block_name
                        # item["title"] = title
                        # item["img"] = img
                        # item["url"] = url
                        match = re.search("keyword=(.*)",url)
                        if match:
                            keyword = match.group(1)
                            keyword = keyword.split("&")[0]
                            item["keyword"] = keyword
                            # keyword = parse.unquote(keyword)
                            # yield item
                            headers = self.get_headers()
                            url_next = "https://api.beidian.com/mroute.html?method=beidian.search.item.list&_airborne_channel=beidian&_airborne_channel=beidian&_abr_=01a32d37b01d9a33d927f1870d193b631eb8b982425da03ddc&keyword={}&sort=hot&page_size=20&page=1".format(keyword)
                            yield scrapy.Request(url=url_next,callback=self.get_goodslist, method="GET",headers=headers)

    def get_goodslist(self,response):
        a = response.request.headers
        text = response.text
        data_json = json.loads(text)
        items = BeidianItem()
        items["source_code"] = data_json
        yield items
        success = data_json.get("success")
        if success:
            keyword = data_json.get("keyword")
            item_count = data_json.get("item_count")
            items = data_json.get("items")
            for good in items:
                product_id = good.get("product_id")
                brand_id = good.get("brand_id")
                cid = good.get("cid")
                iid = good.get("iid")
                sort = good.get("sort")
                price = good.get("price")
                origin_price = good.get("origin_price")
                price_max = good.get("price_max")
                title = good.get("title")
                img = good.get("img")
                desc = good.get("desc")
                real_seller_count = good.get("real_seller_count")
                item = BeidianItem()
                item["keyword"] = keyword
                item["item_count"] = item_count
                item["product_id"] = product_id
                item["brand_id"] = brand_id
                item["cid"] = cid
                item["iid"] = iid
                item["sort"] = sort
                item["price"] = price
                item["origin_price"] = origin_price
                item["price_max"] = price_max
                item["title"] = title
                item["img"] = img
                item["desc"] = desc
                item["real_seller_count"] = real_seller_count
                yield item


    def get_detail(self,response):
        pass


    def get_headers(self):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Host": "api.beidian.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
        }
        return headers











