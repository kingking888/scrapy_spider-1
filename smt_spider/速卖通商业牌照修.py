import re, os, time, redis, random, pymysql
import socket
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
from selenium.webdriver import ActionChains
from selenium import webdriver
from smt_spider.Bloomfilter import BloomFilter
from lxml import etree
from tqdm import tqdm


def get_ip():
    addrs = socket.getaddrinfo(socket.gethostname(), "")
    match = re.search("'192.168.\d+.(\d+)'", str(addrs))
    ip_num = "000"
    if match:
        ip_num = match.group(1)
    return ip_num

class SafeDriver:
    def __init__(self):
        self.chrome_canshu()

    def chrome_canshu(self):
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument('--incognito')
        options.add_argument('--no-sandbox')
        options.add_argument("disable-infobars")
        options.add_argument("disable-web-security")
        options.add_argument("--proxy-server=127.0.0.1:6363")

        # options.add_argument("--headless")
        # options.add_argument("--start-maximized")
        options.add_argument("--log-level=3")
        No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", No_Image_loading)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()

class smt_pz_info(object):
    def __init__(self, zhanghao, ADSL_name, ADSL_pwd):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'}
        self.r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True,password="nriat.123456")
        # self.chrome_canshu()
        self.bf = BloomFilter('SmtPzInfoSpider')
        self.cache_queue = 'smt_pzinfo_cache_queque'
        self.ADSL_name = ADSL_name
        self.ADSL_pwd = ADSL_pwd
        self.zhanghao_list = zhanghao
        self.zhanghao_num = 0
        self.error_num = 0
        self.a_list = [10, 15, 20, 25, 30, 35, 40, 45, 50]
        self.a = random.uniform(20, 30)
        self.write()
        # self.huan_ip()
        self.safe_dirver = SafeDriver()
        print(1)

    # 检测当前程序进程pid,并存入文本中
    def write(self):
        pid = os.getpid()
        with open('pid.txt', 'w', encoding='utf-8') as f:
            f.write(str(pid))

    # ----------------------自动拨号更换IP-----------------------------

    def connect(self):
        name = "宽带连接"
        username = '{}'.format(self.ADSL_name)
        password = '{}'.format(self.ADSL_pwd)
        cmd_str = "rasdial %s %s %s" % (name, username, password)
        res = os.system(cmd_str)
        if res == 0:
            print("连接成功")
        else:
            print(res)

    def disconnect(self):
        name = "宽带连接"
        cmdstr = "rasdial %s /disconnect" % name
        os.system(cmdstr)
        print('断开成功')

    def huan_ip(self):
        # 断开网络
        self.disconnect()
        # 开始拨号
        self.connect()

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
                        self.r.sadd('smt_pzinfo',i)
                        self.r.srem(self.cache_queue, i)
            all_task_name = self.r.keys()

            for i in all_task_name:
                check_TaskName = re.search('smt_pzinfo', i)
                if check_TaskName != None:
                    # 将找到的任务队列添加到列表
                    task_list.append(i)
            # 判断列表是否为空，如果为空，则说明没有任务生成

            if len(task_list) == 0:
                print('------未找到任务队列--------')
                time.sleep(60)
            else:
                TaskName = task_list[0]
                with self.safe_dirver as self.SafeDriver:
                    self.run_task(TaskName)

    # 获取本地IP
    def get_ip(self):
        addrs = socket.getaddrinfo(socket.gethostname(), "")
        match = re.search("'192.168.\d+.(\d+)'", str(addrs))
        ip_num = "000"
        if match:
            ip_num = match.group(1)
        return ip_num
        # IP_Address = [item[4][0] for item in addrs if ':' not in item[4][0]][0]
        # return IP_Address


    def save_file_name(self, all_data_num):
        # 根据数据量来区分存储区间
        if all_data_num > 90000000:
            return 100000
        elif all_data_num > 50000000:
            return 50000
        elif all_data_num > 10000000:
            return 30000
        elif all_data_num > 5000000:
            return 20000
        elif all_data_num > 1000000:
            return 10000
        elif all_data_num > 500000:
            return 5000
        elif all_data_num > 100000:
            return 1000
        elif all_data_num > 50000:
            return 500
        elif all_data_num > 10000:
            return 2000
        elif all_data_num > 5000:
            return 100
        elif all_data_num > 1000:
            return 50
        elif all_data_num > 500:
            return 20
        else:
            return 10

    # -----------------------------------项目代码----------------------------------------

    def get_track(self, distance, a):
        track = []
        # 当前位移
        current = 0
        # 计算间隔
        t = 1
        # 初速度
        v = random.uniform(5, 10)
        while current < distance:
            # 初速度 v0
            v0 = v
            # 当前速度 v = v0 + at
            v = v0 + a * t
            # 移动距离 x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def login_YZM(self):
        login_a = random.uniform(0, 5)
        track = self.get_track(300, login_a)
        slider = self.SafeDriver.driver.find_element_by_id('nc_1_n1z')
        ActionChains(self.SafeDriver.driver).click_and_hold(slider).perform()
        for step in track:
            ActionChains(self.SafeDriver.driver).move_by_offset(xoffset=step, yoffset=0).perform()
        time.sleep(0.5)
        source = self.SafeDriver.driver.page_source
        time.sleep(0.5)
        check_error = re.search("Verified", source)
        if check_error != None:
            return '1'
        else:
            return 'error'

    def login(self):
        while True:
            self.SafeDriver.driver.get('https://sellerjoin.aliexpress.com/credential/showcredential.htm?storeNum=2220178')
            source = self.SafeDriver.driver.page_source
            denglu = re.search(r'expressbuyerlogin', source)
            if denglu:
                self.SafeDriver.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button')
                WebDriverWait(self.SafeDriver.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="login-form"]/div[5]/button')))
                login = self.SafeDriver.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button').get_attribute(
                    'textContent')
                if login:
                    zhanghao = self.zhanghao_list[self.zhanghao_num]
                    pwd = 'a123456789'
                    print('当前使用账号:{}'.format(zhanghao))
                    self.SafeDriver.driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(zhanghao)
                    self.SafeDriver.driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(pwd)
                    self.SafeDriver.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button').click()
                    nodenglu = re.search(r'Your account name or password is incorrect', source)
                    yanzhengma = re.search(r'id="nc_1__scale_text"', source)
                    if yanzhengma:
                        result = self.login_YZM()
                        if result == '1':
                            self.SafeDriver.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button').click()
                            if nodenglu == None:
                                print('登陆成功')
                                self.zhanghao_num += 1
                                if self.zhanghao_num == 3:
                                    self.zhanghao_num = 0
                                return '1'
                            else:
                                self.SafeDriver.driver.refresh()
                        else:
                            print('未通过')
                    else:
                        self.SafeDriver.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button').click()
            return '1'

    def slide_YZM(self, a):
        track = self.get_track(262, a)
        slider = self.SafeDriver.driver.find_element_by_id('nc_1_n1z')
        ActionChains(self.SafeDriver.driver).click_and_hold(slider).perform()
        for step in track:
            ActionChains(self.SafeDriver.driver).move_by_offset(xoffset=step, yoffset=0).perform()
        time.sleep(0.5)
        source = self.SafeDriver.driver.page_source
        check_error = re.search("something's wrong", source)
        if check_error == None:
            return '1'
        else:
            return 'error'

    def requests(self, shop_id, file,file_code):
        url = 'https://sellerjoin.aliexpress.com/credential/showcredential.htm?storeNum={}'.format(
            shop_id)
        self.SafeDriver.driver.get(url)
        error_num = 0
        while True:
            source = self.SafeDriver.driver.page_source
            time.sleep(0.5)
            if_have_YZM = re.search('Please slide to verify', source)
            no_denglu = re.search(r'expressbuyerlogin', source)
            if no_denglu != None:
                result = self.login()
                if result == '1':
                    pass
                else:
                    break
            if if_have_YZM != None:
                print('出现验证码')
                time.sleep(0.5)
                result1 = self.slide_YZM(self.a)
                if result1 == 'error':
                    self.SafeDriver.driver.find_element_by_xpath('//div[@id="your-dom-id"]/div/span/a').click()
                    while True:
                        a1 = random.choice(self.a_list)
                        a2 = random.choice(self.a_list)
                        if a1 < a2:
                            break
                    self.a = random.uniform(a1, a2)
                    error_num += 1
                    if error_num == 3:
                        self.r.sadd('smt_pzinfo', shop_id)
                        self.r.srem(self.cache_queue, shop_id)
                        self.error_num += 1
                        if self.error_num > 3:
                            self.SafeDriver.driver.quit()
                            # self.huan_ip()
                            self.SafeDriver.chrome_canshu()
                            result = self.login()
                            self.error_num = 0
                        break
                else:
                    break
            else:
                break
        time.sleep(0.5)
        source = self.SafeDriver.driver.page_source
        check_data = re.search('No Data|system error!', source)
        if check_data != None:
            self.r.srem(self.cache_queue, shop_id)
        else:
            html = etree.HTML(source)
            info_list = html.xpath('//div[contains(@class,"fn-left")]')
            Business_info_list = []
            Business_info_list.append(shop_id)
            for i in info_list:
                try:
                    info = i.xpath('./text()')[0]
                except:
                    info = ''
                Business_info_list.append(info.replace(',', '，').strip())
            Business_info = (',').join(Business_info_list)
            if info_list:
                print(Business_info)
                self.save_data(Business_info, shop_id,file,file_code,source)
            else:
                self.r.sadd('smt_pzinfo', shop_id)
                self.r.srem(self.cache_queue, shop_id)

    def save_data(self, Business_info, shop_id, file,file_code, source):
        try:
            file.write(Business_info + '\n')
            self.bf.insert(shop_id)
            # 采集完成，从缓存队列中删除
            self.r.srem(self.cache_queue, shop_id)
        except:
            self.r.sadd('smt_pzinfo', shop_id)
            self.r.srem(self.cache_queue, shop_id)
            return
        try:
            file_code.write(source + '\n')
        except:
            self.r.sadd('smt_pzinfo', shop_id)
            self.r.srem(self.cache_queue, shop_id)
            return


    def run_task(self, TaskName):
        num = 0
        ip = self.get_ip()
        file = open('D:/selenium/smt/{{速卖通牌照信息_{}}}[店铺ID,公司名称,增值税税号,营业执照注册号,地址,联系人,业务范围,创建时间,登记机关].txt'.format(ip),'a', encoding='utf-8')
        file_code = open('D:/selenium/smt/店铺牌照信息源码/{{smt_html_{}}}.txt'.format(ip), 'a',encoding='utf-8')
        while True:
            result = self.login()
            if result == '1':
                while True:
                    # ---------------------------------------------------------------------
                    shop_id = self.r.spop('{}'.format(TaskName))
                    # 将获取的数据存储到另外一个集合中，防止程序中途停止导致数据丢失
                    if shop_id == None:
                        print('当前采集任务完成')
                        break
                    else:
                        self.r.sadd(self.cache_queue, shop_id)
                        # 判断是不是没有数据的店铺
                        if self.bf.isContains(shop_id):
                            # 采集完成，从缓存队列中删除
                            self.r.srem(self.cache_queue, shop_id)
                            num += 1
                        else:
                            num += 1
                            if num % 100 == 0 and num != 0:
                                while True:
                                    self.SafeDriver.driver.quit()
                                    # self.huan_ip()
                                    self.SafeDriver.chrome_canshu()
                                    result = self.login()
                                    if result == '1':
                                        break
                            self.requests(shop_id, file,file_code)
                break
            file.close()
            file_code.close()


    def run(self):
        # 领取并执行采集任务
        print('--------------------------开始采集--------------------------')
        self.if_task()


zhanghao = []
with open('F:\pycharmproject\scrapy\smt_spider\任务文件\账号列表\账号59-1.txt', 'r', encoding='utf-8') as f:
    for i in f:
        zhanghao.append(i.replace('\n', ''))
# python配置文件路径
mima_dict = {}

for i in [42,55,56,57,59,95,96,97,98,99]:
    mima_dict[i] = ("wzg.22576911","542861")
for i in [10,100,101,102,103,104,105,106]:
    mima_dict[i] = ("wzg.23722832","847983")
ip = get_ip()
ADSL_name = mima_dict.get(ip,"wzg.22576911")
ADSL_pwd = mima_dict.get(ip,"542861")
get = smt_pz_info(zhanghao, ADSL_name, ADSL_pwd)

get.run()
