import datetime, redis, time


class test():
    def __init__(self):
        self.r = redis.Redis(host='192.168.0.230', port=6379, db=0, decode_responses=True)
        self.ago_data_count = self.r.scard('smt_pzinfo')

    def count(self, start_time):
        data_count = self.r.scard('smt_pzinfo')
        end_time = datetime.datetime.now() - start_time
        already_over = self.ago_data_count - data_count
        print('总用时：{}，10分钟已采集：{}，当前剩余数量：{}'.format(end_time, already_over, data_count))
        self.ago_data_count = data_count

    def run(self):
        start_time = datetime.datetime.now()

        while True:
            self.count(start_time)
            time.sleep(600)


run = test()
run.run()
