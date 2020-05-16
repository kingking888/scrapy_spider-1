import time
from appium import webdriver

class DouYinApp():
    def __init__(self):
        self.params = {}
        self.params['deviceName'] = '127.0.0.1:62001 device'
        self.params['platformVersion'] = '5.1.1'
        self.params['automationName'] = 'Appium'
        self.params['platformName'] = 'Android'
        self.params['autoAcceptAlerts'] = 'true'
        self.params['noReset'] = 'true'
        self.params['appPackage'] = 'com.ss.android.ugc.aweme'
        self.params['appActivity'] = 'com.ss.android.ugc.aweme.live.LivePlayActivity'
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_capabilities=self.params)

    def swipDown(self, n):
        L = self.driver.get_window_size()
        x = L['width'] * 0.5
        y1 = L['height'] * 0.8
        y2 = L['height'] * 0.3
        num = 0
        # while num < n:
        while True:
            self.driver.swipe(x, y1, x, y2, 6000)
            # num += 1

    def swipLeft(self):
        L = self.driver.get_window_size()
        x1 = L['width'] * 0.8
        x2 = L['width'] * 0.3
        y1 = L['height'] * 0.5

        self.driver.swipe(x1, y1, x2, y1, 500)


    def login(self):
        self.driver.find_element_by_xpath('//android.widget.TextView[@text="我"]').click()
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//android.widget.TextView[@text="密码登录"]').click()
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//android.widget.EditText[@text="请输入手机号"]').send_keys('18595794414')
        time.sleep(0.5)
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/dfk').send_keys('525748037')
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//android.widget.CheckBox').click()
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//android.widget.TextView[@text="登录"]').click()
        time.sleep(1)
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/ep8').click()
        print('登录成功')

    def guanggao(self):
        try:
            guanggao = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/eb')
        except:
            guanggao = ''
        return guanggao

    def stream(self):
        self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/cnt').click()


    def more(self):
        self.driver.find_element_by_xpath('//android.widget.TextView[@text="更多直播"]').click()


    def run(self, n):
        try:
            guanggao = self.guanggao()
            if guanggao != '':
                guanggao.click()
            print('--------跳过广告--------')
            time.sleep(1)

            # print('开始登录')
            # self.login()
            # time.sleep(5)

            self.stream()
            print('----------直播---------')
            time.sleep(3)

            self.swipLeft()
            print('----------更多---------')
            time.sleep(2)

            print('--------开始爬取-----------')
            self.swipDown(n)

        except BaseException as e:
            print(e)

if __name__ == '__main__':
    douyin = DouYinApp()
    douyin.run(100)
