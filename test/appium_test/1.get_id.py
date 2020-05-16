from mitmproxy.http import flow
import json
import redis

file_open = open(r"D:\spider_data\taobao_zhibo\taobao_zhiboinfo_new.txt","a",encoding="utf-8")
Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, password="nriat.123456",max_connections=10)
conn = redis.Redis(connection_pool=Pool,decode_responses=True)

def request(flow:flow):
    if ('https://acs.m.taobao.com/gw/mtop.mediaplatform.lightlive.videolist/1.0' in flow.request.url):# or ('https://webcast3-core-c-hl.amemv.com/webcast/feed/?' in flow.request.url) or ('https://webcast3-normal-c-hl.amemv.com/webcast/feed/?' in flow.request.url) :
        print(flow.request.url)
        # print(flow.request.port)

def response(flow:flow):
    if ('https://acs.m.taobao.com/gw/mtop.mediaplatform.lightlive.videolist/1.0' in flow.request.url):# or ('https://webcast3-core-c-hl.amemv.com/webcast/feed/?' in flow.request.url) or ('https://webcast3-normal-c-hl.amemv.com/webcast/feed/?' in flow.request.url) :
        json1 = json.loads(flow.response.text)
        # print(json1)
        data1 = json1.get("data")
        data_list = data1.get("dataList")
        for i in data_list:
            try:
                data2 = i.get("data")
                data3 = data2.get("data")
                accountList = data3.get("accountList")[0]
                accountId = accountList.get("accountId", "")
                accountNick = accountList.get("accountNick", "")
                level = accountList.get("level", "")
                shop = accountList.get("shop", "")
                tmall = accountList.get("tmall", "")

                liveList = data3.get("liveList")[0]
                id = liveList.get("id", "")
                location = liveList.get("location", "")
                praiseCount = liveList.get("praiseCount", "")
                title = liveList.get("title", "")
                userId = liveList.get("userId", "")
                liveChannelId = liveList.get("liveChannelId", "")


                shopId = ""
                shopName = ""

                if shop == "true":
                    shopList = data3.get("shopList")[0]
                    shopId = shopList.get("shopId")
                    shopName = shopList.get("shopName")
                data_list = [accountId, accountNick, level, shop, tmall, id, location, praiseCount, title, userId,
                             liveChannelId, shopId, shopName]
                data_list2 = []
                for i in data_list:
                    i = i.replace(",", '，')
                    i = i.replace("\n", '')
                    i = i.replace("\r", '')
                    data_list2.append(i)
                file_open.write(",".join(data_list2)+"\n")
                file_open.flush()
                conn.sadd("taobao_userid", userId)
            except:
                pass

    #mitmdump -q -s 1.get_id.py -p 8080

