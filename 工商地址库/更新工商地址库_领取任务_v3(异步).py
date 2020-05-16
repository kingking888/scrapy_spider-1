import time, asyncio, aiohttp, urllib, requests, json, jsonpath, re, socket, datetime, redis, pymysql
from Bloomfilter import BloomFilter
from tqdm import tqdm
from multiprocessing import Pool


class GetTask(object):
    def __init__(self, table):
        self.connect = pymysql.connect(host='192.168.0.227', port=3306, database='oridata', user='dev',
                                       password='Data227or8Dev715#', charset='utf8', use_unicode=True)
        self.cursor = self.connect.cursor()

        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'}
        self.r = redis.Redis(host='127.0.0.1', port=6379, db=14, decode_responses=True,password="nriat.123456")
        self.cache_queue = 'gs_cache_queque'
        self.not_spider_queue = 'not_spider_address'
        self.main_queue = 'company_info'
        self.bf = BloomFilter('gs_adress')
        self.bf2 = BloomFilter('not_spider_address')
        self.ak = '91d21af63da4bd5b63a42ae486376000'
        self.table = table
        self.gevent_num = 120
        # 信号量，控制协程数，防止爬的过快
        self.sem = asyncio.Semaphore(self.gevent_num)
        self.JX_1_htmls = []
        self.JX_2_htmls = []
        self.tasks = []

    def if_task(self):
        while True:
            task_list = []
            check_cache_queue = self.r.scard(self.cache_queue)
            if check_cache_queue > 0:
                # 缓存队列不为空，返回缓存队列所有数据
                using_data = self.r.smembers(self.cache_queue)
                print('-----清理缓存队列-----')
                for i in tqdm(using_data):
                    if self.bf.isContains(i):
                        # 该参数已采集到数据则从缓存队列删除
                        self.r.srem(self.cache_queue, i)
                    else:
                        # 该参数未采集到数据则添加进主队列，然后从缓存队列删除
                        self.r.sadd(self.main_queue, i)
                        self.r.srem(self.cache_queue, i)
            all_task_name = self.r.keys()
            for i in all_task_name:
                check_TaskName = re.search(self.main_queue, i)
                if check_TaskName != None:
                    # 将找到的任务队列添加到列表
                    task_list.append(i)
            # 判断列表是否为空，如果为空，则说明没有任务生成

            if len(task_list) == 0:
                print('------未找到任务队列--------')
                time.sleep(60)
            else:
                TaskName = task_list[0]
                self.run_task(TaskName)

    # 获取本地IP
    def get_ip(self):
        addrs = socket.getaddrinfo(socket.gethostname(), None)
        IP_Address = [item[4][0] for item in addrs if ':' not in item[4][0]][0]
        return IP_Address

    def run(self):
        # 领取并执行采集任务
        print('--------------------------开始采集--------------------------')
        self.if_task()

    # -----------------------------------------------------------------------
    def main_get_html_one(self, get_CompanyAndCompanyAddr_list):
        loop = asyncio.get_event_loop()  # 获取事件循环
        tasks = [self.get_html_one(CompanyAndCompanyAddr) for CompanyAndCompanyAddr in
                 get_CompanyAndCompanyAddr_list]  # 把所有任务放到一个列表中
        loop.run_until_complete(asyncio.wait(tasks))  # 激活协程
        # 解析
        self.main_parse_html_1()
        # 关闭事件循环
        # loop.close()

    def main_parse_html_1(self):
        p = Pool(2)
        for html in self.JX_1_htmls:
            p.apply_async(self.multi_parse_html_one(html))
        # 完成解析清除当前已解析过的数据
        self.JX_1_htmls.clear()
        p.close()
        p.join()

    # 提交请求获取网页html
    async def get_html_one(self, CompanyAndCompanyAddr):
        try:
            CompanyAddress = CompanyAndCompanyAddr.split('——')
            try:
                company_addr = CompanyAddress[1].replace('\n', '').replace('——', '')
                company = CompanyAddress[0]
            except:
                company_addr = ''
                company = ''
            if self.bf2.isContains(CompanyAndCompanyAddr):
                self.r.srem(self.cache_queue, CompanyAndCompanyAddr)
            else:
                if company_addr != '':
                    address1 = urllib.parse.quote(company_addr, safe='/')
                    jwd_url = 'https://restapi.amap.com/v3/geocode/geo?address={}&output=json&key={}&output=json'.format(
                        address1, self.ak)
                    with(await self.sem):
                        # async with是异步上下文管理器
                        async with aiohttp.ClientSession() as session:  # 获取session
                            async with session.request('GET', jwd_url, headers=self.header) as resp:  # 提出请求
                                html = await resp.text()  # 直接获取到bytes
                                # 将未解析的数据添加进列表
                                company_html = CompanyAndCompanyAddr + '——' + html
                                self.JX_1_htmls.append(company_html)
                        # print('当前查询的公司地址:{}'.format(company_addr))
        except:
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            self.r.srem(self.cache_queue, CompanyAndCompanyAddr)

    # 使用多进程解析html
    def multi_parse_html_one(self, company_html):
        html = company_html.split('——')[-1]
        company = company_html.split('——')[0]
        company_addr = company_html.split('——')[1]
        CompanyAndCompanyAddr = company + '——' + company_addr
        jsonobj = json.loads(html)
        try:
            status = str(jsonpath.jsonpath(jsonobj, '$..status')[0])
        except:
            status = ''
        if status == '1':
            # 经度
            try:
                location = str(jsonpath.jsonpath(jsonobj, '$..location')[0]).replace('[]', '')
            except:
                location = ''
            if location != '':
                CompanyAndCompanyAddr_location = company_html.replace(html, location)
                self.tasks.append(CompanyAndCompanyAddr_location)
            else:
                location = self.BuChong(company_addr)
                if location != '':
                    CompanyAndCompanyAddr_location = company_html.replace(html, location)
                    self.tasks.append(CompanyAndCompanyAddr_location)
                else:
                    self.bf2.insert(CompanyAndCompanyAddr)
                    self.r.sadd(self.not_spider_queue, CompanyAndCompanyAddr)
                    self.r.srem(self.cache_queue, CompanyAndCompanyAddr)

        elif status == '0':
            print('无效的key')
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            status > 0
        elif status == '10013':
            print('key被删除')
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            status > 0
        elif status == '10004':
            print('单位时间内方位过于频繁')
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            status > 0
        elif status == '10003':
            print('访问已超出日访问量')
            print('错误AK：{}'.format(self.ak))
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            # 设置报错，让程序停止运行
            status > 0
        elif status == '10002':
            print('没有权限使用相应的服务或者请求接口的路径拼写错误')
            print('错误AK：{}'.format(self.ak))
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            status > 0
        else:
            print('发生错误，错误代码为：{}'.format(status))
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            status > 0

    def main_get_html_two(self):
        loop = asyncio.get_event_loop()  # 获取事件循环
        tasks = [self.get_html_two(CompanyAndCompanyAddr_html) for CompanyAndCompanyAddr_html in
                 self.tasks]  # 把所有任务放到一个列表中
        loop.run_until_complete(asyncio.wait(tasks))  # 激活协程
        # 解析
        self.main_parse_html_2()
        # 解析完成关闭事件循环
        # loop.close()

    async def get_html_two(self, CompanyAndCompanyAddr_location):
        info = CompanyAndCompanyAddr_location.split('——')
        # print(info)
        location = info[-1]
        CompanyAndCompanyAddr = info[0] + '——' + info[1]
        try:
            address_url = 'http://restapi.amap.com/v3/geocode/regeo?key={}&location={}&poitype=&radius=1000&extensions=base&batch=false&roadlevel=0'.format(
                self.ak, location)
            async with aiohttp.ClientSession() as session:  # 获取session
                async with session.request('GET', address_url, headers=self.header) as resp:  # 提出请求
                    html = await resp.text()  # 直接获取到bytes
                    # 将未解析的数据添加进列表
                    company_html = CompanyAndCompanyAddr_location + '——' + html
                    self.JX_2_htmls.append(company_html)
        except:
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            self.r.srem(self.cache_queue, CompanyAndCompanyAddr)

    def main_parse_html_2(self):
        p = Pool(2)
        for html in self.JX_2_htmls:
            p.apply_async(self.multi_parse_html_two(html))
        # 完成解析清除当前已解析过的数据
        self.JX_2_htmls.clear()
        p.close()
        p.join()

    def multi_parse_html_two(self, company_html):
        html = company_html.split('——')[-1]
        company = company_html.split('——')[0]
        company_address = company_html.split('——')[1]
        location = company_html.split('——')[-2]
        # print(location)
        jsonobj = json.loads(html)
        lng = location.split(',')[0]
        lat = location.split(',')[1]
        # 国家
        try:
            country = str(jsonpath.jsonpath(jsonobj, '$..country')[0]).replace('[]', '')
        except:
            country = ''
        # 省
        try:
            province = str(jsonpath.jsonpath(jsonobj, '$..province')[0]).replace('[]', '')
        except:
            province = ''
        # 市
        try:
            city = str(jsonpath.jsonpath(jsonobj, '$..city')[0]).replace('[]', '')
        except:
            city = ''
        # 区
        try:
            county = str(jsonpath.jsonpath(jsonobj, '$..district')[0]).replace('[]', '')
        except:
            county = ''
        # 镇
        try:
            township = str(jsonpath.jsonpath(jsonobj, '$..township')[0]).replace('[]', '')
        except:
            township = ''
        # 街道
        try:
            street = str(jsonpath.jsonpath(jsonobj, '$..street')[0]).replace('[]', '')
        except:
            street = ''
        # 方向
        try:
            direction = str(jsonpath.jsonpath(jsonobj, '$..direction')[0]).replace('[]', '')
        except:
            direction = ''
        # 距离
        try:
            distance = str(jsonpath.jsonpath(jsonobj, '$..distance')[0]).replace('[]', '')
        except:
            distance = ''
        # 街道号
        try:
            streetNumber = str(jsonpath.jsonpath(jsonobj, '$..number')[0]).replace('[]', '')
        except:
            streetNumber = ''
        # 行政区划代码
        try:
            adcode = str(jsonpath.jsonpath(jsonobj, '$..adcode')[0]).replace('[]', '')
        except:
            adcode = ''
        # 城市代码
        try:
            citycode = str(jsonpath.jsonpath(jsonobj, '$..citycode')[0]).replace('[]', '')
        except:
            citycode = ''
        # 乡镇代码
        try:
            towncode = str(jsonpath.jsonpath(jsonobj, '$..towncode')[0]).replace('[]', '')
        except:
            towncode = ''
        # 格式化地址
        try:
            formatted_address = str(jsonpath.jsonpath(jsonobj, '$..formatted_address')[0]).replace('[]', '')
        except:
            formatted_address = ''
            #
        # print(company, company_address, lat, lng, country, province, city, county,
        #       township, street, direction, distance, streetNumber, adcode, citycode, towncode, formatted_address)
        # print('-' * 50)
        CompanyAndCompanyAddr = company + '——' + company_address
        try:
            if self.bf.isContains(company):
                # 采集完成，从缓存队列中删除
                self.r.srem(self.cache_queue, CompanyAndCompanyAddr)
            else:
                self.updata_address(company, company_address, lat, lng, country, province, city, county,
                                    township, street, direction, distance, streetNumber, adcode, citycode, towncode,
                                    formatted_address)
                self.bf.insert(company)
                # 采集完成，从缓存队列中删除
                self.r.srem(self.cache_queue, CompanyAndCompanyAddr)
        except:
            self.r.sadd('company_info', CompanyAndCompanyAddr)
            self.r.srem(self.cache_queue, CompanyAndCompanyAddr)

    def updata_address(self, company, company_address, lat, lng, country, province, city, county,
                       township, street, direction, distance, streetNumber, adcode, citycode, towncode,
                       formatted_address):
        self.cursor.execute(
            """ insert into {}(company, company_address, lat, lng, country, province, city, county,
                  township, street, direction, distance, streetNumber, adcode, citycode, towncode, formatted_address) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""".format(
                self.table),

            (company, company_address, lat, lng, country, province, city, county, township, street, direction, distance,
             streetNumber, adcode, citycode, towncode, formatted_address))
        self.connect.commit()

    def check_table(self):
        self.count = self.cursor.execute("""show tables""")
        all_shopinfo = self.cursor.fetchall()
        self.connect.commit()
        all_shopinfo_list = []
        for i in all_shopinfo:
            all_shopinfo_list.append(i[0])
        return all_shopinfo_list

    def run_task(self, TaskName):
        get_CompanyAndCompanyAddr_list = []
        num = 0
        all_data_num = self.r.scard(TaskName)
        while True:
            keyword = self.r.spop('{}'.format(TaskName))
            # 将获取的数据存储到另外一个集合中，防止程序中途停止导致数据丢失
            self.r.sadd(self.cache_queue, keyword)
            if keyword == None:
                print('当前采集任务完成')
                break
            else:
                if self.bf.isContains(keyword):
                    self.r.srem(self.cache_queue, keyword)
                    num += 1
                else:
                    if len(get_CompanyAndCompanyAddr_list) == self.gevent_num:
                        self.main_get_html_one(get_CompanyAndCompanyAddr_list)
                        self.main_get_html_two()
                        # 完成任务后清空列表
                        self.tasks.clear()
                        get_CompanyAndCompanyAddr_list.clear()
                        get_CompanyAndCompanyAddr_list.append(keyword)
                        num += 1
                    else:
                        get_CompanyAndCompanyAddr_list.append(keyword)
                        num += 1
                        if num == all_data_num:
                            self.main_get_html_one(get_CompanyAndCompanyAddr_list)
                            self.main_get_html_two()
                            self.tasks.clear()
                            get_CompanyAndCompanyAddr_list.clear()

    def BuChong(self, address):
        address1 = urllib.parse.quote(address, safe='/')
        self.get_jingweidu_url = 'http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak=8OUnXVy4hbNBS67V9v7PltluwYwvzEw5'.format(
            address1)
        response = requests.get(self.get_jingweidu_url, headers=self.header, timeout=5)
        html = response.text
        jsonobj = json.loads(html)
        try:
            lng = jsonpath.jsonpath(jsonobj, '$..lng')[0]
            lat = jsonpath.jsonpath(jsonobj, '$..lat')[0]
        except:
            lng = ''
            lat = ''
        if lng == '' or lat == '':
            location = ''
            return location
        else:
            location = str(lng) + ',' + str(lat)
            return location


if __name__ == '__main__':
    # save_table_path = 'F:/工商地址库更新/'
    # with open(save_table_path + '存储数据的表名称.txt', 'r', encoding='utf-8') as f:
    #     table = f.read().strip()
    table = input("请输入插入表：")
    get = GetTask(table)
    all_table = get.check_table()
    if table in all_table:
        get.run()
    else:
        print("'{}'表不存在，请创建后再运行程序".format(table))
        time.sleep(10)
