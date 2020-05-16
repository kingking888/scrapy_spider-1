# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict

class YmxSpider(RedisSpider):
    name = 'amazon_uksort'
    allowed_domains = ['amazon.co.uk']
    start_urls = ['https://www.amazon.co.uk/gp/site-directory']
    host = 'https://www.amazon.co.uk'

    def start_requests(self):
        url = "https://www.amazon.co.uk/gp/site-directory"
        yield scrapy.Request(url=url,dont_filter=True,headers=self.get_headers())
    # 一级分类
    def parse(self, response):
        urls = response.css("#shopAllLinks").xpath('.//td/div/ul/li')
        for i in urls:
            url = i.xpath("./a/@href").get()
            name = i.xpath("./a/text()").get()
            item = GmWorkItem()
            if "node" in url:
                url = self.host + url
                item["last_name"] = "原始"
                item["url"] = url
                item["name"] = name
                item["state"] = "正常"
                item["deep"] = 1

                yield item

                yield scrapy.Request(url=url,callback=self.parse_category2,meta={"name":name,"url":url,"deep":1},headers=self.get_headers())
    # 主分类
    def parse_category2(self, response):
        last_name = response.meta.get("name")
        deep = response.meta.get("deep")+1

        if response.status == 200:
            if response.xpath('//li[@class="s-ref-indent-neg-micro"]'):
                url = response.xpath('//li[@class="s-ref-indent-neg-micro"]//a/@href').get()
                name = response.xpath('//li[@class="s-ref-indent-neg-micro"]//a/span/text()').get()
                real_url = self.host + url

                item = GmWorkItem()
                item["last_name"] = last_name
                item["url"] = real_url
                item["name"] = name
                item["state"] = "正常"
                item["deep"] = deep
                yield item
                # yield scrapy.Request(url=real_url,callback=self.parse_category2)
            else:
                item = GmWorkItem()
                item["last_name"] = last_name
                item["url"] = ""
                item["name"] = ""
                item["state"] = "无url"
                item["deep"] = deep
                yield item

                # yield scrapy.Request(url=response.url,callback=self.parse_category3)
        else:
            item = GmWorkItem()

            item["last_name"] = last_name
            item["url"] = ""
            item["name"] = ""
            item["state"] = "状态码错误"
            item["deep"] = deep

            print(last_name)

    # 下级分类
    def parse_category3(self, response):
        if response.status == 200:
            urls = response.xpath('//ul[contains(@class, "s-ref-indent-one")]//a/@href | //ul[contains(@class, "s-ref-indent-two")]//a/@href | //li[@class="a-spacing-micro s-navigation-indent-2"]//a/@href').getall()

            if urls != []:
                print(urls)
                real_urls = [self.host + url for url in urls]

                # 进入下级目录
                for real_url in real_urls:
                    yield scrapy.Request(url=real_url,
                                         callback=self.parse_category3)
            else:
                cat1_name = response.xpath('//li[@class="s-ref-indent-neg-micro"]//text()').getall()
                cat2_name = response.xpath('//li[@class="a-spacing-micro s-navigation-indent-1"]/span/span/text() | //li[@class="s-ref-indent-one"]//text()').get()
                url = response.url

                if cat1_name != [] and cat2_name:
                    for i in cat1_name:
                        i = i.strip()
                        # print('上级目录：%s，下级目录：%s，url：%s' % (i,cat2_name,url))
                    yield scrapy.Request(url=response.url,
                                         callback=self.parse_list)
    # 商品列表页
    def parse_list(self, response):
        if response.status == 200:
            pass
    def get_headers(self):
        headers = headers_todict('''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
        accept-encoding: gzip, deflate, br
        accept-language: zh-CN,zh;q=0.9
        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36''')
        return headers