import redis
from scrapy_redis import picklecompat

serializer = picklecompat

rediscli = redis.StrictRedis(host='127.0.0.1', port=6379, password='imiss968', db=0)
# num = rediscli.zcard("amazon_ph:requests")
a = rediscli.lrange('amazon_ph:requests',0,-1)
with open(r"C:\Users\admin\Desktop\amazon_ph_seeds.txt","a+",encoding="utf-8") as f:
    for i in a:
        # rediscli.rpush("smt_goods:requeststest",i)
        obj = serializer.loads(i)
        url = obj.get("url")
        deep = obj.get("meta").get("deep")
        f.write(str(deep)+","+url+"\n")