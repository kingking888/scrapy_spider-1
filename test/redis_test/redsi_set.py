import redis
r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True,password="nriat.123456")
data = r.smembers("taobao_userid")
file = open("taobao_id.txt","w",encoding="utf-8")
for i in data:
    file.write(i+"\n")