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
    'noReset': True,
    # 'automationName': 'uiautomator2',
    'newCommandTimeout': '5000',  # 超时时间
    # 'systemPort': '8202',  # 端口号，操作不用设备使用不同端口号
    # 'udid': 'xxxxxxxx',  # 移动设备号
    'command_executor': 'http://localhost:4723/wd/hub'  # 和启动命令保持一致
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

    def swipe_up(self, driver: WebDriver = None, _time: int = 500):
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
            y1 = int(size[1] * 0.9)  # 起始y坐标
            y2 = int(size[1] * 0.2)  # 终点y坐标
            driver.swipe(x1, y1, x1, y2, _time)
            return True
        except:
            return False

    def swipe_up_left(self, driver: WebDriver = None, _time: int = 300):
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
            x1 = int(size[0] * 0.85)  # 起始x坐标
            y1 = int(size[1] * 0.5)  # 起始y坐标
            x2 = int(size[1] * 0.2)  # 终点y坐标
            driver.swipe(x1, y1, x2, y1, _time)
            return True
        except:
            return False

    def execute(self,last_num):
        new = self.wait_find_element(by_type=self.by.ID,value="android:id/button2")
        if new:
            new.click()
        type_num = 0+last_num
        for i in range(type_num):
            self.swipe_up_left(self.driver, 300)
            time.sleep(2)
        while type_num<16:
            num = 0
            name = ""
            while True:
                self.swipe_up(self.driver,200)
                time.sleep(0.2)
                try:
                    items = self.wait_find_elements(by_type=self.by.CLASS_NAME, value="android.widget.TextView")
                except:
                    return 0, type_num

                if len(items)>2:
                    try:
                        name1 = items[-2].text
                    except:
                        return 0, type_num
                    print(name1)
                    if name1 == name and name1 != " 观看":#
                        num += 1
                    elif name1 == "山海镜花":
                        return 0, type_num
                    else:
                        name = name1
                        num = 0
                    if num > 2:
                        break
                else:
                    return 0,type_num
            self.swipe_up_left(self.driver, 300)
            type_num += 1
            time.sleep(2)
        return 1,0


def main():
    num = 0
    while True:
        spider = AppiumDemo()
        status,num = spider.execute(num)
        del spider
        time.sleep(3)
        if status == 1:
            time.sleep(1800)


if __name__ == '__main__':
    main()