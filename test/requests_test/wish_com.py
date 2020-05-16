import requests
from tools_s import header_tool
import json
import time
header_str = '''accept: application/json, text/plain, */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
content-length: 73
content-type: application/x-www-form-urlencoded
origin: https://www.wish.com
cookie: bsid=679fe927bcd54bab95d509bd2a98bea9; _xsrf=2|4759539d|5f87de6cc96aeab91ff223e284113c09|1567485141; sweeper_uuid=5135c440bb9e49819c65be0aaceca477; _timezone=8; _is_desktop=true; sweeper_session="2|1:0|10:1567489699|15:sweeper_session|84:Zjc0MDk0ZGMtNDJjYi00Zjc4LWE4NWQtMGFlNDM3Y2MwOGQ1MjAxOS0wOS0wMyAwNDozMjoyNC41OTAzMDM=|4f1b033ae189b686dd0d2fd5123213a72c90783775184494353b5d326a545c03"; sessionRefreshed_5d6cf7094f5e3f599f76c963=true; __stripe_sid=75a34c06-0c34-41b4-a29d-783f53430a38; __stripe_mid=224ab8be-1881-40c2-9ad1-094786108380
referer: https://www.wish.com/feed/tabbed_feed_latest?&source=tabbed_feed_latest
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36
x-xsrftoken: 2|4759539d|5f87de6cc96aeab91ff223e284113c09|1567485141'''
headers = header_tool.headers_todict(header_str)
url = "https://www.wish.com/api/feed/get-filtered-feed"
fordata = "count=30&offset={}&request_categories=false&request_id=tabbed_feed_latest&request_branded_filter=false"
no_more_items = False
num = 0
num_s = 0
File = open("wish_test.txt", 'a+', encoding="utf-8")
while not no_more_items and num<55:
    print("爬取",num)
    try:
        req = requests.post(url,data=fordata.format(30*num),headers=headers)
        num+= 1
        time.sleep(5)
        json_str = req.text
        if json_str.startswith('''{'''):
            json_data = json.loads(json_str)
            code = json_data.get("code")
            sweeper_uuid = json_data.get("sweeper_uuid")
            data = json_data.get("data")
            if data:
                next_offset = data.get("next_offset")
                title = data.get("title")
                no_more_items = data.get("no_more_items")
                products = data.get("products")
                if products:
                    print("成功了",num_s)
                    num_s+=1
                for product in products:
                    product_url = product.get("product_url")
                    meta_title = product.get("meta_title")
                    product_url = product_url.replace(",","")
                    meta_title = meta_title.replace(",","")
                    File.write(product_url+","+meta_title+'\n')
                    File.flush()
    except:
        print("请求中错误")
File.close()