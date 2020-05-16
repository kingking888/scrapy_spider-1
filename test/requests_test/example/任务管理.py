import csv
from collections import defaultdict
import time
import heapq
import numpy
from collections import namedtuple

def raw_data():
    bingfa_dict = {}
    with open("D://data/seeds/spidertask_data.csv","r",encoding="gbk")as f1:
        dict_lichu = csv.DictReader(f1)
        for i in dict_lichu:
            bingfa_dict[i["任务名称"]] =i["并发"]

    with open("D://data/seeds/spidertask_output.csv","r",encoding="gbk")as f:
        data = csv.reader(f,delimiter=',')
        header = next(data)

        task_dict = defaultdict(list)

        for i in data:

            task_name = i[0]

            start_time = int(time.mktime(time.strptime(i[1],"%Y/%m/%d %H:%M:%S")))
            end_time = int(time.mktime(time.strptime(i[2],"%Y/%m/%d %H:%M:%S")))

            time_yunxin = end_time-start_time
            schedule_data = namedtuple("schedule",["start","end","concurrent"])#为这个任务中的基本数据
            task_dict[task_name].append(schedule_data(start_time,end_time,bingfa_dict.get(task_name,0)))#一个任务的多次调度数据
        return task_dict
def concurrent_time(timestamp,data):#根据时间点是否在单次调度的时间内返回并发数
    if timestamp >int(data.start) and timestamp < int(data.end):
        return int(data.concurrent)
    else:
        return 0
def timestamp_get(time_now = time.time()):
    year = str(time.gmtime(time_now).tm_year)
    mouth = str(time.gmtime(time_now).tm_mon)
    day = str(time.gmtime(time_now).tm_mday)
    hour = str(time.gmtime(time_now).tm_hour)
    timestamp = time.mktime(time.strptime("{}-{}-{} {}".format(year,mouth,day,hour),"%Y-%m-%d %H"))
    timestamp_list = []
    for i in range(24):
        timestamp_list.append(timestamp)
        timestamp -= 3600
    return timestamp_list
timestamp_iter = timestamp_get()

task_dict = raw_data()
totle_concurrent = 0
totle_concurrent_dict = defaultdict(int)
for i,y in task_dict.items():
    print(i)

    now_data = max(y,key=lambda x:x.end)
    three_last = heapq.nlargest(3,y,key=lambda x:x.end)
    mead_runtime = int(numpy.mean([i.end-i.start for i in three_last]))#取最近三次的平均时间
    concurrent_last = now_data.concurrent
    for j in y:
        print(j)
        print(1)
        for time_i in timestamp_iter:
            concurrent = concurrent_time(int(time_i),j)
            if concurrent != 0:
                print(concurrent)
            totle_concurrent_dict[time_i] += concurrent

print(totle_concurrent_dict)



