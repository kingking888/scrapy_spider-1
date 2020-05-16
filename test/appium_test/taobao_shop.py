import time
from appium import webdriver
from appium.webdriver.common import mobileby
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

desired_capabilities = {
    'platformName': 'Android',  # 系统
    'deviceName': '127.0.0.1:62001 device',#'RKKDU18329005156',  # 移动设备号
    # 'platformVersion': '6.0.1',  # 系统版本
    # 'appPackage': 'com.taobao.taobao',  # 操作的app
    # 'appActivity': 'com.taobao.search.sf.MainSearchResultActivity',  # 打开淘宝app首页
    'appPackage': 'com.taobao.live',  # 操作的app
    'appActivity': 'com.taobao.live.HomePageActivity',  # 打开淘宝app首页
    'unicodeKeyboard': True,
    'resetKeyboard': True,
    # 'dontStopAppOnReset': True,
    # 'autoGrantPermissions': True,
    # 'noReset': True,
    # 'automationName': 'uiautomator2',
    'newCommandTimeout': '5000',  # 超时时间
    # 'systemPort': '8202',  # 端口号，操作不用设备使用不同端口号
    # 'udid': 'xxxxxxxx',  # 移动设备号
    'command_executor': 'http://127.0.0.1:4723/wd/hub'  # 和启动命令保持一致
}

class AppiumDemo(object):
    def __init__(self):
        self.driver = webdriver.Remote(command_executor=desired_capabilities['command_executor'],
                                       desired_capabilities=desired_capabilities)
        self.by = mobileby.MobileBy()

    def wait_find_element(self, by_type: str, value: str, driver: WebDriver = None):
        """
        获取单个元素, 显式等待
        :param driver: 驱动对象
        :param by_type: 查找元素的操作
        :param value: 查找元素的方法
        :return:
        """
        driver = driver or self.driver
        if not driver:
            return driver
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator=(by_type, value)))
            return driver.find_element(by_type, value)
        except:
            # self.logger.warning(traceback.format_exc())
            return False

    def wait_find_elements(self, by_type: str, value: str, driver: WebDriver = None):
        """
        获取多个元素, 显式等待
        :param driver:
        :param by_type:
        :param value:
        :return:
        """
        driver = driver or self.driver
        if not driver:
            return driver
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator=(by_type, value)))
            return driver.find_elements(by_type, value)
        except:
            return False

    def get_size(self, driver: WebDriver = None):
        """
        获取屏幕大小
        :param driver:
        :return:
        """
        driver = driver or self.driver
        if not driver:
            return driver

        x = driver.get_window_size()['width']
        y = driver.get_window_size()['height']
        return [x, y]

    def swipe_up(self, driver: WebDriver = None, _time: int = 1000):
        """
        向上滑动
        :param driver:
        :param _time:
        :return:
        """
        driver = driver or self.driver
        if not driver:
            return driver
        try:
            size = self.get_size(driver)
            x1 = int(size[0] * 0.5)  # 起始x坐标
            y1 = int(size[1] * 0.80)  # 起始y坐标
            y2 = int(size[1] * 0.30)  # 终点y坐标
            driver.swipe(x1, y1, x1, y2, _time)
            return True
        except:
            return False

    def execute(self, seed):
        self.swipe_up(self.driver)
        dianpu = self.wait_find_element(by_type=self.by.XPATH, value='//android.widget.TextView[@text="店铺"]')#点击店铺
        if dianpu:
            dianpu.click()
        # 点击店铺搜索
        search_keyword = self.wait_find_element(by_type=self.by.ID, value='com.taobao.taobao:id/search_bar_wrapper')
        if search_keyword:
            search_keyword.click()
        #输入关键词
        search_keyword = self.wait_find_element(by_type=self.by.ID, value='com.taobao.taobao:id/searchEdit')
        if search_keyword:
            search_keyword.clear().send_keys(seed['keyword'])
        search = self.wait_find_element(by_type=self.by.ACCESSIBILITY_ID, value='搜索')
        time.sleep(1)
        if search:
            search.click()
        shop_list = self.wait_find_elements(by_type=self.by.XPATH, value='//android.widget.FrameLayout/android.widget.TextView[@text="进店"]')
        if shop_list:
            for shop_info in shop_list:
                shop_info.click()
                # 点击全部宝贝
                totle = self.wait_find_element(by_type=self.by.XPATH, value='//android.widget.FrameLayout[@content-desc="全部宝贝"]/android.widget.ImageView')
                if totle:
                    totle.click()
                el8 = self.wait_find_element(by_type=self.by.ID, value="列表模式")
                if el8:
                    el8.click()
                el9 = self.wait_find_element(by_type=self.by.ID, value="销量")
                if el9:
                    el9.click()
                for i in range(100):
                    # 获取这一屏的数据
                    item_list = self.wait_find_elements(by_type=self.by.ID, value="com.taobao.taobao:id/title")

                    if item_list:
                        for item_info in item_list:
                            print(item_info.text)
                    self.swipe_up()  # 向上滑动
                    time.sleep(0.1)  # 一定要延时
                self.driver.back()  # 返回上一级
            self.driver.back()


def main():
    seed = {
        'keyword': "店铺"
    }
    spider = AppiumDemo()
    while True:
        spider.execute(seed=seed)


if __name__ == '__main__':
    main()