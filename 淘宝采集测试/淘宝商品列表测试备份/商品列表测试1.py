import requests
from selenium import webdriver
from lxml import etree
import re, time, redis
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from threading import Thread


class GetGoodsList(object):
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
        self.chrome_canshu()
        self.r0 = redis.Redis(host='192.168.0.230', port=6379, db=0, decode_responses=True)

    def chrome_canshu(self):
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 1}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--proxy-server=127.0.0.1:6363')
        options.add_argument('disable-infobars')
        # options.add_argument('--incognito')
        options.add_argument('--no-sandbox')
        options.add_argument("disable-infobars")
        options.add_argument("disable-web-security")
        # options.add_argument("--headless")
        # options.add_argument("--start-maximized")
        options.add_argument("--log-level=3")
        No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", No_Image_loading)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)

    def account(self):
        username = self.driver.find_element_by_xpath('//*[@id="TPL_username_1"]')
        username.clear()
        username.send_keys('a121442819')
        password = self.driver.find_element_by_xpath('//*[@id="TPL_password_1"]')
        password.clear()
        password.send_keys('..gq52zydl..')
        time.sleep(1)

    def slide_YZM(self):
        slider = self.driver.find_element_by_id('nc_1_n1z')
        ActionChains(self.driver).click_and_hold(slider).perform()
        ActionChains(self.driver).move_by_offset(xoffset=275, yoffset=0).perform()
        time.sleep(0.5)
        # 获取页面
        source2 = self.driver.page_source
        # 检查滑动验证码是否出错
        check_error = re.search('哎呀，出错了，点击', source2)
        # 检查滑动验证码是否成功
        check_successful = re.search('验证通过', source2)
        if check_error != None:
            return 'check_error'
        if check_successful != None:
            print('滑动验证码解锁成功')
            return 'check_successful'

    def __is_element_exist(self, selector):
        """
        检查是否存在指定元素
        :param selector:
        :return:
        """
        try:
            self.driver.find_element_by_css_selector(selector)
            return True
        except NoSuchElementException:
            return False

    def __lock_exist(self):
        """
        判断是否存在滑动验证
        :return:
        """
        return self.__is_element_exist('#nc_1_wrapper') and self.driver.find_element_by_id(
            'nc_1_wrapper').is_displayed()

    def get_cookies(self):
        # 获取cookie
        cookie_list = self.driver.get_cookies()
        # 将selenium获取的cookie转化成requests请求可使用的cookie
        cookie_str = ''
        for index, cookie in enumerate(cookie_list):
            cookie_str += cookie['name'] + '=' + cookie['value'] + ';'
        return cookie_str

    def login_input(self):
        self.account()
        source1 = self.driver.page_source
        # 判断是否出现滑动验证码
        if self.__lock_exist():
            print('出现滑动验证码')
            # 解锁滑动验证码
            result = self.slide_YZM()
            if result == 'check_error':
                return print('滑动验证码出错，请稍后重新启动程序')

            elif result == 'check_successful':
                # 点击登陆
                login = self.driver.find_element_by_xpath('//*[@id="J_SubmitStatic"]').click()
        else:
            # 点击登陆
            login = self.driver.find_element_by_xpath('//*[@id="J_SubmitStatic"]').click()

    def login(self):
        login_url = 'https://i.taobao.com/my_taobao.htm?spm=a21bo.2017.201864-1.1.1a2811d9x9mCMM&ad_id=&am_id=&cm_id=&pm_id=1501036000a02c5c3739&nekot=YTEyMTQ0MjgxOQ==1568180280608'
        self.driver.get(login_url)
        if self.driver.find_element_by_id('J_QRCodeLogin').is_displayed():
            self.driver.find_element_by_id('J_Quick2Static').click()
            self.login_input()
            source = self.driver.page_source
            check_login = re.search(r'会员名/邮箱/手机号', source)
            if check_login != None:
                self.login_input()
        else:
            self.login_input()
            source = self.driver.page_source
            check_login = re.search(r'会员名/邮箱/手机号', source)
            if check_login != None:
                self.login_input()

    def save_data(self, GoodsInfo):
        with open('', 'a', encoding='utf-8') as f:
            f.write(GoodsInfo + '\n')

    def get_GoodsInfo(self, goods_list_url2, page_num):
        time.sleep(0.1)
        self.driver.get(goods_list_url2)
        source = self.driver.page_source
        check_html = re.search('rgv587_flag', source)
        if check_html == None:
            html_list = source.split('data-id')
            for i in range(len(html_list)):
                if i != 0:
                    # 商品ID
                    goods_id = re.findall(r'=\\"(.*?)\\">', html_list[i])
                    # 销售量
                    sales_num = re.findall(r'<span class=\\\"sale-num\\\">(.*?)</span>', html_list[i])
                    # 原价
                    original_price = re.findall(r'class=\\\"s-price\\\">(.*?) </span>', html_list[i])
                    # 促销价
                    promotion_price = re.findall(r'class=\\\"c-price\\\">(.*?)</span>', html_list[i])
                    # 评论数
                    comment_num = re.findall(r'"_blank\\\"><span>(.*?)</span>', html_list[i])
                    # 商品链接
                    goods_url = re.findall(r'class=\\\"J_TGoldData\\\" href=\\\"(.*?)\\\"', html_list[i])
                    try:
                        goods_id = goods_id[0]
                    except:
                        goods_id = ''
                    try:
                        original_price = original_price[0]
                    except:
                        original_price = ''
                    try:
                        promotion_price = promotion_price[0]
                    except:
                        promotion_price = ''
                    try:
                        sales_num = sales_num[0]
                    except:
                        sales_num = ''
                    try:
                        comment_num = comment_num[0]
                    except:
                        comment_num = ''
                    try:
                        goods_url = goods_url[0]
                    except:
                        goods_url = ''
                    # print('-' * 50)
                    # print(goods_id + ',' + original_price + ',' + promotion_price + ',' + sales_num + ',' + comment_num + ',' + goods_url)
                    # GoodsIinfo = goods_id + ',' + original_price + ',' + promotion_price + ',' + sales_num + ',' + comment_num + ',' + goods_url
                    # # self.save_data(GoodsIinfo)
            print('-----------当前第{}页-----------'.format(page_num))
            print('该页商品数：{}'.format(len(html_list) - 1))
            # self.r0.set(goods_list_url2,goods_list_url2)
        else:
            print(check_html)
            print('未找到有效数据')
            x > 0

    def look_goods_num(self, shop_id, source):
        html = etree.HTML(source)
        # if check_html == None:
        # 该店铺商品总数
        try:
            html_goods_num = html.xpath('//*[@id="shop-search-list"]/div/div[2]/span/text()')[0]
            # print(html_goods_num)
        except:
            html_goods_num = 0
        try:
            ALLPageNum = html.xpath('//div[@class="pagination pagination-mini"]/span/text()')[0]
            # print(ALLPageNum)
            all_page_num = ALLPageNum.split('/')[-1]
        except:
            all_page_num = 0
        all_page_count = int(all_page_num)
        print('店铺ID：{},该店铺商品列表共有{}页,共有{}件商品'.format(shop_id, all_page_num, html_goods_num))
        return all_page_count

    def request_GoodsList(self, shop_id, all_page_count):
        # 打开新的窗口
        self.driver.execute_script("window.open('')")
        # 切换到第二个窗口
        self.driver.switch_to.window(self.driver.window_handles[1])
        threads = []
        url_list = []
        num = 0
        page = 0
        for page_num in range(1, all_page_count + 1):
            goods_list_url2 = 'https://shop{}.taobao.com/i/asynSearch.htm?_ksTS=1568180617323_176&mid=w-11445511953-0&wid=11445511953&path=/search.htm&search=y&pageNo={}'.format(
                shop_id, page_num)
            check_base_url = self.r0.exists(goods_list_url2)
            if check_base_url == 1:
                num += 1
            else:
                num += 1
                try:
                    if num % 10 == 0:
                        url_list.append(goods_list_url2)
                        for url in url_list:
                            page += 1
                            t = Thread(target=self.get_GoodsInfo(url, page))
                            threads.append(t)
                            t.start()
                        for t in threads:
                            t.join()
                        url_list.clear()
                    else:
                        url_list.append(goods_list_url2)
                        if num == all_page_count:
                            for url in url_list:
                                page += 1
                                t = Thread(target=self.get_GoodsInfo(url, page))
                                threads.append(t)
                                t.start()
                            for t in threads:
                                t.join()
                            url_list.clear()
                except:
                    return 'error'
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return 'ture'

    def get_shop_id(self):
        with open('shop_id_list.txt', 'r', encoding='utf-8') as f:
            data = f.readlines()
            shop_id_set = set(data)
        shop_id_list = list(shop_id_set)
        return shop_id_list

    def shop_yzm(self):
        self.driver.switch_to.frame('sufei-dialog-content')
        slider = self.driver.find_element_by_id('nc_1_n1z')
        ActionChains(self.driver).click_and_hold(slider).perform()
        ActionChains(self.driver).move_by_offset(xoffset=275, yoffset=0).perform()
        time.sleep(0.5)
        # 获取页面
        source2 = self.driver.page_source
        # 检查滑动验证码是否出错
        check_error = re.search('哎呀，出错了，点击', source2)
        # 检查滑动验证码是否成功
        check_successful = re.search('验证通过', source2)
        if check_error != None:
            return 'check_error'
        if check_successful != None:
            print('滑动验证码解锁成功')
            return 'check_successful'

    def run(self):
        # 登陆，获取cookie
        cookies = self.login()
        # print(cookies)
        shop_id_list = self.get_shop_id()
        url2 = 'https://shop{}.taobao.com/search.htm'.format('125646855')
        self.driver.get(url2)
        for shop_id in shop_id_list:
            shop_id = shop_id.replace('\n', '')
            # shop_id = '125646855'
            while True:
                time.sleep(0.5)
                source = self.driver.page_source
                all_page_count = self.look_goods_num(shop_id, source)
                if all_page_count > 0:
                    requests_result = self.request_GoodsList(shop_id, all_page_count)
                elif all_page_count == 0:
                    if self.__is_element_exist('#sufei-dialog-content'):
                        print('出现滑动验证码')
                        # 解锁滑动验证码
                        yzm_result = self.shop_yzm()
                        if yzm_result == 'check_error':
                            self.driver.refresh()
                            # return print('滑动验证码出错，请稍后重新启动程序')
                            # result = self.request_GoodsList(shop_id, source, url2)
                        elif yzm_result == 'check_successful':
                            requests_result = self.request_GoodsList(shop_id, source)
                if requests_result == 'ture':
                    break
                elif requests_result == 'error':
                    self.driver.close()
                    # 切换回第一个窗口
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    url2 = 'https://shop{}.taobao.com/search.htm'.format('125646855')
                    self.driver.get(url2)


main = GetGoodsList()
main.run()
