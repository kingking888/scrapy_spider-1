import asyncio
import pyppeteer
from urllib import parse

async def main(name,**kwargs):
    browser = await pyppeteer.launch({"headless":False})
    page = await browser.newPage()
    #page1 = await browser.newPage()
    await page.setViewport({"width":1920,"height":1080,"deviceScaleFactor ":"0"})
    browdict = kwargs
    await page.setJavaScriptEnabled(enabled=True)

    if browdict.get("url"):
        url = browdict.get("url")
        await page.goto(browdict["url"])
        if "sj.qq.com/myapp/detail.htm" in url:
            #await page.click("a#J_DetIntroShowMore")
            await asyncio.sleep(2)
        await page.evaluate("() => window.scrollTo(-50,300)")
        await asyncio.sleep(2)

        await page.evaluate("() => window.scrollTo(-300,600)")

        cookies = await page.cookies()
        print(cookies)
        png_name = parse.urlparse(url)
        await page.screenshot({'path': '{}.png'.format(png_name.netloc),"fullPage":True})
    try:
        await page.goto("https://translate.google.cn/#view=home&op=translate&sl=en&tl=zh-CN&text=frame")
        await page.screenshot({'path': '{}.png'.format("https://translate.google.cn"),"fullPage":True})
    except:
        print("未加载完全")
    await page.waitFor(10)
    await browser.close()

task=[main("task2",url="https://sj.qq.com/myapp/detail.htm?apkName=com.eg.android.AlipayGphone")]#main("task1",url="https://www.baidu.com"),

asyncio.get_event_loop().run_until_complete(asyncio.wait(task))