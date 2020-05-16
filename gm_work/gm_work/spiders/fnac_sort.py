# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re


class FnacSpider(RedisSpider):
    name = 'fnac_sort'
    allowed_domains = ['fnac.com']
    start_urls = ['https://www.fnac.com']
    redis_key = "fnac_sort:start_url"

    def start_requests(self):
        url = "https://www.fnac.com"
        headers = self.get_headers(1)
        yield scrapy.Request(url=url,method="GET",callback=self.sort_first,headers=headers,dont_filter=True)

    def sort_first(self,response):
        youxiao = re.search("(livre.asp)",response.text)
        url = response.url
        if youxiao:
            sort_list = response.css(".CategoryNav-link.js-CategoryNav-link")
            headers = self.get_headers(1)
            for i in sort_list:
                url = i.xpath("./@href").get()
                name = i.xpath("./text()").get()
                if "www.fnac.com" in url:
                    yield scrapy.Request(url=url,method="GET",callback=self.sort_second,headers=headers,dont_filter=True
                                         ,meta={"sort":[name]})
                else:
                    print(name)
        else:
            try_result = self.try_again(response,key="1", url=url)
            yield try_result

    def sort_second(self,response):
        youxiao = re.search("(category-menu)",response.text)#判断是否出现左边导航列表
        youxiao1 = re.search("(js-Search-titleCount)",response.text)#判断是否出现good列表
        sort = response.meta.get("sort")
        if youxiao1:
            self.get_list(response,youxiao1)
            item = GmWorkItem()
            item["sort"] = str(sort)
            item["url"] = response.url
        else:
            url = response.url
            if youxiao:
                headers = self.get_headers(1)
                sort_list = response.css(".category-menu").xpath("./dl/dd//a")
                for i in sort_list:
                    sort_copy = sort.copy()
                    url = i.xpath("./@href").get()
                    name = i.xpath("./text()").get()
                    if re.search("\w",name) and name not in sort_copy:
                        sort_copy.append(name)
                        item = GmWorkItem()
                        item["sort"] = str(sort_copy)
                        item["url"] = url
                        yield item
                        yield scrapy.Request(url=url, method="GET", callback=self.sort_second, headers=headers,
                                         dont_filter=True, meta={"sort":sort_copy})
            else:
                try_result = self.try_again(response,key=str(sort),url=url)
                yield try_result

    def get_list(self,response,youxiao=None):
        if not youxiao:
            youxiao = re.search("(js-Search-titleCount)",response.text)
        if youxiao:
            url = response.url
            category_list = []
            page_num = response.meta.get("page_num")
            headers = self.get_headers(1)
            category = response.css(".Breadcrumb-list").xpath("./li")
            for i in category:
                category = i.xpath("./a/span/text()").get()
                if not category:
                    category = i.xpath("./span[2]/text()").get()
                if category:
                    category_list.append(category)
            count = response.css(".Search-titleCount.js-Search-titleCount").xpath("./text()").get()
            if count:
                match = re.search("\((\d*)\)", count)
                count = 0
                if match:
                    count = match.group(1)
            goods_list = response.css(".clearfix.Article-item.js-Search-hashLinkId")
            for i in goods_list:
                good_url = i.css(".Article-desc").xpath("./span/a/@href").get()
                good_name = i.css(".Article-desc").xpath("./span/a/text()").get()
                good_id = i.xpath("./@id").get()
                score = i.css(".Article-rate.js-bestReview").xpath("./span/span[1]/text()").get()
                score_number = i.css(".Article-rate.js-bestReview").xpath("./span/span[2]/text()").get()
                if score_number:
                    match = re.search("\((.*?)\)",score_number)
                    if match:
                        score_number = match.group(1)
                price = i.css(".userPrice").xpath("./text()").get()
                if price:
                    price = price.strip()
                goodshop_url = i.css(".OffersSumary.clearfix").xpath("./a/@href").get()
                item = GmWorkItem()
                item["good_url"] = good_url
                item["good_name"] = good_name
                item["good_id"] = good_id
                item["score"] = score
                item["score_number"] = score_number
                item["price"] = price
                item["goodshop_url"] = goodshop_url
                item["category"] = str(category)
                # yield item
            # if not page_num and count and int(count) > 20:
            #     page_num = int(int(count)/20) if int(count)%20 else int(int(count)/20)-1
            #     for i in range(2,page_num+2):
            #
            #         next_url = url+"?PageIndex={}&sl".format(i)
            #         yield scrapy.Request(url=next_url, method="GET", callback=self.get_list, headers=headers,
            #                              meta={"page_num":i},dont_filter=True)

    def try_again(self,rsp,**kwargs):
        print("cuowu")
        max_num = -1
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
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
cookie: akavpau_FRPRD_FNACCOM=1579504176~id=c47606a9252db9ae6b6424077f58d7e4; datadome=Y7k9tjHyvrXoo9-JIl5bDmSAvRSDneVG1e2pruOX.vUcQykUqMFxcqF_W7-lpxQy30ef45kU2gL.z9B_mFruvO5aaeLL81KaW3KQe70COl
pragma: no-cache
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        else:
            headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
                        accept-encoding: gzip, deflate, br
                        accept-language: zh-CN,zh;q=0.9
                        upgrade-insecure-requests: 1
                        user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
        return headers_todict(headers)