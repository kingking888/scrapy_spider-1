import requests
from tools_s.header_tool import headers_todict
headers_str = '''Host: shop126041192.taobao.com
Cache-Control: no-cache
Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Referer: https://shop126041192.taobao.com/i/asynSearch.htm?_ksTS=1568189550597_241&callback=jsonp242&mid=w-18394102008-0&wid=18394102008&path=/search.htm&search=y
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: t=533a27cd3c629dd03641a6eb99c9507b; _m_h5_tk=926e001f0d264a00de058c34b7e7692c_1568282606061; _m_h5_tk_enc=0659c6c0fc38cc10a9844483e48da433; cookie2=16d49c3bcec7ce827928d17d004c97dc; _tb_token_=733556e3bb3d5; cna=gvAAFjjMWnUCAdy4URBLu1tr; v=0; unb=1841955291; uc3=id2=UonfNi0%2FFrMiHg%3D%3D&nk2=q6SExg6ViDH5dsxxo5k%3D&lg2=W5iHLLyFOGW7aA%3D%3D&vt3=F8dByuPRWydtesdnsbQ%3D; csg=0ba6ba0d; lgc=%5Cu4E09%5Cu9014%5Cu6CB3%5Cu8FD8%5Cu662F%5Cu5929%5Cu5802; cookie17=UonfNi0%2FFrMiHg%3D%3D; dnk=%5Cu4E09%5Cu9014%5Cu6CB3%5Cu8FD8%5Cu662F%5Cu5929%5Cu5802; skt=51d2f94298636c64; existShop=MTU2ODI3NzYzNw%3D%3D; tracknick=%5Cu4E09%5Cu9014%5Cu6CB3%5Cu8FD8%5Cu662F%5Cu5929%5Cu5802; _cc_=UtASsssmfA%3D%3D; tg=0; _l_g_=Ug%3D%3D; sg=%E5%A0%821c; _nk_=%5Cu4E09%5Cu9014%5Cu6CB3%5Cu8FD8%5Cu662F%5Cu5929%5Cu5802; cookie1=AQGkWYrtqrzZNy4hOkvFso4Pf1LwvRb%2BLVjL8pIk81o%3D; enc=Q%2FHWJrG3gH60SR8dDaEkznlS2PCBT0e67im%2BGC2cHLUhyww%2FpFIKDJ2pOK2QV5djOLXa6byYW8mJ9JT%2FVoLMYg%3D%3D; JSESSIONID=0C4AA503D4BFCC52BE05BDCA770710C7; mt=ci=2_1; thw=cn; uc1="cookie15=U%2BGCWk%2F75gdr5Q%3D%3D"; hng=CN%7Czh-CN%7CCNY%7C156; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; swfstore=44387; isg=BBcXOTrsBhSx74KYW_l7IAtppouh9Oi6DJcBZGlEBOZNmDfacC4FDtPy-ngjcMM2; l=cBgYYcKuqc294jAQBOCZ5uI8Yu7tvIRAguPRwhYMi_5QW68626bOkPzEgFJ6cjWdtwYp4aHcGPw9-etlsugP9P--g3fP.'''
headers_y = headers_todict(headers_str)
# print(headers_y)
# with open(r"C:\Users\yiosus\Desktop\taobao.csv") as f:
#     for i in f:
url = "https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?jsv=2.5.1&appKey=12574478&t=1568291538962&sign=a13e3e25ec6d9bf557dae54afbf04196&api=mtop.taobao.detail.getdetail&v=6.0&isSec=0&ecode=0&AntiFlood=true&AntiCreep=true&H5Request=true&ttid=2018%40taobao_h5_9.9.9&type=jsonp&dataType=jsonp&callback=mtopjsonp1"
# time_str = str(int(time.time()*1000))
# url = url.replace("126041192",str(i.strip()))
# url = url.replace("1568189550597",time_str)
# print(url)
headers = headers_y
# headers["Host"] = headers_y["Host"].replace("126041192",str(i.strip()))
# headers["Referer"] = url
# print(headers)
req = requests.get(url,headers=headers)
print(req.text)
