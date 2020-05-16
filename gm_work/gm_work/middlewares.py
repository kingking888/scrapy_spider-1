# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from tools.tools_r.smt.smt_getsign import get_sign
from tools.tools_r.smt.smt_getparam import get_allprame
from tools.tools_r.smt.smt_headers import get_headers
from tools.tools_r.taobao.taobao_sign_h5 import get_taobaosign
from tools.tools_r.header_tool import get_host,headers_todict,reqhead_split,dict_to_cookiesstr
import requests
from scrapy import signals
import os
import re
import time
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.http.response.html import HtmlResponse
import datetime


class NriatSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class NriatSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SmtPrameDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self,crawler):
        self.num = 0
        self.crawler = crawler
        settings = crawler.settings
        self.change_prame()
        self.chang_ip = settings.get("CHANGE_IP_NUM")
        self.username = settings.get("USER_NAME")
        self.password = settings.get("PASSWORD")

    def change_prame(self):
        seller_id = "201122799"
        shop_id = "110173"
        url = "https://m.aliexpress.com/store/v3/home.html?shopId={}&sellerId={}&pagePath=allProduct.htm".format(
            shop_id, seller_id)
        num = 1
        while num < 5:
            num+=1
            try:
                self.prame, self.etag, self.prame3 = get_allprame(shop_id, seller_id, url)  # 这里生成token参数
                break
            except Exception as e:
                print(e)
        else:
            print("参数获取错误超过五次,engine")
            raise Exception()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if spider.name == "smt_goodsid_order" and not request.url.endswith("baidu.com"):
            meta = request.meta
            shop_id = meta.get("shop_id")
            seller_id = meta.get("seller_id")
            page_num = meta.get("page_num")
            if page_num == 1:
                self.num += 1
                if self.num % self.chang_ip == 0:
                    print("换ip换参数")
                    self.crawler.engine.pause()
                    ip_num = 0
                    while ip_num < 5:
                        time.sleep(1)
                        ip_num += 1
                        state = "失败"
                        try:
                            state = self.huan_ip()
                        except Exception as e:
                            print(e)
                        if state == "成功":
                            self.crawler.engine.unpause()
                            break
                        print("换ip错误")
                    else:
                        print("ip切换错误：引擎停止")
                        self.crawler.engine.close()
                    try:
                        self.change_prame()
                    except Exception as e:
                        print("参数切换错误：引擎停止")
                        self.crawler.engine.close()

            prame = self.prame
            etag = self.etag
            prame3 = self.prame3
            url = "https://m.aliexpress.com/store/v3/home.html?shopId={}&sellerId={}&pagePath=allProduct.htm".format(
                shop_id, seller_id)
            # if not prame or not etag or not prame3:
            #     try:
            #         prame, etag, prame3 = get_allprame(shop_id, seller_id, url)  # 这里生成token参数
            #     except Exception as e:
            #         print(e)

            time_str = int(time.time() * 1000)
            appkey = "24770048"
            data = r'''{{"page":{},"pageSize":20,"locale":"en_US","site":"glo","storeId":"{}","country":"US","currency":"USD","aliMemberId":"{}","sort":"orders_desc"}}'''.format(
                page_num, shop_id, seller_id)
            token = prame3.get("_m_h5_tk").split("_")[0]
            sign = get_sign(time_str, appkey, data, token)
            url4 = "https://acs.aliexpress.com/h5/mtop.aliexpress.store.products.search.all/1.0/?jsv=2.4.2&appKey=24770048&t={}&sign={}&api=mtop.aliexpress.store.products.search.all&v=1.0&dataType=json&AntiCreep=true&type=originaljson&data={}".format(
                time_str, sign, data)
            cookies_s = "ali_apache_id={}; xman_us_f=x_l=1; acs_usuc_t={}; xman_t={}; xman_f={}; cna={};_m_h5_tk={}; _m_h5_tk_enc={}".format(
                prame.get("ali_apache_id"), prame.get("acs_usuc_t"), prame.get("xman_t"),
                prame.get("xman_f"), etag, prame3.get("_m_h5_tk"), prame3.get("_m_h5_tk_enc"))
            headers4 = get_headers(3)
            headers4["Host"] = get_host(url4)
            headers4["Referer"] = url
            headers4["Origin"] = "https://m.aliexpress.com"
            headers4["Cookie"] = cookies_s
            request._set_url(url4)
            # request.meta["prame"] = prame
            # request.meta["etag"] = etag
            # request.meta["prame3"] = prame3
            for i in headers4:
                request.headers.setdefault(i,headers4[i])

        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request objectip_c
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def connect(self):
        name = "宽带连接"
        username = self.username
        password = self.password
        cmd_str = "rasdial %s %s %s" % (name, username, password)
        res = os.system(cmd_str)
        if res == 0:
            print("连接成功")
            return "成功"
        else:
            print("连接失败")
            return "失败"

    def disconnect(self):
        name = "宽带连接"
        cmdstr = "rasdial %s /disconnect" % name
        os.system(cmdstr)
        print('断开成功')

    def huan_ip(self):

        # 断开网络
        self.disconnect()
        # 开始拨号
        a = self.connect()
        return a

class TaobaoZhiboDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self,crawler):
        self.num = 0
        self.crawler = crawler
        settings = crawler.settings
        self.cookies_dict = None
        self.change_prame()
        self.chang_ip = settings.get("CHANGE_IP_NUM")
        self.username = settings.get("USER_NAME")
        self.password = settings.get("PASSWORD")


    def change_prame(self, test_id="1714128138"):
        num = 1
        while num < 5:
            num += 1
            self.cookies_dict = self.get_sign1(test_id)
            if self.cookies_dict:
                break
            time.sleep(1)
        else:
            print("参数获取错误超过五次,engine")
            raise Exception()

    def get_sign1(self,sellerid):
        headers1 = self.get_taobao_headers()
        headers1["referer"] = "https://h5.m.taobao.com/taolive/video.html?id={}".format(sellerid)
        url = "https://h5api.m.taobao.com/h5/mtop.mediaplatform.live.videolist/2.0/?jsv=2.4.0&appKey={}&t={}&sign={}&AntiCreep=true&api=mtop.mediaplatform.live.videolist&v=2.0&type=jsonp&dataType=jsonp&timeout=20000&callback=mtopjsonp1&data=%7B%7D"
        time_now = str(int(time.time() * 1000))
        appkey = "12574478"
        data = '{}'
        sign = get_taobaosign(time=time_now, appKey=appkey, data=data)
        url = url.format(appkey, time_now, sign)
        try:
            req = requests.get(url=url, headers=headers1)
            headers_rep = req.headers
            set_cookiesstr = headers_rep.get("set-cookie")
            set_cookies = reqhead_split(set_cookiesstr)
            cookies_dict = dict()
            cookies_dict["t"] = set_cookies.get("t", "")
            cookies_dict["_m_h5_tk"] = set_cookies.get("_m_h5_tk", "")
            cookies_dict["_m_h5_tk_enc"] = set_cookies.get("_m_h5_tk_enc", "")
            if cookies_dict.get("t") and cookies_dict.get("_m_h5_tk") and cookies_dict.get("_m_h5_tk_enc"):
                return cookies_dict
        except Exception as e:
            pass

    def get_taobao_headers(self):
        headers = '''accept: */*
        accept-encoding: gzip, deflate, br
        accept-language: zh-CN,zh;q=0.9
        cache-control: no-cache
        pragma: no-cache
        sec-fetch-mode: no-cors
        sec-fetch-site: same-site
        user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
        return headers_todict(headers)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if spider.name == "taobao_zhiboinfo" and not request.url.endswith("baidu.com"):
            meta = request.meta
            sellerid = meta.get("seller_id")
            self.num += 1
            if self.num % self.chang_ip == 0:
                print("换ip换参数")
                self.crawler.engine.pause()
                ip_num = 0
                while ip_num < 5:
                    time.sleep(1)
                    ip_num += 1
                    state = "失败"
                    try:
                        state = "成功"#self.huan_ip()
                    except Exception as e:
                        print(e)
                    if state == "成功":
                        break
                    print("换ip错误")
                else:
                    print("ip切换错误：引擎停止")
                    self.crawler.engine.close()
                try:
                    self.change_prame()
                    self.crawler.engine.unpause()
                except Exception as e:
                    print("参数切换错误：引擎停止")
                    self.crawler.engine.close()

            headers2 = self.get_taobao_headers()
            headers2["referer"] = "https://tblive.m.taobao.com/wow/tblive/act/host-detail?wh_weex=true&broadcasterId={}".format(sellerid)  # broadcasterId
            cookeis = dict_to_cookiesstr(self.cookies_dict)
            headers2["Cookie"] = cookeis
            time_now = str(int(time.time() * 1000))
            appkey = "12574478"
            data = '{{"broadcasterId":"{}","start":0,"limit":10}}'.format(sellerid)  #broadcasterId
            sign_token = self.cookies_dict.get("_m_h5_tk").split("_")[0]
            sign = get_taobaosign(time=time_now, appKey=appkey, data=data, token=sign_token)
            url2 = "https://h5api.m.taobao.com/h5/mtop.mediaplatform.anchor.info/1.0/?jsv=2.4.8&appKey={}&t={}&sign={}&api=mtop.mediaplatform.anchor.info&v=1.0&AntiCreep=true&AntiFlood=true&type=jsonp&dataType=jsonp&callback=mtopjsonp3&data=%7B%22broadcasterId%22%3A%22{}%22%2C%22start%22%3A0%2C%22limit%22%3A10%7D"

            url2 = url2.format(appkey, time_now, sign, sellerid)

            request._set_url(url2)
            for i in headers2:
                request.headers[i] = headers2[i]#.setdefault(i,headers2[i])
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request objectip_c
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def connect(self):
        name = "宽带连接"
        username = self.username
        password = self.password
        cmd_str = "rasdial %s %s %s" % (name, username, password)
        res = os.system(cmd_str)
        if res == 0:
            print("连接成功")
            return "成功"
        else:
            print("连接失败")
            return "失败"

    def disconnect(self):
        name = "宽带连接"
        cmdstr = "rasdial %s /disconnect" % name
        os.system(cmdstr)
        print('断开成功')

    def huan_ip(self):

        # 断开网络
        self.disconnect()
        # 开始拨号
        a = self.connect()
        return a

class IpChangeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self,crawler):
        self.crawler = crawler
        settings = crawler.settings
        self.num = 0
        self.chang_ip = settings.get("CHANGE_IP_NUM")
        self.username = settings.get("USER_NAME")
        self.password = settings.get("PASSWORD")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        change_num = self.chang_ip
        self.num += 1
        if self.num % change_num == 0:
            # print("换ip换参数")
            self.crawler.engine.pause()
            ip_num = 0
            while ip_num < 5:
                time.sleep(1)
                ip_num += 1
                state = "失败"
                try:
                    state = self.huan_ip()
                except Exception as e:
                    print(e)
                if state == "成功":
                    self.crawler.engine.unpause()
                    break
            else:
                print("ip切换错误：引擎停止")
                self.crawler.engine.close()
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        # Must either;
        # - return a Response object
        # - return a Request objectip_c
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def connect(self):
        name = "宽带连接"
        username = self.username
        password = self.password
        cmd_str = "rasdial %s %s %s" % (name, username, password)
        res = os.system(cmd_str)
        if res == 0:
            print("连接成功")
            return "成功"
        else:
            print("连接失败")
            return "失败"

    def disconnect(self):
        name = "宽带连接"
        cmdstr = "rasdial %s /disconnect" % name
        os.system(cmdstr)
        print('断开成功')

    def huan_ip(self):

        # 断开网络
        self.disconnect()
        # 开始拨号
        a = self.connect()
        return a

class HostDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        url = request.url
        match = re.search("//(.*?)[/$]",url)
        if match:
            host_new = match.group(1)
            request.headers["Host"] = host_new
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request objectip_c
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UpdatetimeMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def process_request(self, request, spider):
        today = datetime.date.today().strftime("%Y-%m-%d")
        tomorrow = (datetime.date.today()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        data = request.body.decode()
        data = data.replace("入住时间",today)
        data = data.replace("离店时间",tomorrow)
        request._set_body(data)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request objectip_c
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass


class ProcessAllExceptionMiddleware(object):
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    def process_response(self, request, response, spider):
        # 捕获状态码为40x/50x的response
        # if str(response.status).startswith('4') or str(response.status).startswith('5'):
        #     # 随意封装，直接返回response，spider代码中根据url==''来处理response
        #     response = HtmlResponse(url='')
        #     return response

        # 其他状态码不处理
        return response

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            print('Got exception: %s %s' % (request.url,exception))
            # 随意封装一个response，返回给spider
            response = HtmlResponse(url='exception')
            return response

        # 打印出未捕获到的异常
        print('not contained exception: %s' % exception)