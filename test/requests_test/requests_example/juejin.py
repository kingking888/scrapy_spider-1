import requests
import json
from lxml import etree
import pymysql
import time
# requests.get("https://juejin.im/")

host = "47.92.39.242"
user = "py_data"
password = "arXekemkP2EzJyEs"
database = "py_data"
db = pymysql.connect(host=host, user=user, password=password, db=database, port=3306, charset="utf8")
cursor = db.cursor()
insert_sql = "insert into juejin_article (`url`,`title`,`tags`,`create_time`,`like_count`,`text`,`html`,`user`)values ({});"

headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "web-api.juejin.im",
            "Referer": "https://juejin.im/",
            "X-Requested-With":"XMLHttpRequest",
            "Origin": "https://juejin.im",
            "Content-Type": "application/json",
            "Sec-Fetch-Mode": "cors",
            "X-Legacy-Uid":"",
            "X-Agent": "Juejin/Web",
            "X-Legacy-Token":"",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }
header1 = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "juejin.im",
        "X-Legacy-Token": "",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
after =""
url = "https://web-api.juejin.im/query"

judge = True
num = 0
while judge and num <= 50:
    num+=1
    try:
        data_r = '''{"operationName":"","query":"","variables":{"first":20,"after":"''' + after + '''","order":"POPULAR"},"extensions":{"query":{"id":"21207e9ddb1de777adeaca7a2fb38030"}}}'''
        req = requests.post(url,headers=headers,data=data_r)
        a = req.apparent_encoding

        json_data = json.loads(req.text)
        data = json_data.get("data")
        articleFeed = data.get("articleFeed")
        items = articleFeed.get("items")
        if not items:
            break
        edges = items.get("edges")
        pageInfo = items.get("pageInfo")
        after = pageInfo.get("endCursor")
        hasNextPage = pageInfo.get("hasNextPage")
        for edge in edges:
            try:
                data_list = []
                node = edge.get("node")

                originalUrl = node.get("originalUrl") if node.get("originalUrl") else ""
                # title = node.get("title") if node.get("title") else ""

                createdAt = node.get("createdAt") if node.get("createdAt") else ""
                likeCount = node.get("likeCount") if node.get("likeCount") else ""
                # tags = node.get("tags")
                # tag_list = []
                # for tag in tags:
                #     title_tag = tag.get("title")
                #     tag_list.append(title_tag)
                # tag_last = " ".join(tag_list)
                # user = node.get("user")
                # username = user.get("username") if user.get("username") else ""
                req1 = requests.get(originalUrl, headers=header1)
                html = etree.HTML(req1.text)
                div_list = html.xpath('//*[@class="article"]')
                div_str = ''
                if div_list:
                    div = div_list[0]
                    div_str = etree.tostring(div, encoding='utf-8').decode("utf-8")
                titles = html.xpath('//*[@id="juejin"]/div[2]/main/div/div[1]/article/h1/text()')
                if titles:
                    title = titles[0]
                else:
                    title = ""
                usernames = html.xpath('//meta[@itemprop="name"]/@content')
                if usernames:
                    username = usernames[0]
                else:
                    username = ""
                tag_list = html.xpath('//meta[@name="keywords"]/@content')
                tag_last = " ".join(tag_list)
                text = html.xpath('string(//*[@class="article"])')
                data_list.append('"'+pymysql.escape_string(originalUrl)+'"')
                data_list.append('"'+pymysql.escape_string(title)+'"')
                data_list.append('"'+pymysql.escape_string(tag_last)+'"')
                data_list.append('"'+pymysql.escape_string(str(createdAt))+'"')
                data_list.append('"'+pymysql.escape_string(str(likeCount))+'"')
                data_list.append('"'+pymysql.escape_string(text)+'"')
                data_list.append('"'+pymysql.escape_string(div_str)+'"')
                data_list.append('"'+pymysql.escape_string(username)+'"')
                values = ",".join(data_list)
                cursor.execute(insert_sql.format(values))
            except Exception as e:
                print(e)
            time.sleep(5)
    except Exception as e:
        break













