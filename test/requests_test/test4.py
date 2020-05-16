import requests
from tools_s.header_tool import headers_todict
from PIL import Image

headers = '''accept: */*
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cache-control: no-cache
content-length: 242
content-type: application/x-www-form-urlencoded;charset=UTF-8
origin: https://gxinmarker.en.alibaba.com
pragma: no-cache
referer: https://gxinmarker.en.alibaba.com/contactinfo.html
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'''
url = "https://gxinmarker.en.alibaba.com/event/app/alisite/render.htm"
data = '''bizId: 17380381748
language: en_US
envMode: product
hostToken: V1I2KX9UOJ3RmRT0n8EvhXZKzLL21eH6xPR0ZjAIF+s6sg5LoS55cRvzM7l+7GgpXLox7N3ZFV/VQjadwQUB8NVA==
siteId: 5005155392
pageId: 5014064654
renderType: component
componentKeys: companyCard'''
data = headers_todict(data)
req = requests.post(url=url,data=data,headers = headers_todict(headers))
print(req.content)

