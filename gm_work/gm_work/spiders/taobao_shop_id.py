# -*- coding: utf-8 -*-
import scrapy
from tools.tools_r.header_tool import headers_todict
from gm_work.items import taobao
import re

class SuduTestSpider(scrapy.Spider):
    name = 'taobao_shopid'
    allowed_domains = []
    redis_key = "taobao:start_url"
    id_start = 101717810
    id_end = 101717810

    def start_requests(self):
        headers_str = '''User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36'''
        headers = headers_todict(headers_str)

        # for i in range(self.id_start,self.id_end+1):
        for i in [101717810, 57472900, 10000366]:
            url = "https://count.taobao.com/counter3?callback=jsonp102&keys=SCCP_2_{}".format(i)
            yield scrapy.Request(url=url, callback=self.parse_shopid, method="GET", headers=headers,meta={"shop_id":i})

    def parse_shopid(self,response):
        youxiao = 'jsonp102({"SCCP'
        text = response.text
        if youxiao in text:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            item_s = taobao()
            item_s["source_code"] = text
            item_s["pipeline_level"] = "店铺扫描"

            yield item_s
            meta = response.meta
            shop_id = meta.get("shop_id")

            zhuangtai_s = self.match_zhengze('"SCCP_2_[^"]*":([^\}]*)\}',text)
            item = taobao()
            item["zhuangtai"] = zhuangtai_s
            item["shop_id"] = shop_id
            item["pipeline_level"] = "店铺扫描"
            yield item

            if int(zhuangtai_s) > 0:#这里判断
                url = "http://shop.m.taobao.com/shop/shop_info.htm?shop_id={}&tbpm=3"
                url = url.format(shop_id)
                headers_str = '''User-Agent:Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25'''
                headers = headers_todict(headers_str)
                yield scrapy.Request(url=url, callback=self.parse_shopxinyong, method="GET", headers=headers,meta={"shop_id":shop_id})#手机信用

        else:
            request = self.try_again(response)
            if request:
                yield request

    def parse_shopxinyong(self,response):
        text = response.text
        youxiao = '(您浏览店铺不存在|没有找到相应的店铺|店主被删除或冻结了|掌柜|您查看的页面找不到了|Location:http://\.m\.tmall\.com|com/error1\.html|//chaoshi[a-z]*\.m\.tmall|//aliqin\.tmall|//a\.m\.tmall|modbundle-start)'
        youxiao_m = re.search(youxiao,text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            item_s = taobao()
            item_s["source_code"] = text
            item_s["pipeline_level"] = "手机店铺信用"

            yield item_s
            meta = response.meta
            shop_id = meta.get("shop_id")

            zhuangtai_s = self.match_zhengze('(店铺不存在|没有找到|掌柜|删除或冻结|Location:http://[^\.]*\.m\.tmall)',text)#状态
            shop_id_s = self.match_zhengze('shop_id=([^"#;]*)"|shopId = "([^#"]*)";',text)#店铺ID
            sellerid_s = self.match_zhengze('''data-suid='([^']*)'|seller_id=([^"]*)"''',text)#卖家ID
            zhanggui_s = self.match_zhengze('>掌柜ID</label>([\s\S]+?)<div ',text)#掌柜
            nickurl_s = self.match_zhengze('nick = ([ ^ "]*)"',text)#nickurl
            nick_s = self.match_zhengze('"nick":"([^"]*)",',text)#nick
            shop_name_s = self.match_zhengze('title>([\s\S]+?)</titl',text)#店铺名称
            haoping_s = self.match_zhengze('好评率：([^<]*)<',text)#好评率
            miaoshuxf_s = self.match_zhengze('描述相符</label>([^<]*)<',text)#描述相符
            fuwutd_s = self.match_zhengze('服务态度</label>([^<]*)<',text)#服务态度
            fahuosd_s = self.match_zhengze('发货速度</label>([^<]*)<',text)#发货速度
            area_s = self.match_zhengze('label>地区</label>([\s\S]+?)</li>',text)#所在地区
            phone_s = self.match_zhengze("客服电话：<[^>]*>([^<]*)<",text)#客服电话
            shopurl_s = self.match_zhengze('"shopUrl":"([^"]*)"',text)#shopUrl

            item = taobao()
            item["shop_id_key"] = shop_id
            item["zhuangtai"] = zhuangtai_s
            item["seller_id"] = sellerid_s
            item["shop_id"] = shop_id_s
            item["zhanggui"] = zhanggui_s
            item["nickurl"] = nickurl_s
            item["nick"] = nick_s
            item["shop_name"] = shop_name_s
            item["haoping"] = haoping_s
            item["miaoshuxf"] = miaoshuxf_s
            item["fuwutd"] = fuwutd_s
            item["fahuosd"] = fahuosd_s
            item["area"] = area_s
            item["phone"] = phone_s
            item["shopurl"] = shopurl_s
            item["pipeline_level"] = "手机店铺信用"
            yield item

        else:
            request = self.try_again(response)
            if request:
                yield request



    def match_zhengze(self,zz_str,text):
        str_m = re.search(zz_str, text)
        clomunus = str_m.group(str_m.lastindex) if str_m else ""
        return clomunus.strip()

    def try_again(self,rsp):
        max_num = 5
        meta = rsp.meta
        try_num = meta.get("try_num",0)
        if try_num < max_num:
            try_num += 1
            request = rsp.request
            request.dont_filter = True
            request.meta["try_num"] = try_num
            return request