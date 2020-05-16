import redis, pymysql, datetime, re, os
from tqdm import tqdm


class CreateTask(object):
    def __init__(self):
        # 任务存放处
        self.r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True,password="nriat.123456")
        self.r1 = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True,password="nriat.123456")
        self.connect = pymysql.connect(host='192.168.0.227', port=3306, database='ec_cross_border', user='dev',
                                       password='Data227or8Dev715#',
                                       charset='utf8', use_unicode=True)
        self.cursor = self.connect.cursor()
        all_task_name = self.r.keys()
        for i in all_task_name:
            TaskName = re.match('smt_pzinfo', i)
            cache_queue = re.match('smt_pzinfo_cache_queque', i)
            if TaskName != None:
                self.r.delete(i)
            if cache_queue != None:
                self.r.delete(i)
        self.r1.delete('SmtPzInfoSpider')

    def get_shop_id(self, table):
        self.cursor.execute("""SELECT  shop_id from {} GROUP BY shop_id""".format(table))
        all_data = self.cursor.fetchall()
        self.connect.commit()
        return all_data

    # def get_shop_id_txt(self):
    #     with open('X:/数据库/速卖通/{3_0_1速卖通_有销量无地址}[店铺id].txt','r',encoding='utf-8') as f:
    #         data=f.readlines()

    def check_table(self):
        self.count = self.cursor.execute("""show tables""")
        all_shopinfo = self.cursor.fetchall()
        self.connect.commit()
        all_shopinfo_list = []
        for i in all_shopinfo:
            all_shopinfo_list.append(i[0])
        return all_shopinfo_list

    def run(self, table):
        all_table = self.check_table()
        if table in all_table:
            start_time = datetime.datetime.now()
            shop_id_list = self.get_shop_id(table)
            end_time = datetime.datetime.now() - start_time
            print('查询所有公司名称所用时间：{}'.format(end_time))
            for i in tqdm(shop_id_list):
                shop_id = i[0].replace('\n', '')
                # 将参数存入对应列表
                self.r.sadd('smt_pzinfo', shop_id)
            task_num = self.r.scard('smt_pzinfo')
            with open('F:/pycharmproject/scrapy/smt_spider/任务文件/当前参数数量.txt', 'w', encoding='utf-8') as f:
                f.write(str(task_num))
            print('速卖通-任务生成完毕,参数总量为:{}'.format(task_num))
        else:
            print("'{}'表不存在，请确认表名后重新运行程序".format(table))

if __name__ == '__main__':
    save_table_path = 'F:/pycharmproject/scrapy/smt_spider/任务文件/'
    with open(save_table_path + '提取数据的表名称.txt', 'r', encoding='utf-8') as f:
        table = f.read().strip()
    get = CreateTask()
    get.run(table)
