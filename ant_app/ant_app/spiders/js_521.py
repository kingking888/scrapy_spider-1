# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
#import execjs.runtime_names

class Js521Spider(RedisSpider):
    name = 'js_521'

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "HTTPERROR_ALLOWED_CODES": [200, 521],  # 允许在此列表中的非200状态代码响应
    }
    redis_key = "js_521:start_url"
    def start_requests(self):
        url = "http://www.cbrc.gov.cn/chinese/newListDoc/111003/1.html"
        headers = self.get_headers(1)  # 可以添加headers
        yield scrapy.Request(url, callback=self.parse, method="GET", headers=headers, dont_filter=True)
    # def make_requests_from_url(self, url):#对初始的种子进行处理
    #     headers = self.get_headers(1)#可以添加headers
    #     return scrapy.Request(url,callback=self.parse,method="GET",headers=headers,dont_filter=True)

    def parse(self,response):#回调函数,见test中的js521.py
        content = response.text
        text = content.replace("<script>","")
        text = text.replace("</script>","")

        js_str1 = "function _log(x){ new Function(x); return x;};function getEvalCode(){var result;"+text+"return result;}"
        js_str1 = js_str1.replace("eval","result = _log")
        #js_str1 = repr(js_str1)[1:-1]
        # na = execjs.runtime_names.Node
        # node = execjs.get(na)
        # js_s = node.compile(js_str1)
        # js_str2 = js_s.call("getEvalCode")
        print(text)
        print(js_str1)
        # print(js_str2)


    def get_headers(self,num):
        if num == 1:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection":"keep-alive",
                "Host": "www.cbrc.gov.cn",
                "Upgrade-Insecure-Requests":"1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            }
        else:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Host": "www.cbrc.gov.cn",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            }
        return headers


