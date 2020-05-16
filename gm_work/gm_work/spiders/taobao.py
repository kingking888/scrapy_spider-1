# -*- coding: utf-8 -*-
import scrapy
from tools.tools_r.header_tool import headers_todict
from gm_work.items import taobao
import re

class SuduTestSpider(scrapy.Spider):
    name = 'taobao'
    allowed_domains = []
    redis_key = "taobao:start_url"
    id_start = 101717810
    id_end = 101717810

    def start_requests(self):
        headers_str = '''User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36'''
        headers = headers_todict(headers_str)

        # for i in range(self.id_start,self.id_end+1):
        for i in [101717810,57472900,10000366]:

            url = "https://count.taobao.com/counter3?callback=jsonp102&keys=SCCP_2_{}".format(i)
            yield scrapy.Request(url=url, callback=self.parse_shopid, method="GET", headers=headers,meta={"shop_id":i})

        # item_id_s = "599176795701"#test商品信息
        # seller_id_s = "1114511827"
        #
        # url1 = "https://item.taobao.com/item.htm?id={}"
        # headers1 = '''User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36'''
        # if item_id_s:
        #     url = url.format(item_id_s)
        #     headers = request_tools.headers_todict(headers)
        #     yield scrapy.Request(url=url, callback=self.parse_goods_xiaoliang, method="GET", headers=headers,
        #                      meta={"item_id_s": item_id_s})
        #     url1 = url1.format(item_id_s)#
        #     headers1 = request_tools.headers_todict(headers1)
        #     yield scrapy.Request(url=url1, callback=self.parse_good_information, method="GET", headers=headers1, meta={"item_id_s": item_id_s,"seller_id":seller_id_s})#商品详情


    def parse_shopid(self,response):
        youxiao = 'jsonp102({"SCCP'
        text = response.text
        if youxiao in text:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            shop_id = meta.get("shop_id")

            zhuangtai_s = self.match_zhengze('"SCCP_2_[^"]*":([^\}]*)\}',text)
            item = taobao()
            item["zhuangtai"] = zhuangtai_s
            item["pipeline_level"] = "店铺扫描"
            yield item

            if int(zhuangtai_s) > 0:#这里判断
                url = "http://shop.m.taobao.com/shop/shop_info.htm?shop_id={}&tbpm=3"
                url = url.format(shop_id)
                headers_str = '''User-Agent:Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25'''
                headers = headers_todict(headers_str)
                yield scrapy.Request(url=url, callback=self.parse_shopxinyong, method="GET", headers=headers,meta={"shop_id":shop_id})#手机信用

                url_tui = "https://tui.taobao.com/recommend?shop_id={}&floorId=42296&appid=6862"
                url_tui = url_tui.format(shop_id)
                headers_tui_str = "User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36"
                headers2 = headers_todict(headers_tui_str)
                yield scrapy.Request(url=url_tui, callback=self.parse_tui_diannao, method="GET", headers=headers2,meta={"shop_id": shop_id})#店铺tui
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

            if sellerid_s:
                url_1 = "https://ext-mdskip.taobao.com/extension/seller_info.htm?user_num_id={}"
                headers = '''User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36
                                    Referer:https://www.taobao.com'''
                url_1 = url_1.format(sellerid_s)
                headers = headers_todict(headers)
                yield scrapy.Request(url=url_1, callback=self.main_sale, method="GET", headers=headers,meta={"seller_id": sellerid_s})#主营
                url_2 = "https://count.taobao.com/counter3?keys=SM_368_dsr-{}&callback=jsonp173"
                headers = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36"
                url_2 = url_2.format(sellerid_s)
                headers = headers_todict(headers)
                yield scrapy.Request(url=url_2, callback=self.parse_shopxinyong_diannao, method="GET", headers=headers,meta={"seller_id": sellerid_s})  # 公司信用_电脑端

                asyn_url = "http://hdc1.alicdn.com/asyn.htm?userId={}&pageId=&v=2014"
                headers = "User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36"
                asyn_url = asyn_url.format(sellerid_s)
                headers = headers_todict(headers)
                yield scrapy.Request(url=asyn_url, callback=self.parse_asyn_good, method="GET", headers=headers,meta={"shop_id": shop_id})

        else:
            request = self.try_again(response)
            if request:
                yield request

    def main_sale(self,response):
        text = response.text
        youxiao = '(店铺动态评分|大小:7[;]{1,}[\s]*<|服务质量记录|NullPointerException)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            seller_id = meta.get("seller_id")

            main_sale_id_s = self.match_zhengze("所属行业：([^\)]*)\)",text)#主营
            miaoshu_pf_s = self.match_zhengze('商品与描述相符：</span><em class="count" title="([^分]*)分"', text)#描述评分这里的正则</span><em去了空格
            fuwu_pf_s = self.match_zhengze('商家的服务态度：</span><em class="count" title="([^分]*)分"', text)  # 服务评分
            wuliu_pf_s = self.match_zhengze('商家发货的速度：</span><em class="count" title="([^分]*)分"', text)  # 物流评分
            item = taobao()
            item["main_sale_id"] = main_sale_id_s
            item["miaoshu_pf_s"] = miaoshu_pf_s
            item["fuwu_pf_s"] = fuwu_pf_s
            item["wuliu_pf_s"] = wuliu_pf_s
            item["pipeline_level"] = "淘宝天猫主营"
            yield item
        else:
            request = self.try_again(response)
            if request:
                yield request

    def parse_shopxinyong_diannao(self,response):#11
        text = response.text
        youxiao = '(jsonp173\({"SM_368)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            seller_id = meta.get("seller_id")

            seller_id_s = self.match_zhengze('"SM_368_dsr-([0-9]*)', text)#卖家ID
            v_id_s = self.match_zhengze('{v:([^,]*),', text)#v
            nv_id_s = self.match_zhengze('nv:([^,]*),', text)#nv
            miaoshu_ufb_s = self.match_zhengze('m_UFB:([^,]*),', text)#描述_UFB_0高_1_2低
            miaoshu_s = self.match_zhengze('m:([^,]*),', text)#描述评分
            miaoshu_th_s = self.match_zhengze('m_g:([^,]*),', text)#描述比同行
            fuwu_ufb_s = self.match_zhengze('s_UFB:([^,]*),', text)#服务_UFB_0高_1_2低
            fuwu_s = self.match_zhengze(',s:([^,]*),', text)#服务评分
            fuwu_th_s = self.match_zhengze('s_g:([^,]*),', text)#服务比同行
            wuliu_ufb_s = self.match_zhengze('c_UFB:([^,]*),', text)#物流_UFB_0高_1_2低
            wuliu_s = self.match_zhengze('c:([^,]*),', text)#物流评分
            wuliu_th_s = self.match_zhengze('c_g:([^,]*),', text)#物流比同行
            shop_haoping_s = self.match_zhengze('gp:([^,]*),', text)#店铺好评率
            seller_xinyong_s = self.match_zhengze('ss:([0-9]*),', text)#卖家信用
            pingfeng_s = self.match_zhengze('hdr:([^}]*)}', text)#是否有评分
            item = taobao()
            item["seller_id"] = seller_id_s
            item["v_id"] = v_id_s
            item["nv_id"] = nv_id_s
            item["miaoshu_ufb"] = miaoshu_ufb_s
            item["miaoshu"] = miaoshu_s
            item["miaoshu_th"] = miaoshu_th_s
            item["fuwu_ufb"] = fuwu_ufb_s
            item["fuwu"] = fuwu_s
            item["fuwu_th"] = fuwu_th_s
            item["wuliu_ufb"] = wuliu_ufb_s
            item["wuliu"] = wuliu_s
            item["wuliu_th"] = wuliu_th_s
            item["shop_haoping"] = shop_haoping_s
            item["seller_xinyong"] = seller_xinyong_s
            item["pingfeng"] = pingfeng_s
            item["pipeline_level"] = "天猫店铺信用"
            yield item

        else:
            request = self.try_again(response)
            if request:
                yield request

    def parse_tui_diannao(self, response):
        text = response.text
        youxiao = '("itemId"|"result":\[\])'
        youxiao_m = re.search(youxiao, text)

        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            shop_id = meta.get("shop_id")

            url1 = "https://tui.taobao.com/recommend?shop_id={}&item_ids={}&floorId=42296&pSize=12&callback=detail_pine&appid=6862&count=12&pNum=0"
            headers1 = '''Referer: https://item.taobao.com/item.htm?id=590354499275
            User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36'''
            fenlie = "},{"
            for i in text.split(fenlie):
                text_s = i
                shop_type_s = self.match_zhengze('"userType":[\s]*["]{0,1}([^",\}]*)', text_s)
                shop_id_s = self.match_zhengze('"shopId":[\s]*["]{0,1}([^",\}]*)', text_s)
                seller_id_s = self.match_zhengze('"sellerId":[\s]*["]{0,1}([^",\}]*)', text_s)
                item_id_s = self.match_zhengze('"itemId":[\s]*["]{0,1}([^",\}]*)', text_s)
                good_name_s = self.match_zhengze('"itemName":"([\s\S]+?)",', text_s)#UTF8
                price_s = self.match_zhengze('"price":[\s]*["]{0,1}([^",\}]*)', text_s)
                promotion_price_s = self.match_zhengze('"promotionPriceRaw":[\s]*["]{0,1}([^",\}]*)', text_s)
                sell_count_s = self.match_zhengze('"sellCount":[\s]*["]{0,1}([^",\}]*)', text_s)
                mouth_count_s = self.match_zhengze('"monthSellCount": [\s]*["]{0,1}([^",\}] * )', text_s)
                quantity_s = self.match_zhengze('"quantity":[\s]*["]{0,1}([^",\}]*)', text_s)
                favor_count_s = self.match_zhengze('"favorCount":[\s]*["]{0,1}([^",\}]*)', text_s)
                brand_id_s = self.match_zhengze('"brandId":([0-9]*)', text_s)
                category_id_s = self.match_zhengze('"categoryId":[\s]*["]{0,1}([^",\}]*)', text_s)
                category_id_lv1_s = self.match_zhengze('"categoryLv1Id":[\s]*["]{0,1}([^",\}]*)', text_s)
                sub_item_name_s = self.match_zhengze('"subItemName":[\s]*["]{0,1}([^",\}]*)', text_s)
                pic_s = self.match_zhengze('"pic":[\s]*["]{0,1}([^",\}]*)', text_s)
                item = taobao()
                item["shop_type"] = shop_type_s
                item["shop_id"] = shop_id_s
                item["seller_id"] = seller_id_s
                item["good_name"] = good_name_s
                item["price"] = price_s
                item["promotion_price"] = promotion_price_s
                item["sell_count"] = sell_count_s
                item["mouth_count"] = mouth_count_s
                item["quantity"] = quantity_s
                item["favor_count"] = favor_count_s
                item["brand_id"] = brand_id_s
                item["category_id"] = category_id_s
                item["category_id_lv1"] = category_id_lv1_s
                item["sub_item_name"] = sub_item_name_s
                item["pic"] = pic_s
                item["pipeline_level"] = "tui店铺"
                yield item
                if item_id_s:
                    url =url1.format(shop_id,item_id_s)
                    headers = headers_todict(headers1)
                    yield scrapy.Request(url=url, callback=self.parse_kanleyoukan, method="GET", headers=headers,meta={"shop_id": shop_id,"item_id":item_id_s})
        else:
            request = self.try_again(response)
            if request:
                yield request


    def parse_asyn_good(self,response):
        text = response.text
        youxiao = '(s-maxage=5|"userId":)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            shop_id = meta.get("shop_id")
            headers1 = '''Referer: https://item.taobao.com/item.htm?id=590354499275
            User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36'''
            url1 = "https://tui.taobao.com/recommend?shop_id={}&item_ids={}&floorId=42296&pSize=12&callback=detail_pine&appid=6862&count=12&pNum=0"

            fenlie = "},{"
            for i in text.split(fenlie):
                text_s = i
                item_id_s = self.match_zhengze('item\.htm\?id=([0-9]*)', text_s)#商品ID
                item_name_s = self.match_zhengze(r'title=\\"([\s\S]+?)\\"|class=\\"desc\\"><a[^>]*target=\\"_blank\\"[^>]*>([\s\S]+?)</a>', text_s)
                price_s = self.match_zhengze(r'class=\\"price\\"[^>]*>￥<spa[^>]*>([^<]*)</span>', text_s)
                mouth_count_s = self.match_zhengze(r'sale-count\\"[^>]*>([^<]*)<', text_s)
                item = taobao()
                item["item_id"] = item_id_s
                item["item_name"] = item_name_s
                item["price"] = price_s
                item["mouth_count"] = mouth_count_s
                item["pipeline_level"] = "asyn商品"
                yield item

                if item_id_s:
                    url =url1.format(shop_id,item_id_s)
                    headers = request_tools.headers_todict(headers1)
                    yield scrapy.Request(url=url, callback=self.parse_kanleyoukan, method="GET", headers=headers,meta={"shop_id": shop_id,"item_id_s":item_id_s})

            biuaoshi_s = self.match_zhengze('"categoryName":"([^"]*)', text)#标识
            gongsibs_s = self.match_zhengze('(工商执照)：', text)#公司标识
            shop_id_s = self.match_zhengze('sid([0-9]{1,})_', text)#店铺ID
            seller_id_s = self.match_zhengze(r'dsr-userid\\" value=\\"([0-9]{1,})|"userId":([0-9]{1,})', text)#卖家ID
            company_name_s = self.match_zhengze(r'公 司 名：[^<]*</label>[^<]*<[^>]*>[^\s]*([^\\]*)', text)#公司名称UTF8
            shop_name_s = self.match_zhengze(r'shop-name-title\\" title=\\"([^"]*)"|class=\\"shop-name\\"[^>]*><span>([^>]*)<', text)#店铺名称
            pingfeng_s = self.match_zhengze('(该店铺尚未收到评价|该店尚未收到评价)', text)#评分标识
            miaoshu_s = self.match_zhengze('>描述</span>[\s\S]+?<em>([^<]*)</em>|描述相符：<a[^>]*>[^>]*<em[^>]*>([^>]*)</em>|描述相符<em[^>]*>([^>]*)</em>', text)#描述
            fuwu_s = self.match_zhengze('>服务</span>[\s\S]+?<em>([^<]*)</em>|服务态度：<a[^>]*>[^>]*<em[^>]*>([^>]*)</em>|服务态度<em[^>]*>([^>]*)</em>', text)#服务
            wuliu_s = self.match_zhengze('>物流</span>[\s\S]+?<em>([^<]*)</em>|发货速度：<a[^>]*>[^>]*<em[^>]*>([^>]*)</em>|物流服务<em[^>]*>([^>]*)</em>', text)#物流
            seller_name_s = self.match_zhengze(r'data-nick=\\"([^"]*)"', text)#卖家用户名 URL
            baozhengjin_s = self.match_zhengze(r'tb-seller-bail\\"><i></i>([^<]*)</span>|J_TotalBailAmount\\">([^<]*)</span>保证金', text)#保证金UTF8|去中间空字符
            lianxifanshi_s = self.match_zhengze(r'<h4>联系方式</h4>[^<]*<ul class=\\"service-content\\">([\s\S]+?)</ul>', text)#联系方式UTF8|去HTML标签
            zhutibg_s = self.match_zhengze('>主体变更：</span>([^<]*)</p>', text)#主体变更UTF8
            item1 = taobao()
            item1["biuaoshi"] = biuaoshi_s
            item1["gongsibs"] = gongsibs_s
            item1["shop_id"] = shop_id_s
            item1["seller_id"] = seller_id_s
            item1["company_name"] = company_name_s
            item1["shop_name"] = shop_name_s
            item1["pingfeng"] = pingfeng_s
            item1["miaoshu"] = miaoshu_s
            item1["fuwu"] = fuwu_s
            item1["wuliu"] = wuliu_s
            item1["seller_name"] = seller_name_s
            item1["baozhengjin"] = baozhengjin_s
            item1["lianxifanshi"] = lianxifanshi_s
            item1["zhutibg"] = zhutibg_s
            item1["pipeline_level"] = "asyn商店"
            yield item1
        else:
            request = self.try_again(response)
            if request:
                yield request

    def parse_kanleyoukan(self,response):
        text = response.text
        youxiao = '(detail_pine)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            shop_id = meta.get("shop_id")
            item_id = meta.get("item_id")

            url2= '''https://mdskip.taobao.com/core/initItemDetail.htm?isUseInventoryCenter=false&cartEnable=true&service3C=false&isApparel=false&isSecKill=false&tmallBuySupport=true&isAreaSell=false&tryBeforeBuy=false&offlineShop=false&itemId={}&showShopProm=false&isPurchaseMallPage=false&itemGmtModified=1568217644000&isRegionLevel=false&household=false&sellerPreview=false&queryMemberRight=true&addressLevel=2&isForbidBuyItem=false&callback=setMdskip&timestamp=1568612546869'''
            headers2 = '''User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36
            Referer: https://detail.tmall.com/item.htm?id=585627813748
            Cookie:t=771e985ad68867dca634b66c8b52c710; cna=RxThFT+HtVACATyweW2UU3HN; tracknick=%5Cu4E09%5Cu9014%5Cu6CB3%5Cu8FD8%5Cu662F%5Cu5929%5Cu5802; _cc_=URm48syIZQ%3D%3D; enc=5DlFftlD20fPoNrYGejylp4qjVAwaVqHVif222OGfTVcQTqAx2FMz1Zq21yB5qgS%2FwJtxLSsCsnMVvodBHNseg%3D%3D; thw=cn; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; hng=CN%7Czh-CN%7CCNY%7C156; cookie2=1cf7677466b3b4247ee06b58db60af76; _tb_token_=3bebd4e0eb356; v=0; mt=ci%3D-1_1; miid=1514173119299498437; uc1=cookie14=UoTbnKMDmEcUIg%3D%3D; tk_trace=oTRxOWSBNwn9dPyorMJE%2FoPdY8zZPEr%2FCrvCMS%2BG3sTRRWrQ%2BVVTl09ME1KrXdS91s4jJYL5NA7c2uWyfyw%2F9gYrem7NEW7%2FhRF2%2BDZyzjzJUQM%2B3ajmc%2BqsNRORcaRH3CNHyGPkcc%2F%2BLjMbn8%2FEPT%2FB8BQzJOUzWHeXEfYMACGjSPsry1CB514xsVVKb7xQpGcujL%2FGqsEgBrb1wz3x5x7vG9V5OAdii7QZqPQIrqC92RZGPM2m943EN8TkLKCavVsJtrfVF%2B2rncH0VPQJbqgCp1b7IcFLp4aV1X2Gt2nDZo4%2BPKkcowzbgNV4LUNTu6ynXBPWBq0RDDlOX%2FY1ucI%3D; linezing_session=1jM55aS1rIVc20jqjpDgyWCs_1571208987345cSbM_6; _m_h5_tk=3756ebaa20d617d7e1fc48cec3e82ad6_1571233351866; _m_h5_tk_enc=8a6d0092297b00d8f43562a95fa43ddf; l=dBgt4Jcmq1sEN_vbBOCZnurza779sIRAguPzaNbMi_5IL18suR7OkgjmxeJ6cjWfTlYB4dG4psJ9-etkZ4eT6qM8sxAJNxDc.; isg=BJqaNiC5kzLEHR9lMWc-xLee60C8yx6lNJSpOKQTRy34FzpRjFiZtWll46Mux5Y9'''

            url1 = "https://item.taobao.com/item.htm?id={}"
            headers1 = '''User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36'''
            fenlie = "},{"
            for i in text.split(fenlie):
                text_i = i
                item_id_s = self.match_zhengze(r'itemId\":(\d+)', text_i)#商品ID
                seller_id_s = self.match_zhengze('sellerId":(\d+)', text_i)#卖家ID
                cate_id_s = self.match_zhengze('categoryId":(\d+)', text_i)#类目id
                item = taobao()
                item["item_id"] = item_id_s
                item["seller_id"] = seller_id_s
                item["cate_id"] = cate_id_s
                item["pipeline_level"] = "看了又看"
                yield item
                if item_id_s:
                    url = url2.format(item_id_s)
                    headers = headers_todict(headers2)
                    yield scrapy.Request(url=url, callback=self.parse_goods_xiaoliang, method="GET", headers=headers,meta={"item_id": item_id_s})
                    url = url1.format(item_id_s)#
                    headers = headers_todict(headers1)
                    # yield scrapy.Request(url=url, callback=self.parse_good_information, method="GET", headers=headers,meta={"item_id": item_id_s,"seller_id":seller_id_s})#商品详情
        else:
            request = self.try_again(response)
            if request:
                yield request

    def parse_goods_xiaoliang(self,response):
        text = response.text
        youxiao = '(isSuccess\":true|success\":false)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            item_id = meta.get("item_id")

            zjprice_s = self.match_zhengze(r'postageFree\":[^,]+,\"price\":\"([^\"]+)', text)#折扣价格
            fzjprice_s = self.match_zhengze(r'onlyShowOnePrice\":[^,]+,\"price\":\"([^\"]+)', text)#非折扣价格
            dizhi_s = self.match_zhengze(r'skuDeliveryAddress":"([^\"]+)', text)#发出地址
            xiaoliang_s = self.match_zhengze(r'sellCount":"([^\"]+)', text)#销量
            item = taobao()
            item["zjprice"] = zjprice_s
            item["fzjprice"] = fzjprice_s
            item["dizhi"] = dizhi_s
            item["xiaoliang"] = xiaoliang_s
            item["pipeline_level"] = "商品销量"
            yield item
        else:
            request = self.try_again(response)
            if request:
                yield request


    def parse_good_information(self,response):
        text = response.text
        youxiao = '(您查看的宝贝不存在|idata|商品详情|闲鱼|飞猪|司法|crossorigin|404|500|alitrip|paimai)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            seller_id = meta.get("seller_id")
            item_id = meta.get("item_id")

            item_id_s = self.match_zhengze('''itemId\s*:\s*["|']([^"']+)''',text)#商品ID
            shop_id_s = self.match_zhengze('''shopId\s*:\s*["|']([^"']+)''', text)#店铺ID
            seller_id_s = self.match_zhengze('''sellerId\s*:\s*["|']([^"']+)''', text)#卖家ID
            taobao_shop_name_s = self.match_zhengze('''shopName\s*:\s*["|']([^"']+)''', text)#淘宝店铺名称
            taobao_seller_name_s = self.match_zhengze('''sellerNick\s*:\s*["|']([^"']+)''', text)#淘宝卖家名称
            taobao_item_id_s = self.match_zhengze('''title\s*:\s*["|']([^"']+)''', text)#淘宝商品名称
            taobao_cate_id_s = self.match_zhengze('''\scid\s*:\s*["|']([^"']+)''', text)#淘宝类目ID
            taobao_cateroot_id_s = self.match_zhengze('''rcid\s*:\s*["|']([^"']+)''', text)#淘宝根类目ID
            shangjiatime_s = self.match_zhengze('''dbst\s*:\s*(\d+)''', text)#淘宝上架时间
            shop_type_s = self.match_zhengze('''type\s*:\s*["|']([^"']+)''', text)#店铺类型
            taobao_shop_dizhi_s = self.match_zhengze('''\surl\s*:\s*'//([^/]+)''', text)#淘宝店铺地址
            taobao_price_s = self.match_zhengze('''name="current_price"\svalue=\s"(\d+\.\d{2})''', text)#淘宝宝贝价格
            tmall_shop_name_s = self.match_zhengze('''slogo-shopname.+?><strong>([^<]+)''', text)#天猫店铺名称
            tmall_selller_name_s = self.match_zhengze('''seller_nickname" value="([^"]+)''', text)#天猫卖家名称
            tmall_shop_dizhi_s = self.match_zhengze('''shopUrl:"//([^"]+)''', text)#天猫店铺地址
            tamall_goods_name_s = self.match_zhengze('''name="title"\s*value="([^"]+)''', text)#天猫商品名称
            tmall_cate_id_s = self.match_zhengze('''"categoryId":"(\d+)''', text)#天猫类目ID
            tmall_brand_s = self.match_zhengze('''"brandId":"(\d+)''', text)#天猫品牌ID
            tmall_price_s = self.match_zhengze('''reservePrice":"(\d+\.\d{2})''', text)#天猫商品划线价
            tmall_shop_type_s = self.match_zhengze('''(旗舰店|专营店|品牌店)''', text)#天猫店铺类型
            item = taobao()
            item["item_id"] = item_id_s
            item["shop_id"] = shop_id_s
            item["seller_id"] = seller_id_s
            item["taobao_shop_name"] = taobao_shop_name_s
            item["taobao_seller_name"] = taobao_seller_name_s
            item["taobao_item_id"] = taobao_item_id_s
            item["taobao_cate_id"] = taobao_cate_id_s
            item["taobao_cateroot_id"] = taobao_cateroot_id_s
            item["shangjiatime"] = shangjiatime_s
            item["shop_type"] = shop_type_s
            item["taobao_shop_dizhi"] = taobao_shop_dizhi_s
            item["taobao_price"] = taobao_price_s
            item["tmall_shop_name"] = tmall_shop_name_s
            item["tmall_selller_name"] = tmall_selller_name_s
            item["tmall_shop_dizhi"] = tmall_shop_dizhi_s
            item["tamall_goods_name"] = tamall_goods_name_s
            item["tmall_cate_id"] = tmall_cate_id_s
            item["tmall_brand"] = tmall_brand_s
            item["tmall_price"] = tmall_price_s
            item["tmall_shop_type"] = tmall_shop_type_s
            item["pipeline_level"] = "商品详情"
            yield item

            if tmall_shop_name_s:#判断为天猫天猫
                if shop_id_s:
                    url = "http://shop{}.m.taobao.com/"#这个为天猫的url
                    headers = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
    User-Agent: Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36'''
                    url = url.format(shop_id_s)
                    headers = request_tools.headers_todict(headers)
                    yield scrapy.Request(url=url, callback=self.parse_tmall_idurl, method="GET", headers=headers,meta={"shop_id": shop_id_s})
                if seller_id_s:
                    asyn_url = "http://hdc1.alicdn.com/asyn.htm?userId={}&pageId=&v=2014"
                    headers = "User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36"
                    url_2 = asyn_url.format(seller_id_s)
                    headers = request_tools.headers_todict(headers)
                    yield scrapy.Request(url=url_2, callback=self.parse_tmall_asynshop, method="GET", headers=headers,meta={"seller_id": seller_id_s})#asyn公司

        else:
            request = self.try_again(response)
            if request:
                yield request

    def parse_tmall_idurl(self,response):#得到短url
        text = response.text
        youxiao = '(<link href="https://[^.]+|请使用手机淘宝进行浏览)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            shop_id = meta.get("shop_id")

            dizhi_s = self.match_zhengze('url" content="https://([^.]+)', text)#地址
            shop_id_s = self.match_zhengze('g_config.shopId = "(\d+)', text)#店铺id
            item = taobao()
            item["dizhi"] = dizhi_s
            item["shop_id"] = shop_id_s
            item["pipeline_level"] = "天猫id短链接"
            yield item

            if dizhi_s:
                url = "https://{}.m.tmall.com/shop/shop_info.htm?tbpm=3"
                headers = "User-Agent:Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.6.2000 Chrome/30.0.1599.101 Safari/537.36"
                url = url.format(dizhi_s)
                headers = request_tools.headers_todict(headers)
                yield scrapy.Request(url=url, callback=self.parse_tmall_jieshao, method="GET", headers=headers,meta={"dizhi_s": dizhi_s,"shop_id":shop_id})
        else:
            request = self.try_again(response)
            if request:
                yield request

    def parse_tmall_jieshao(self,response):#后置步骤
        text = response.text
        youxiao = '(店铺介绍|error2\.html;|whitelist|对不起，您访问的页面不存在！)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            shop_id = meta.get("shop_id")

            shop_id_s = self.match_zhengze('"id":"([^"]*)', text)#店铺ID
            seller_id_s = self.match_zhengze('"sellerId":([^,]*)', text)#卖家ID
            seller_name_s = self.match_zhengze('"nick":"([^"]*)', text)#卖家名称
            shop_url_s = self.match_zhengze('"shopUrl":"([^"]*)', text)#店铺URL
            shop_name_s = self.match_zhengze('"title":"([^"]*)', text)#店铺名称
            kaidiantime_s = self.match_zhengze('"starts":([^,]*)', text)#开店时间
            province_s = self.match_zhengze('"prov":"([^"]*)', text)#天猫省
            city_s = self.match_zhengze('"city":"([^"]*)', text)#天猫市
            shoucang_s = self.match_zhengze('"collectNum":([^,]*)', text)#收藏量
            shoucang2_s = self.match_zhengze('"collectorCount":([^,]*)', text)#收藏量2
            tellphone_s = self.match_zhengze('"phone":"([^"]*)', text)#客服电话
            fenphone_s = self.match_zhengze('"phoneExt":"([^"]*)', text)#电话分机
            brand_s = self.match_zhengze('"isBrandShop":([^,]*)', text)#是否品牌店
            tupiao_s = self.match_zhengze('"picUrl":"([^"]*)', text)#店铺图标
            shop_typeloge_s = self.match_zhengze('"shopTypeLogo":"([^"]*)', text)#店铺类型图标
            beijin_s = self.match_zhengze('"backImg":"([^"]*)', text)#店铺背景
            shop_dj_s = self.match_zhengze('"rateSum":"([^"]*)', text)#店铺等级
            shop_nl_s = self.match_zhengze('"shopAge":([^,]*)', text)#店铺年龄
            shop_type_s = self.match_zhengze('"shopType":([0-9]*)', text)#店铺类型
            haoping_s = self.match_zhengze('"sellerGoodPercent":"([^"]*)', text)#好评率
            wuliu_s = self.match_zhengze('"consignmentScore":"([^"]*)', text)#物流评分
            miaoshu_s = self.match_zhengze('"merchandisScore":"([^"]*)', text)#描述评分
            wufu_s = self.match_zhengze('"serviceScore":"([^"]*)', text)#服务评分
            hywuliu_s = self.match_zhengze('"cg":"([^"]*)', text)#行业物流比分
            hymiaoshu_s = self.match_zhengze('"mg":"([^"]*)', text)#行业描述比分
            hywufu_s = self.match_zhengze('"sg":"([^"]*)', text)#行业服务比分
            shangping_s = self.match_zhengze('"content":"([^"]*)","menuName":"全部商品",|"type":"allItems","content":"([^"]*)"', text)#商品数量
            shangxing_s = self.match_zhengze('"content":"([^"]*)","menuName":"上新"|"type":"newItems","content":"([^"]*)"', text)#上新数量
            wangwang_s = self.match_zhengze('to_user=([^&]*)', text)#加密旺旺
            gongshang_id_s = self.match_zhengze('xid=([^"]*)', text)#工商xid
            item = taobao()
            item["shop_id"] = shop_id_s
            item["seller_id"] = seller_id_s
            item["seller_name"] = seller_name_s
            item["shop_url"] = shop_url_s
            item["shop_name"] = shop_name_s
            item["kaidiantime"] = kaidiantime_s
            item["province"] = province_s
            item["city"] = city_s
            item["shoucang"] = shoucang_s
            item["shoucang2"] = shoucang2_s
            item["tellphone_s"] = tellphone_s
            item["fenphone"] = fenphone_s
            item["brand"] = brand_s
            item["tupiao"] = tupiao_s
            item["shop_typeloge"] = shop_typeloge_s
            item["beijin"] = beijin_s
            item["shop_dj"] = shop_dj_s
            item["shop_nl"] = shop_nl_s
            item["shop_type"] = shop_type_s
            item["haoping"] = haoping_s
            item["wuliu"] = wuliu_s
            item["miaoshu"] = miaoshu_s
            item["wufu"] = wufu_s
            item["hywuliu"] = hywuliu_s
            item["hymiaoshu"] = hymiaoshu_s
            item["hywufu"] = hywufu_s
            item["shangping"] = shangping_s
            item["shangxing"] = shangxing_s
            item["wangwang"] = wangwang_s
            item["gongshang_id"] = gongshang_id_s
            item["pipeline_level"] = "天猫介绍"
            yield item
        else:
            request = self.try_again(response)
            if request:
                yield request

    def parse_tmall_asynshop(self,response):#后置步骤
        text = response.text
        youxiao = '(s-maxage=5|"userId":)'
        youxiao_m = re.search(youxiao, text)
        if youxiao_m:
            text = text.replace("\n", "")
            text = text.replace("\r", "")
            text = text.replace("\t", "")
            meta = response.meta
            seller_id = meta.get("seller_id")

            biaoshi_s = self.match_zhengze(r'"categoryName":"([^"]*)',text)#标识
            shop_id_s = self.match_zhengze(r'sid([0-9]{1,})_', text)  # 店铺ID
            seller_id_s = self.match_zhengze(r'dsr-userid\\" value=\\"([0-9]{1,})|"userId":([0-9]{1,})', text)  # 卖家ID
            company_name_s = self.match_zhengze(r' 公 司 名：[^<]*</label>[^<]*<[^>]*>[^\s]*([^\\]*)', text)  # 公司名称
            xid_s = self.match_zhengze(r'&xid=([^\\]*)', text)  # xid##11
            item = taobao()
            item["biaoshi"] = biaoshi_s
            item["shop_id"] = shop_id_s
            item["seller_id"] = seller_id_s
            item["company_name"] = company_name_s
            item["xid"] = xid_s
            item["pipeline_level"] = "天猫asyn店铺"
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