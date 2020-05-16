import asyncio
import time, random
from pyppeteer.launcher import launch  # 控制模拟浏览器用
from retrying import retry  # 设置重试次数用的
import random,numpy


async def main(username, pwd, url):  # 定义main协程函数，
    # 以下使用await 可以针对耗时的操作进行挂起
    browser = await launch({'headless': False, 'args': ['--no-sandbox'], })  # 启动pyppeteer 属于内存中实现交互的模拟器
    page = await browser.newPage()  # 启动个新的浏览器页面
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')

    await page.goto(url)  # 访问登录页面
    # 替换淘宝在检测浏览时采集的一些参数。
    # 就是在浏览器运行的时候，始终让window.navigator.webdriver=false
    # navigator是windiw对象的一个属性，同时修改plugins，languages，navigator 且让
    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    # 使用type选定页面元素，并修改其数值，用于输入账号密码，修改的速度仿人类操作，因为有个输入速度的检测机制
    # 因为 pyppeteer 框架需要转换为js操作，而js和python的类型定义不同，所以写法与参数要用字典，类型导入
    # await page.waitFor('#alibaba-login-box')
    # a = page.frames[1]

    await page.type('#fm-login-id', username, {'delay': input_time_random() - 50})
    await page.type('#fm-login-password', pwd, {'delay': input_time_random()})

    # await page.screenshot({'path': './headless-example-result.png'})    # 截图测试

    # 检测页面是否有滑块。原理是检测页面元素。
    slider = 1#await page.Jeval('#nc_1_n1z', 'node => node.style')  # 是否有滑块
    #
    if slider:
        print('当前页面出现滑块')
        # await page.screenshot({'path': './headless-login-slide.png'}) # 截图测试
        flag, page = await mouse_slide(page=page)  # js拉动滑块过去。
        if flag:
            # await page.keyboard.press('Enter')  # 确保内容输入完毕，少数页面会自动完成按钮点击
            print("print enter", flag)
            await page.evaluate('''document.querySelector(".fm-button.fm-submit.password-login").click()''')  # 如果无法通过回车键完成点击，就调用js模拟点击登录按钮。
            await page.waitForNavigation()

            # time.sleep(2)
            # cookies_list = await page.cookies()
            # print(cookies_list)
            # await get_cookie(page)  # 导出cookie 完成登陆后就可以拿着cookie玩各种各样的事情了。
    else:
        await page.keyboard.press('Enter')
        print("print enter")
        # await page.evaluate('''document.getElementById("J_SubmitStatic").click()''')
        await page.waitFor(1)
        await page.waitForNavigation()
        # res = await page.content()

    await goto_page(page)
    # await get_cookie(page)
    # time.sleep(100)


    # try:
    #     global error  # 检测是否是账号密码错误
    #     print("error_1:", error)
    #     error = await page.Jeval('.error', 'node => node.textContent')
    #     print("error_2:", error)
    # except Exception as e:
    #     error = None
    # finally:
    #     if error:
    #         print('确保账户安全重新入输入')
    #         # 程序退出。
    #         loop.close()
    #     else:
    #         print(page.url)



async def goto_page(page):
    num = 0
    with open(r"C:\Users\Administrator\Desktop\{smt_shopid}[shopid].txt","r",encoding="utf-8") as f:
        for i  in f:
            print(num)
            num += 1
            i = i.strip()
            await get_page(page,i)


async def get_page(page,id):
            url = "https://sellerjoin.aliexpress.com/credential/showcredential.htm?storeNum={}".format(id)
            await page.goto(url)
            await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
            await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            statue,page = await mouse_slide(page)
            # await page.waitForNavigation()
            shopid = id
            if statue:
                company_dict = {"shopid":shopid,
                                "Company name：": "",
                                "VAT number：": "",
                                "registration number：": "",
                                "Address：": "",
                                "Corporate：": "",
                                "Scope：": "",
                                "Established：": "",
                                "authority：": ""}
                content = await page.content()
                if "No Data" in content :
                    pass
                elif "information" in content:
                    text_elements = await page.xpath('//div[@id="container"]/div')
                    for item in text_elements:
                        title_str = await (await item.getProperty('textContent')).jsonValue()
                        for text_i in company_dict:
                            if text_i in title_str:
                                data = title_str.split(text_i)[-1].strip()
                                data = data.replace(",","，")
                                company_dict[text_i] = data
                else:
                    print("{}爬取不对".format(shopid))
                print(company_dict)
            else:
                print("{}爬取不对".format(shopid))


# 获取登录后cookie
async def get_cookie(page):
    # res = await page.content()
    cookies_list = await page.cookies()
    cookies = ''
    for cookie in cookies_list:
        str_cookie = '{0}={1};'
        str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
        cookies += str_cookie
    print(cookies)
    return cookies

def get_path(distance):
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

def random_linspace(num, length):
    '''辅助函数
    传入要分成的几段 -> num ；长度 -> length, 生成一个递增的、随机的、不严格等差数列
    '''
    # 数列的起始值 、 结束值。 这里以平均值的 0.5 作为起始值，平均值的 1.5倍作为结束值。
    start, end = 0.5 * (length / num), 1.5 * (length / num)
    # 借助三方库生成一个标准的等差数列，主要是得出标准等差 space
    origin_list = numpy.linspace(start, end, num)
    space = origin_list[2] - origin_list[1]
    # 在标准等差的基础上，设置上下浮动的大小，（上下浮动10%）
    min_random, max_random = -(space / 10), space / 10
    result = []
    # 等差数列的初始值不变，就是我们设置的start
    value = start
    # 将等差数列添加到 list
    result.append(value)
    # 初始值已经添加，循环的次数 减一
    for i in range(num - 1):
        # 浮动的等差值 space
        random_space = space + random.uniform(min_random, max_random)
        value += random_space
        result.append(value)
    return result

def slide_list(total_length):
    '''等差数列生成器，根据传入的长度，生成一个随机的，先递增后递减，不严格的等差数列'''
    # 具体分成几段是随机的
    total_num = random.randint(10, 15)
    # 中间的拐点是随机的
    mid = total_num - random.randint(3, 5)
    # 第一段、第二段的分段数
    first_num, second_num = mid, total_num - mid
    # 第一段、第二段的长度，根据总长度，按比例分成
    first_length, second_length = total_length * (first_num / total_num), total_length * (second_num / total_num)
    # 调用上面的辅助函数，生成两个随机等差数列
    first_result = random_linspace(first_num, first_length)
    second_result = random_linspace(second_num, second_length)
    # 第二段等差数列进行逆序排序
    slide_result = first_result + second_result[::-1]
    # 由于随机性，判断一下总长度是否满足，不满足的再补上一段
    if sum(slide_result) < total_length:
        slide_result.append(total_length - sum(slide_result))
    return slide_result


def retry_if_result_none(result):
    return result is None


@retry(retry_on_result=retry_if_result_none, )
async def mouse_slide(page=None):
    await asyncio.sleep(1)
    try:
        # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
        await page.hover('#nc_1_n1z')  # 不同场景的验证码模块能名字不同。
        await page.mouse.down()
        # for x in get_path(5)
        a = page.mouse._x
        for i in slide_list(500):
            a += i
            await page.mouse.move(a, 0, )
        await page.mouse.up()
    except Exception as e:
        print(e, ':验证失败')
        return None, page
    else:
        await asyncio.sleep(1)
        return 1, page


def input_time_random():
    return random.randint(100, 151)


if __name__ == '__main__':
    username = 'bb1234567@qq.com'  # 淘宝用户名
    pwd = 'a123456789'  # 密码
    url = 'https://login.aliexpress.com/'
    loop = asyncio.get_event_loop()  # 协程，开启个无限循环的程序流程，把一些函数注册到事件循环上。当满足事件发生的时候，调用相应的协程函数。
    loop.run_until_complete(main(username, pwd, url))
