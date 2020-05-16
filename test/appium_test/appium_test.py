import time
from appium import webdriver
from appium.webdriver.common import mobileby
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


information = {"platformName":"Android",
               'deviceName': "RKKDU18329005156",
               'appPackage': "com.taobao.taobao",
               'appActivity': "com.taobao.search.searchdoor.SearchDoorActivity",#com.taobao.search.sf.MainSearchResultActivity
               'unicodeKeyboard': "True",  #绕过手机键盘操作，unicodeKeyboard是使用unicode编码方式发送字符串
               'resetKeyboard': "True"  # 绕过手机键盘操作，resetKeyboard是将键盘隐藏起来
               }
driver_server='http://127.0.0.1:4723/wd/hub'
driver=webdriver.Remote(driver_server, information)
wait=WebDriverWait(driver,300000)
by = mobileby.MobileBy()
time.sleep(5)
el1 = driver.find_element_by_id("com.taobao.taobao:id/searchEdit")
el1.send_keys("店铺")
time.sleep(5)

el2 = driver.find_element_by_accessibility_id("搜索")
el2.click()
time.sleep(5)
el3 = driver.find_element_by_xpath('//android.widget.TextView[@text="店铺"]')
el3.click()
time.sleep(5)

el4 = driver.find_element_by_xpath("//android.widget.FrameLayout/android.view.View[2]")
el4.click()
time.sleep(5)

el5 = driver.find_element_by_xpath('//android.widget.FrameLayout[@content-desc="全部宝贝"]/android.widget.ImageView')
el5.click()
time.sleep(5)
el6 = driver.find_element_by_xpath('//android.widget.TextView[@resource-id="com.taobao.taobao:id/title"]')
print(el6.text)

driver.back()
driver.swipe(300, 1200, 300, 100)
driver.swipe(300, 1200, 300, 100)
el6s = driver.find_elements_by_id("com.taobao.taobao:id/layer_container")
for el6 in el6s:
    print(el6.text)
driver.swipe(300, 1200, 300, 100)
driver.swipe(300, 1200, 300, 100)
driver.swipe(300, 1200, 300, 100)
driver.swipe(300, 1200, 300, 100)


