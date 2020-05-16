import base64
from urllib import parse
import requests
import json
from PIL import Image
from io import BytesIO


# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=1lcrorctDt5SpCGAkWaCPHo7&client_secret=NoTTReewWdt4ZQLV5GA87Cr1nYYxYaS8'
response = requests.get(host)
if response:
    print(response.json())

tupian_url = "http://g-search3.alicdn.com/img/bao/uploaded/i4/i1/2885407209/O1CN016GmIGY237lp2sxDq9_!!0-item_pic.jpg_360x360Q90.jpg_.webp"
url_p = parse.urlparse(tupian_url)
domain = url_p.netloc
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Upgrade-Insecure-Requests": "1",
    "Connection": "keep-alive",
    "Host": domain
}
req = requests.get(tupian_url,headers=headers)
img_b = req.content
img_s = base64.b64encode(img_b)#得到了url的base64编码

#将二进制图片用image打开
#Image只能打开文件类图片
# image1 = Image.open(BytesIO(img_b))
# image1 = image1.crop((1,10,50,30))
# image1.save("byteio.png")


#进行百度接口请求
baidu_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"
access_token = "24.e9572f44cf6640430b5ca10eda8348bb.2592000.1561134005.282335-16320205"#一个月失效
url_param = {
    "access_token":access_token
}
headers_baidu = {
    "Content-Type":"application/x-www-form-urlencoded"
}
body = {"image":img_s}
baidu_url = baidu_url+"?"+parse.urlencode(url_param)
req_baidu = requests.post(url=baidu_url,data=parse.urlencode(body),headers=headers_baidu)
jieguo = json.loads(req_baidu.text)
print(jieguo)