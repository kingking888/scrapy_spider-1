import asyncio
import requests
async def main(name):
    await asyncio.sleep(1)
    print("好的{}".format(name))
async def shuchu(add):
    req =requests.get("https://www.baidu.com")
    print(req.status_code)
    await asyncio.sleep(1)
    print("shide".format(add))
def yance():
    requests.get("http://www.baidu.com")
    yield "name"
def jieguo():
    print("shuchujieguo")
    yield from yance()


loop = asyncio.get_event_loop()
tasks = [shuchu("xihu")]

loop.run_until_complete(asyncio.wait(tasks))



