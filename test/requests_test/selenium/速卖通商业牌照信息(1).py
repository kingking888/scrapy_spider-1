import re, os, time, redis, random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium import webdriver
from Bloomfilter import BloomFilter
from lxml import etree
from tqdm import tqdm


class smt_pz_info(object):
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'}
        self.r = redis.Redis(host='192.168.0.230', port=6379, db=0, decode_responses=True)
        self.chrome_canshu()
        self.path = ''
        self.bf = BloomFilter('SmtPzInfoSpider')
        self.bf2 = BloomFilter('NoHaveInfoID')
        # self.write()
        self.huan_ip()
        self.zhanghao_list = ['e1234567@qq.com', 'g1234567@qq.com', 'e123456@qq.com', 'f123456@qq.com',
                              'c112233@qq.com']


    # 检测当前程序进程pid,并存入文本中
    def write(self):
        pid = os.getpid()
        with open('pid.txt', 'w', encoding='utf-8') as f:
            f.write(str(pid))

    # ----------------------自动拨号更换IP-----------------------------
    def connect(self):
        name = "宽带连接"
        username = 'wzg.22576911'
        password = "542861"
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

    # -----------------------------------项目代码----------------------------------------
    def chrome_canshu(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--proxy-server=127.0.0.1:6363')
        self.options.add_argument('disable-infobars')
        # options.add_argument('--incognito')
        # 以最高权限运行
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("disable-infobars")
        self.options.add_argument("disable-web-security")
        # 设置为无头
        # self.options.add_argument("--headless")
        # 设置全屏页面
        # self.options.add_argument("--start-maximized")
        self.options.add_argument("--log-level=3")
        No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        self.options.add_experimental_option("prefs", No_Image_loading)
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe', options=self.options)

    def login(self):
        try:
            while True:
                self.driver.get('https://sellerjoin.aliexpress.com/credential/showcredential.htm?storeNum=2220178')
                source = self.driver.page_source
                denglu = re.search(r'expressbuyerlogin', source)
                if denglu:
                    self.driver.switch_to.frame('alibaba-login-box')
                    self.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button')
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="login-form"]/div[5]/button')))
                    login = self.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button').get_attribute(
                        'textContent')
                    if login:
                        zhanghao = random.choice(self.zhanghao_list)
                        # self.zhanghao = self.zhanghao_list[num]
                        pwd = 'a123456789'
                        print('当前使用账号:{}'.format(zhanghao))
                        self.driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(zhanghao)
                        self.driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(pwd)
                        self.driver.find_element_by_xpath('//*[@id="login-form"]/div[5]/button').click()
                        # try:
                        #     # ACCESS 按钮
                        #     source1 = self.driver.page_source
                        #     time.sleep(5)
                        #     tishi = re.search('Access Now', source1)
                        #     if tishi != None:
                        #         self.driver.switch_to.frame('alibaba-login-box')
                        #         ACCESS = self.driver.find_element_by_xpath(
                        #             '//button[contains(@class,"fm-button")]').get_attribute('textContent')
                        #         print(ACCESS)
                        #         if ACCESS:
                        #             self.driver.find_element_by_xpath('//button[contains(@class,"fm-button")]').click()
                        # except:
                        #     print('未出现已登陆按钮')
                        source = self.driver.page_source
                        nodenglu = re.search(r'Your account name or password is incorrect', source)
                        if nodenglu == None:
                            print('登陆成功')
                            return '1'
                else:
                    print('未检测到登陆页面')
                    return '2'
        except:
            print('----报错!!!!!----')
            return '1'

    def get_track(self, distance):
        track = []
        # 当前位移
        current = 0
        # 计算间隔
        t = 1
        # 初速度
        v = 0
        a = random.uniform(0.5, 3)
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

    def slide_YZM(self):
        track = self.get_track(262)
        slider = self.driver.find_element_by_id('nc_1_n1z')
        ActionChains(self.driver).click_and_hold(slider).perform()
        for step in track:
            ActionChains(self.driver).move_by_offset(xoffset=step, yoffset=0).perform()
        time.sleep(0.5)
        source = self.driver.page_source
        check_error = re.search("something's wrong", source)
        if check_error == None:
            return '1'
        else:
            return 'error'

    def requests(self):
        result = self.login()
        with open('F:/Pycharm/Project/速卖通商品列表/速卖通商业牌照信息/{2_2_速卖通_有效_店铺评分_浙江}[店铺ID].txt', 'r', encoding='utf-8') as f:
            shop_id_list = f.readlines()
        num = 0
        if result == '1':
            for index, shop_id in enumerate(tqdm(shop_id_list)):
                shop_id = shop_id.replace('\n', '')
                if self.bf2.isContains(shop_id):
                    num += 1
                else:
                    num += 1
                    if index % 20 == 0 and index != 0:
                        while True:
                            self.driver.quit()
                            self.huan_ip()
                            self.chrome_canshu()
                            result = self.login()
                            if result == '1':
                                break
                    url = 'https://sellerjoin.aliexpress.com/credential/showcredential.htm?storeNum={}'.format(shop_id)
                    self.driver.get(url)

                    while True:
                        source = self.driver.page_source
                        time.sleep(0.5)
                        if_have_YZM = re.search('Please slide to verify', source)
                        denglu = re.search(r'expressbuyerlogin', source)
                        if denglu != None:
                            result = self.login()
                            if result == '1':
                                break
                        if if_have_YZM != None:
                            print('出现验证码')
                            time.sleep(1)
                            result1 = self.slide_YZM()
                            if result1 == 'error':
                                self.driver.find_element_by_xpath('//div[@id="your-dom-id"]/div/span/a').click()
                            else:
                                break
                        else:
                            break
                    time.sleep(2)
                    source = self.driver.page_source
                    check_data = re.search('No Data', source)
                    if check_data != None:
                        self.bf2.insert(shop_id)
                        with open('F:/Pycharm/Project/速卖通商品列表/速卖通商业牌照信息/无信息的店铺id.txt', 'a', encoding='utf-8') as f:
                            f.write(shop_id + '\n')
                    else:
                        html = etree.HTML(source)
                        info_list = html.xpath('//div[@id="container"]/div/div/text()')
                        Business_info_list = []
                        if len(info_list) == 16:
                            for num, i in enumerate(info_list):
                                if num % 2 != 0:
                                    Business_info_list.append(i.replace(',', ' '))
                            Business_info = (',').join(Business_info_list)
                            with open('F:/Pycharm/Project/速卖通商品列表/速卖通商业牌照信息/输出结果/速卖通牌照信息.txt', 'a',
                                      encoding='utf-8') as f:
                                f.write(Business_info + '\n')
                            # with open('F:/Pycharm/Project/速卖通商品列表/速卖通商业牌照信息/源码/smt_html.txt', 'a',
                            #           encoding='utf-8') as f:
                            #     f.write(source + '\n')


run = smt_pz_info()
run.requests()
