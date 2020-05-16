# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from gm_work.items import GmWorkItem
from tools.tools_r.header_tool import headers_todict
import re


class AmazonPhSpider(RedisSpider):
    name = 'duhuang'
    allowed_domains = ['duhuang.com']
    start_urls = ['http://www.duhuang.com/']
    redis_key = "duhuang:start_url"
    headers = headers_todict('''Host: www.dhgate.com
Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Sec-Fetch-Site: none
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: vid=rBUUMl2DFlQ+oA/mBSOuAg==; NTKF_T2D_CLIENTID=guest14AD0ED5-5CE7-1831-3338-480F3C006C44; cto_lwid=2b0fa1c5-ad41-4220-ab73-8d28fee0f719; gaVisitorUuid=74e7a602-8866-4041-ae8e-b18a061188c5; pw_deviceid=40caaaf1-f170-4c61-adaf-589b66d206ae; pw_status_912a3e66fccf9b4a6ba50e65fd43522dabaecbe69c771596aeead701e85dd0af=deny; vscr_vid=ff3a19737627479e990f4ffb12fba990; smc_uid=1569314979382597; smc_tag=eyJpZCI6NzMzLCJuYW1lIjoiZGhnYXRlLmNvbSJ9; smc_not=default; seller_site_lang=zh_CN; seller_site_region=CN; c=UeHqQFOh-1575546092257-b880d6d2b8bf51942328817; c_haslogined=1; dh_isChange=isChange; gaIsValuable=1; searchinfo=pagesize%3D24%3Bviewtype%3D1%3B; dhc_s=321291c2-c2f6-4d69-a26e-c748d629cdcb; ref_f=seo|seller||organic|baidu||seller.dhgate.com; session=h9FBr1ccCnbexEA1MYiXQQ; _Jo0OQK=66FAFB7B7665388F613191308D62742C63A8C85B45E99FF22161029F88AF1D6D21E0C6E93F2376B923EBA903DA2963E8C4827B1313D3EFD632D94B573A64B71623CEFE3C935BE26F12FF0CFE73051AB9DA509C47B205529371D27B1313D3EFD632D419E13A61F2567F6E7302D862DBB29F0GJ1Z1Xw==; suship=CN; language=en; intl_locale=en; nTalk_CACHE_DATA={uid:dh_1000_ISME9754_ff8080816eea80d9016f83f286d6287f,tid:1578466731910275}; _pk_ses..c028=*; smc_sesn=2; item_recentvisit=446848411%2C409056389%2C453794591; cto_bundle=HhAwFF9mMXBzTFZGOU9PcEZvUmdQSDhiQlBWbXQ2THN4QTElMkIwRWFiS1ZqbE5ERnl6Yml1VHRlR2VWdWJuaHU1OWl0SldSVGR6bmZHRyUyQiUyQkpVJTJGSjZpdVpOQ1NRMDlmdjBUcWM1U2hQTkgxN21jRWpRUG8wdG9XZmwwYnAlMkZad2lwczd4bGpzd21ORHM2UDM1THhaSEVRcWF6VjRxWTJMZUxEc0hXSVNSaVpBZzhSVVYwJTNE; JSESSIONID=Q43UpUYr-5Drsk_EvDQJhAbbebLITvtbNyrzYptz; dht_lot=Public_S0003; b2b_cart_sid=0a593161-b5e6-4018-932b-1de576305240; b2b_ip_country=CN; login_auth_token=ca75df1d-853d-46e4-91ba-8b660fb4b656; __utma=251624089.850967565.1578468269.1578468269.1578468269.1; __utmc=251624089; __utmz=251624089.1578468269.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; _ga=GA1.2.850967565.1578468269; _gid=GA1.2.654880981.1578468273; _fmdata=AuB8%2Bk%2Bmil%2FzIeL26QejkjppmwIFzN2AxdgfZ01aMgeDzzSsSGiKxgFm68VLcxPDjlTtB5cP%2BIhBXVVhxGqyVGDOw7CYeO19jSvEzCz9lro%3D; _xid=qLL57rIGQyu5PK%2FSDHOvtOjWIdYE8tTR2XYYacit1AjDI0CYMjdBhDXX7%2FohBsPqIYMFq22NdMccLf6MOT80Sg%3D%3D; B2BCookie=a5450f13-7766-4749-81ff-447f6ad4054c; b2b_b_t_v2=789dbd93aa6c91eed57d96db0d4b1065c8b64a5497fd49b7449cec61c98e5196272920b2674d30991cd6fe75b8facb477487535198a0fbd420cee0f6ef246cc72f4a4e3f529074c3dd52aa9d7c87f88b10b4947c633a422543bcb9e2a1882c98; _Session_ID=pugdaTSL1we3L4Mfsg3CcT6bDfzBoWhAFLZP6U0m; bc=c|e; b2b_buyer_lv=0; b2b_nick_n=516387331; _b_o0l=8a9a0b754374779ebd197ef8054358bcbc7adae9758e4366d312f63a8a07bcb2; _b_o05="0,0,0,0"; buyerusername=516387331@qq.com; b2b_buyerid=ff8080816eea80d9016f83f286d6287f; b_u_cc=ucc=CN; pvn=96; lastvisittime=1578468295373; vnum=30; __utmb=251624089.2.10.1578468269; smc_spv=2; smc_tpv=3; smct_session={"s":1578466752509,"l":1578468408511,"lt":1578468320333,"t":79,"p":77}''')

    def start_requests(self):
        with open(r"C:\Users\admin\Desktop\{select_敦煌_业务信息URL}[店铺ID,Business_Information_url].txt","r",encoding="utf-8") as f:
            for i in f:
                data = i.strip().split(",")
                id = data[0]
                url = data[1]
                meta = {"key":id}
                yield scrapy.Request(url=url,method="GET",headers=self.headers,dont_filter=True,meta=meta)

    def parse(self, response):
        youxiao = re.search("(Information)",response.text)
        url = response.url
        key = response.meta.get("key")
        if youxiao:
            title = response.css(".b-title").xpath("./text()").get()

            item = GmWorkItem()
            item["key"] = key
            item["url"] = url
            item["company_name"] = title

            yield item

        else:
            print("错误")
            try_result = self.try_again(response,key)
            yield try_result

    def try_again(self,rsp,key):
        max_num = 5
        meta = rsp.meta
        try_num = meta.get("try_num",0)
        if try_num > max_num:
            try_num += 1
            request = rsp.request
            request.dont_filter = True
            request.meta["try_num"] = try_num
            return request
        else:
            item_e = GmWorkItem()
            item_e["error_id"] = 1
            item_e["key"] = key
            return item_e