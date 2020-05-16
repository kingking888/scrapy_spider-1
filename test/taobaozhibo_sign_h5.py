import requests
from tools.tools_r.taobao.taobao_sign_h5 import get_taobaosign
from tools.tools_r.header_tool import headers_todict,reqhead_split,dict_to_cookiesstr
import time
import json
import re

def get_sign1(sellerid):
    headers1 = get_taobao_headers()
    headers1["referer"] = "https://h5.m.taobao.com/taolive/video.html?id={}".format(sellerid)
    url = "https://h5api.m.taobao.com/h5/mtop.mediaplatform.live.videolist/2.0/?jsv=2.4.0&appKey={}&t={}&sign={}&AntiCreep=true&api=mtop.mediaplatform.live.videolist&v=2.0&type=jsonp&dataType=jsonp&timeout=20000&callback=mtopjsonp1&data=%7B%7D"
    time_now = str(int(time.time()*1000))
    appkey = "12574478"
    data = '{}'
    sign = get_taobaosign(time=time_now, appKey=appkey, data=data)
    url = url.format(appkey,time_now,sign)
    req = requests.get(url=url,headers=headers1)
    headers_rep = req.headers
    set_cookiesstr = headers_rep.get("set-cookie")
    set_cookies = reqhead_split(set_cookiesstr)
    cookies_dict = dict()
    cookies_dict["t"] = set_cookies.get("t","")
    cookies_dict["_m_h5_tk"] = set_cookies.get("_m_h5_tk","")
    cookies_dict["_m_h5_tk_enc"] = set_cookies.get("_m_h5_tk_enc","")
    return cookies_dict

def request_1(cookies_dict,sellerid):
    headers2 = get_taobao_headers()
    headers2["referer"] = "https://h5.m.taobao.com/taolive/video.html?id={}".format(sellerid)#id  #userId
    cookeis = dict_to_cookiesstr(cookies_dict)
    # print(cookeis)
    headers2["cookie"] = cookeis
    # headers2["host"] = "h5api.m.taobao.com"
    time_now = str(int(time.time()*1000))
    appkey = "12574478"
    data = '{{"creatorId":"{}"}}'.format(sellerid)#liveId creatorId
    # print(data)
    sign_token = cookies_dict.get("_m_h5_tk").split("_")[0]
    # print(sign_token)
    sign = get_taobaosign(time=time_now, appKey=appkey, data=data,token=sign_token)
    # print(sign)
    url2 = "https://h5api.m.taobao.com/h5/mtop.mediaplatform.live.livedetail/4.0/?jsv=2.4.0&appKey={}&t={}&sign={}&AntiCreep=true&api=mtop.mediaplatform.live.livedetail&v=4.0&type=jsonp&dataType=jsonp&timeout=20000&callback=mtopjsonp3&data=%7B%22creatorId%22%3A%22{}%22%7D"
    url2 = url2.format(appkey,time_now,sign,sellerid)
    req = requests.get(url=url2,headers=headers2)
    # print(url2)
    # print(headers2)
    print(req.text)
def request2(cookies_dict,sellerid):
    headers2 = get_taobao_headers()
    headers2["referer"] = "https://tblive.m.taobao.com/wow/tblive/act/host-detail?wh_weex=true&broadcasterId={}".format(sellerid)#broadcasterId
    cookeis = dict_to_cookiesstr(cookies_dict)
    # print(cookeis)
    headers2["cookie"] = cookeis
    # headers2["host"] = "h5api.m.taobao.com"

    time_now = str(int(time.time()*1000))
    appkey = "12574478"
    data = '{{"broadcasterId":"{}","start":0,"limit":10}}'.format(sellerid)#
    # print(data)
    sign_token = cookies_dict.get("_m_h5_tk").split("_")[0]
    # print(sign_token)
    sign = get_taobaosign(time=time_now, appKey=appkey, data=data,token=sign_token)
    # print(sign)
    url2 = "https://h5api.m.taobao.com/h5/mtop.mediaplatform.anchor.info/1.0/?jsv=2.4.8&appKey={}&t={}&sign={}&api=mtop.mediaplatform.anchor.info&v=1.0&AntiCreep=true&AntiFlood=true&type=jsonp&dataType=jsonp&callback=mtopjsonp3&data=%7B%22broadcasterId%22%3A%22{}%22%2C%22start%22%3A0%2C%22limit%22%3A10%7D"
    url2 = url2.format(appkey,time_now,sign,sellerid)
    req = requests.get(url=url2,headers=headers2)
    # print(url2)
    # print(headers2)
    print(req.text)
    return req.text

def get_taobao_headers():
    headers = '''accept: */*
    accept-encoding: gzip, deflate, br
    accept-language: zh-CN,zh;q=0.9
    cache-control: no-cache
    pragma: no-cache
    sec-fetch-mode: no-cors
    sec-fetch-site: same-site
    user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'''
    return headers_todict(headers)
if __name__=="__main__":
    test_id = "1714128138"
    cookies_dict = get_sign1(test_id)
    # sellerid_list = ["2207965874011","2355986698"]
    # for i in sellerid_list:
    #     request_1(cookies_dict,i)
    sellerid = 1759494485
    text = request2(cookies_dict,sellerid)
    match = re.search(" mtopjsonp3\((.*)\)",text)
    if match:
        json_str = match.group(1)
        json_data = json.loads(json_str)
        data = json_data.get("data")
        anchorId = data.get("anchorId")
        nick = data.get("nick")
        relation = data.get("relation")
        fansCount = relation.get("fansCount")
        followTopCount = relation.get("followTopCount")
        liveCount = relation.get("liveCount")
        replays = data.get("replays")
        for i in replays:
            liveId = i.get("liveId")
            liveTime = i.get("liveTime")
            roomTypeName = i.get("roomTypeName")
            title = i.get("title")
            viewerCount = i.get("viewerCount")