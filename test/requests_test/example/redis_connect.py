import redis

# 将start_url 存储到redis中的redis_key中，让爬虫去爬取
redis_Host = "192.168.9.83"
redis_key = "smt:start_url"

# 创建redis数据库连接
rediscli = redis.Redis(host = redis_Host, port = 6379, db = "0",password="nriat.123456")
rediscli.lpush(redis_key, "https://www.baidu.com")
print(1)
