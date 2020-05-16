# -*- coding: utf-8 -*-
import scrapy
from ant_app.items import yamaxun
from scrapy_redis.spiders import RedisSpider
import pymysql
from collections import namedtuple



class YamaxunSpider(RedisSpider):
    name = 'yamaxun'
    allowed_domains = ['www.amazon.cn']
    start_urls = ['https://www.amazon.cn/gp/search/other?ie=UTF8&page=1&pickerToList=enc-merchantbin&rh=n%3A79182071']
    redis_key = "yamaxun:start_url"    

    def start_requests(self):
        # yield scrapy.Request(url=self.start_urls[0],callback=self.get_shanghu,method="GET",dont_filter=True)
        host = '127.0.0.1'
        user = "root"
        password = "imiss968"
        database = "crawl_schema"
        sql = '''SELECT detailurl FROM yamaxun
where detailurl is not null
group by detailurl
having count(`name`) =0;
        '''
        connet = pymysql.connect(host=host, user=user, port=3306, db=database, password=password, charset="utf8")
        cur = connet.cursor()
        num = cur.execute(sql)
        headers = [i[0] for i in cur.description]
        for i in range(num):
            data_shujuku = cur.fetchone()
            data_nametuple = namedtuple("row", headers)
            data = data_nametuple(*data_shujuku)

            url = data.detailurl
            yield scrapy.Request(url=url,callback=self.get_detail,method="GET",dont_filter=True)
        cur.close()
        connet.close()

    def parse(self, response):
        pass

    def getfenlei(self,response):
        fenlei_urls = response.css("a.nav_a.a-link-normal.a-color-base")
        for fenlei in fenlei_urls:
            fenlei_url = fenlei.xpath("./@href").get()
            fenlei_url = "https://www.amazon.cn" + fenlei_url
            fenlei_name = fenlei.xpath("./text()").get()
            item = yamaxun()
            item["fenlei_url"] = fenlei_url
            item["fenlei_name"] = fenlei_name
            yield item

    def get_more(self,response):
        more_url = response.css("#leftNav").xpath("./ul[last()]/li/span/a/@href").get()
        if more_url:
            more_url = "https://www.amazon.cn" + more_url
            fenlei_url = response.url
            item = yamaxun()
            item["fenlei_url"] = fenlei_url
            item["more_url"] = more_url
            yield item

    def get_shanghu(self,response):
        shanghu_list = response.css(".s-see-all-indexbar-column").xpath("./li")
        for shanghu in shanghu_list:
            shanghu_url = shanghu.xpath("./span/a/@href").get()
            if shanghu_url:
                shanghu_url = "https://www.amazon.cn" + shanghu_url
            shanghu_name = shanghu.xpath("./span/a/span/text()").get()
            item = yamaxun()
            item["shanghu_url"] = shanghu_url
            item["shanghu_name"] = shanghu_name
            yield item

    def get_url(self,response):
        url = response.css("#ddmMerchantMessage").xpath("./a/@href").get()
        url = "https://www.amazon.cn"+url
        return scrapy.Request(url=url,callback=self.get_detail,method="GET",dont_filter=True)

    def get_detail(self,response):
        url = response.url
        imfor = response.css(".a-unordered-list.a-nostyle.a-vertical.aagLegalData")
        name = imfor.xpath("./li[1]/text()").get()
        phonenum = imfor.xpath("./li[2]/text()").get()
        information = response.css(".amabot_right").xpath("./p[1]").xpath("string(.)").get()
        if not information:
            information = response.css(".amabot_right").xpath("./p[2]").xpath("string(.)").get()
        if information:
            information = information.strip()

        item = yamaxun()
        item["detailurl"] =url
        item["name"] =name
        item["phonenum"] =phonenum
        item["information"] =information

        return item

