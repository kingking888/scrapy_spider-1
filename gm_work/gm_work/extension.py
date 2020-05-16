import logging
import time
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object
from gm_work.seed_split import file_split
import os
from pathlib import Path
import re
from scrapy_redis import connection ,defaults



logger = logging.getLogger(__name__)

class redisSpiderSmartIdleCloseExensions():
    def __init__(self,idler_number,crawler):
        self.crawler = crawler
        self.idle_number = idler_number
        self.idle_list = []
        self.idle_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        # 首先检查是否应该启用和提高扩展
        # 否则不配置

        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        if not 'redis_key' in crawler.spidercls.__dict__.keys():
            raise NotConfigured('Only supports RedisSpider')

        # 获取配置中的时间片个数，默认为360个，30分钟
        idle_number = crawler.settings.getint('IDLE_NUMBER', 360)

        # 实例化扩展对象
        ext = cls(idle_number, crawler)

        # 将扩展对象连接到信号， 将signals.spider_idle 与 spider_idle() 方法关联起来。
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)


        # return the extension object
        return ext

    def spider_opened(self, spider):
        logger.info("opened spider {} redis spider Idle, Continuous idle limit： {}".format(spider.name, self.idle_number) )

    def spider_closed(self, spider):
        logger.info("closed spider %s, idle count %d , Continuous idle count %d",
                    spider.name, self.idle_count, len(self.idle_list))

    def spider_idle(self, spider):    #改为判断是否有key
        self.idle_count += 1  # 空闲计数
        self.idle_list.append(time.time())  # 每次触发 spider_idle时，记录下触发时间戳
        idle_list_len = len(self.idle_list)  # 获取当前已经连续触发的次数

        # 判断 redis 中是否存在关键key, 如果key 被用完，则key就会不存在
        if idle_list_len > 2 and spider.server.exists(spider.redis_key):
        # 判断 当前触发时间与上次触发时间 之间的间隔是否大于5秒，如果大于5秒，说明redis 中还有key
        # if idle_list_len > 2 and self.idle_list[-1] - self.idle_list[-2] > 6:
            self.idle_list = [self.idle_list[-1]]

        elif idle_list_len > self.idle_number:
            # 连续触发的次数达到配置次数后关闭爬虫
            logger.info('\n continued idle number exceed {} Times'
                        '\n meet the idle shutdown conditions, will close the reptile operation'
                        '\n idle start time: {},  close spider time: {}'.format(self.idle_number,
                                                                                self.idle_list[0], self.idle_list[0]))
            # 执行关闭爬虫操作
            self.crawler.engine.close_spider(spider, 'closespider_pagecount')


class SpiderOpenCloseLogging(object):

    def __init__(self, request_count,scheduler):
        self.request_count = request_count
        self.request_num = 0
        self.scheduler = scheduler
        self.request = None
        self.no_meet = True#是否遇到seed请求
        self.path_base = r"D:\test_data\seed"


    @classmethod
    def from_crawler(cls, crawler,):
        # first check if the extension should be enabled and raise

        # NotConfigured otherwis
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured
        # get the number of items from settings

        request_count = crawler.settings.getint('MYEXT_ITEMCOUNT', 1000)

        # instantiate the extension object
        scheduler_cls = load_object(crawler.settings['SCHEDULER'])
        scheduler = scheduler_cls.from_crawler(crawler)
        ext = cls(request_count,scheduler)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.request_scheduled, signal=signals.request_scheduled)
        # return the extension object

        return ext

    def spider_opened(self, spider):
        self.scheduler.open(spider)#
        file = spider.name+".txt"
        split_t = file_split(file=file,path=r"D:\test_data\seed")
        split_t.change_num(10000)
        split_t.split()
        spider.log("opened spider %s" % spider.name)
        self.path = Path(self.path_base)/(spider.name+"_split")

    def spider_closed(self, spider):
        spider.log("closed spider %s" % spider.name)

    def request_scheduled(self, request, spider):
        self.request_num += 1
        if self.no_meet and request.meta.get("seed_reuqest"):
            self.request = request
            self.request.meta["try_num"] = 0#优化修改为删除try_num
            self.no_meet = False
        if self.request_num % self.request_count == 0:
            spider.log("scraped %d request" % self.request_num)
            #检查redis中
            update_state,file_name=self.check_seed(self.scheduler,self.path)
            if update_state:
                for i in self.get_request(self.request,file_name):
                    self.scheduler.enqueue_request(i)
                else:
                    print("更新一个种子队列到队列中")

    def check_seed(self,scheduler,path):#优化怎么检查的

        if len(scheduler.queue) < 100000:
            files = os.listdir(path)
            for i in files:
                if re.search("-\d+\.txt",i):
                    return True,i
            else:
                return False,""
        else:
            return False, ""

    def get_request(self,request,file_name):
        with open(self.path/file_name,"r",encoding="utf-8") as f:
            for i in f:
                url = i.strip()
                request._set_url = url
                yield request
        end_filename = file_name.replace(".txt","end.txt")
        os.rename(self.path/file_name,self.path/end_filename)

class Spider1OpenCloseLogging(object):#将url添加到startrequest中

    def __init__(self, settings):
        self.request_count = settings.getint('MYEXT_ITEMCOUNT', 1000)
        self.request_num = 0
        # self.scheduler = scheduler
        self.request = None
        self.no_meet = True#是否遇到seed请求
        self.path_base = settings.get("SEED_FILE_PATH")
        self.server = connection.from_settings(settings)
        use_set = settings.getbool('REDIS_START_URLS_AS_SET', defaults.START_URLS_AS_SET)
        request_set = settings.get("SCHEDULER_QUEUE_CLASS")
        self.fetch_one = self.server.spop if use_set else self.server.lpop
        self.add_one = self.server.sadd if use_set else self.server.lpush
        self.get_num = self.server.llen if "LifoQueue" in request_set or "FifoQueue" in request_set else self.server.zcard
        self.get_startnum = self.server.scard if use_set else self.server.llen
        self.split_num = settings.get("SPLIT_NUM")
        self.path_split = None


    @classmethod
    def from_crawler(cls, crawler,):
        # first check if the extension should be enabled and raise

        # NotConfigured otherwis

        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured
        # get the number of items from settings
        settings = crawler.settings
        # instantiate the extension object
        # SCHEDULER_SETTING = crawler.settings['SCHEDULER']
        # scheduler_cls = load_object(SCHEDULER_SETTING)
        # scheduler = scheduler_cls.from_crawler(crawler)
        # scheduler.queue_cls='%(spider)s:start_url'
        ext = cls(settings)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.request_scheduled, signal=signals.request_scheduled)
        # return the extension object

        return ext

    def spider_opened(self, spider):
        self.key_start = "{}:start_url".format(spider.name)
        self.key_request = "{}:requests".format(spider.name)
        # self.scheduler.open(spider)#
        spider.log("opened spider %s" % spider.name)
        file = spider.name+".txt"
        split_t = file_split(file=file,path=self.path_base)
        split_t.change_num(self.split_num)
        result = split_t.split()
        if result:
            spider.log("%s spider split success" % spider.name)
        else:
            raise("分割文本错误")
        self.path_split = Path(self.path_base)/(spider.name+"_split")
        update_state, file_name = self.check_seed(key_request=self.key_request, key_start=self.key_start,
                                                  path=self.path_split)
        if update_state:
            self.get_request(key=self.key_start, file_name=file_name)
        print(1)

    def spider_closed(self, spider):
        spider.log("closed spider %s" % spider.name)

    def request_scheduled(self, request, spider):
        self.request_num += 1
        # if self.no_meet and request.meta.get("deep") == 1:
        #     self.request = request
        #     self.request.meta["try_num"] = 0#优化修改为删除try_num
        #     self.no_meet = False
        if self.request_num % self.request_count == 0:
            # spider.log("scraped %d request" % self.request_num)
            #检查redis中
            update_state,file_name=self.check_seed(key_request=self.key_request,key_start=self.key_start,
                                                   path=self.path_split)
            if update_state:
                self.get_request(key=self.key_start,file_name=file_name)

    def check_seed(self,key_request,key_start,path):#优化怎么检查的
        if self.get_num(key_request) < self.split_num and self.get_startnum(key_start) < self.split_num*0.2:
            files = os.listdir(path)
            for i in files:
                if re.search("-\d+\.txt",i):
                    return True,i
            else:
                return False,""
        else:
            return False, ""

    def get_request(self,key,file_name):
        with open(self.path_split/file_name,"r",encoding="utf-8") as f:
            for i in f:
                url = i.strip()
                self.add_one(key,url)
            else:
                print("更新一个种子队列到队列中")
        end_filename = file_name.replace(".txt","end.txt")
        os.rename(self.path_split/file_name,self.path_split/end_filename)


class redis_oprating():
    pass