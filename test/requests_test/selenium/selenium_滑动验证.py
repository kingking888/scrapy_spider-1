import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from urllib import parse
from lxml import etree
import csv
from PIL import Image


class SeleniumTest():#怎么做并发的selenium，可以结合scrapy以及多线的东西
    def __init__(self,timeout=20,window_height=900,window_width=900):#这里进行设置
        self.driver = webdriver.Chrome()
        #设置时间显示框大小
        if window_height and window_width:
            #self.driver.set_window_position(100,100)
            #self.driver.set_window_size(900,900)

            self.driver.maximize_window()#全屏
        self.driver.set_page_load_timeout(timeout)#页面加载超时时间
        self.wait = WebDriverWait(driver=self.driver,timeout=20)#等待

    def getpage(self,url):#直接渲染得到页面
        try:
            time1 = time.time()
            self.driver.get(url)
            time2 = time.time()

            body1 = self.driver.page_source
            #状态码等东西能加进去？
            time3 = time.time()
            print("时间：",time2-time1,time3-time2)
            return body1

        except Exception as e:
            print("发生错误")
            print(e)

    def login(self,url,login_xpath):
        self.driver.get(url)
        self.driver.get("https://www.baidu.com")
        A = self.driver.current_window_handle
        self.driver.execute_script('window.open("https://www.sogou.com");')
        time.sleep(1)
        self.driver.close()
        self.driver.quit()

        self.wait.until(EC.presence_of_element_located((By.XPATH, login_xpath))).click()
        time.sleep(2)
        self.driver.find_element_by_css_selector(".title-tab.text-center").find_element_by_xpath("./div[2]").click()
        time.sleep(1)

        #a = self.driver.find_element_by_xpath('//div[@class="title-tab text-center"]/div[2]').submit()#这里的空格要标准化，看xpath文档
        self.driver.find_element_by_css_selector(".modulein.modulein1.mobile_box.f-base.collapse.in").find_element_by_xpath("./div[2]/input").send_keys("15957194776")
        a = self.driver.find_element_by_css_selector(".modulein.modulein1.mobile_box.f-base.collapse.in").find_element_by_xpath("./div[3]/input")
        a.send_keys("imiss968")
        a.send_keys(Keys.ENTER)
        #self.driver.find_element_by_css_selector(".modulein.modulein1.mobile_box.f-base.collapse.in").find_element_by_xpath("./div[5]").click()#点击登入按钮
        #submit怎么用，相当于回车
        time.sleep(1)

        im1 = self.jietu(".gt_cut_fullbg.gt_show","yanzhengma1.png",1.25)
        anniu = self.driver.find_element_by_css_selector(".gt_slider_knob.gt_show")
        ActionChains(self.driver).click_and_hold(anniu).perform()
        #当你调用ActionChains的方法时，不会立即执行，而是会将所有的操作按顺序存放在一个队列里，当你调用perform()方法时，队列中的时间会依次执行
        time.sleep(1)
        im2 = self.jietu(".gt_cut_fullbg.gt_show","yanzhengma2.png",1.25)
        distance = int(self.get_distance(im1,im2))/1.25+7
        result = self.get_path(distance)
        for x in result:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()

        time.sleep(0.5)
        ActionChains(self.driver).release(anniu).perform()
        print("haole")

    @classmethod
    def num(cls,num):
        num = num

    def jietu(self,element_xpath,name,proportion=1.0):
        self.driver.save_screenshot(name)
        im = Image.open(name)
        if element_xpath:
            yezhengma = self.driver.find_element_by_css_selector(element_xpath)
            left = yezhengma.location['x']*proportion#在设置中浏览器全屏，乘以电脑的缩放比例
            top = yezhengma.location['y']*proportion
            right = (yezhengma.location['x'] + yezhengma.size['width'])*proportion
            bottom = (yezhengma.location['y'] + yezhengma.size['height'])*proportion
            im = im.crop((left, top, right, bottom))
            im.save(name)
        return im

    def get_distance(self,bg_Image, fullbg_Image):

        # 阈值
        threshold = 200
        dif_list = set()

        for i in range( bg_Image.size[0]):
            for j in range(bg_Image.size[1]):
                bg_pix = bg_Image.getpixel((i, j))
                fullbg_pix = fullbg_Image.getpixel((i, j))
                r = abs(bg_pix[0] - fullbg_pix[0])
                g = abs(bg_pix[1] - fullbg_pix[1])
                b = abs(bg_pix[2] - fullbg_pix[2])

                if r + g + b > threshold:
                    dif_list.add(i)

        avg = sum(dif_list)/len(dif_list)
        avg_list1 = [ i for i in dif_list if i < avg]
        avg_list2 = [ i for i in dif_list if i > avg]
        avg1 = sum(avg_list1)/len(avg_list1)
        avg2 = sum(avg_list2)/len(avg_list2)

        return avg2-avg1

    def get_path(self,distance):
        result = []
        current = 0
        mid = distance * 4 / 5
        t = 0.2
        v = 0
        while current < (distance - 10):
            if current < mid:
                a = 2
            else:
                a = -3
            v0 = v
            v = v0 + a * t
            s = v0 * t + 0.5 * a * t * t
            current += s
            result.append(round(s))
        return result


def read_csv(file_name,columns):
    data = []
    with open(file_name,"r",encoding="utf-8-sig") as csvfile:

        csv_reader = csv.reader(csvfile)  # 读取csvfile中的文件
        data_header = next(csv_reader)  # 读取第一行每一列的标题 next为读取下一行

        for row in csv_reader:  # 将csv 文件中的数据保存到data中
            data.append(row[columns-1])#选择所需要的数据，###这里可以优化下传入所需的参数进行优化
    return data_header,data

def write_csv(filename,header,data):
    with open(filename, "w",newline="") as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerow(header)
        for i in data:
            csvWriter.writerow(i)
        csvFile.close()

if __name__ == "__main__":
    file = "D://data/tianyancha.CSV"
    file1 = "d://data/tianyanche_output.csv"
    headers,company_name = read_csv(file,1)
    test1 = SeleniumTest(timeout=30, window_height=900, window_width=900)
    address_list =[]
    for i in range(len(company_name)):

        test1.login("https://www.tianyancha.com/",'//*[@id="web-content"]/div/div[1]/div[1]/div/div/div[2]/div/div[4]/a')
        #test1.login("https://www.126.com/",'//*[@id="web-content"]/div/div[1]/div[1]/div/div/div[2]/div/div[4]/a')

        url = "https://www.tianyancha.com/search?key="+parse.quote(company_name[i])
        text = test1.getpage(url)
        time.sleep(random.randint(6,10))

        html = etree.HTML(text)
        url1 = html.xpath('//*[@id="web-content"]/div/div[1]/div/div[3]/div[1]/div/div[3]/div[1]/a/@href')

        text1 = test1.getpage(str(url1))
        html1 = etree.HTML(text1)
        address = html1.xpath('//*[@id="_container_baseInfo"]/table[2]/tbody/tr[9]/td[2]/text()')
        time.sleep(3)

        address = ""
        address_list.append(str(address))
    headers =[headers[0],"地址"]
    data = [[company_name[i],address_list[i]]for i in range(len(company_name))]
    write_csv(file1,headers,data)
