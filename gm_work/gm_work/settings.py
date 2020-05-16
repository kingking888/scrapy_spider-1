# -*- coding: utf-8 -*-

# Scrapy settings for gm_work project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time

BOT_NAME = 'gm_work'

SPIDER_MODULES = ['gm_work.spiders']
NEWSPIDER_MODULE = 'gm_work.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'gm_work (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4 #并发

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 0.5#下载延迟三秒
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

REDIRECT_MAX_TIMES = 10

# REDIRECT_ENALBED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "zh-CN,zh;q=0.9",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
# }

# ----------- selenium参数配置 -------------
SELENIUM_TIMEOUT = 25           # selenium浏览器的超时时间，单位秒
#LOAD_IMAGE = True               # 是否下载图片
WINDOW_HEIGHT = 900             # 浏览器窗口大小
WINDOW_WIDTH = 900

# Enable or disable spider middlewares爬虫中间件
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'gm_work.middlewares.AntAppSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares下载中间件
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
MY_USER_AGENT = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
]
DOWNLOADER_MIDDLEWARES = {
#   'gm_work.middlewares.AntAppDownloaderMiddleware': 543,
#   'gm_work.middlewares.RandomUserAgentMiddleware':543,
#   'gm_work.middlewares.ProxyDownloaderMiddleware': 400
#   'gm_work.middlewares.SeleniumMiddleware': 10
#   'gm_work.middlewares.HostDownloaderMiddleware': 30,
#     'gm_work.middlewares.SmtPrameDownloaderMiddleware': 21,
#   'gm_work.middlewares.IpChangeDownloaderMiddleware': 20,
    'gm_work.middlewares.ProcessAllExceptionMiddleware': 20,
    # 'gm_work.middlewares.TaobaoZhiboDownloaderMiddleware': 22,
    # 'gm_work.middlewares.UpdatetimeMiddleware': 23,

}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   # 'scrapy.extensions.telnet.TelnetConsole': None,
   #  'gm_work.extension.redisSpiderSmartIdleCloseExensions': 500,##自动关闭
   #   'gm_work.extension.Spider1OpenCloseLogging': 500,##添加starturl
    #   'gm_work.extension.SpiderOpenCloseLogging': 500,##request队列
}
# 'gm_work.middlewares.HostDownloaderMiddleware': 500,

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {#从低到高
    'gm_work.pipelines.CodeWriterPipeline': 290,
    'gm_work.pipelines.JsonWriterPipeline': 300,
    'gm_work.pipelines.errorWriterPipeline': 310,
   #   'gm_work.pipelines.MysqlPipeline': 300,
   #  'scrapy_redis.pipelines.RedisPipeline': 290
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []#这么http状态码不响应
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

RETRY_ENABLED = True#重试
RETRY_TIMES = 3
#RETRY_HTTP_CODES=#遇到什么网络状态码进行重试默认[500, 502, 503, 504, 522, 524, 408]
HTTPERROR_ALLOWED_CODES=[301,302,307,403,404,408,429,500, 502, 503, 504, 522, 524] #允许在此列表中的非200状态代码响应
REDIRECT_ENABLED = False##重定向



#DOWNLOAD_TIMEOUT超时等待时间
#DOWNLOAD_MAXSIZE下载最大相应大小
#DOWNLOAD_WARNSIZE下载警告大小

#log日志记录
LOG_LEVEL = "INFO"
to_day = time.localtime()
log_file_path = 'log/scrapy_{}_{}_{}.log'.format(to_day.tm_year, to_day.tm_mon, to_day.tm_mday)#在spider添加spidername
#LOG_FILE = log_file_path


# COMMANDS_MODULE = "gm_work.commands"#将自定义命令加入到scrapy中
#SPIDER_LOADER_CLASS = ""#这个？


#reids
#指定使用scrapy-redis的调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"#指定使用scrapy-redis的去重
# 指定排序爬取地址时使用的队列，
# 默认的 按优先级排序(Scrapy默认)，由sorted set实现的一种非FIFO、LIFO方式。
#广度优先:"scrapy_redis.queue.FifoQueue  深度优先:"SpiderPriorityQueue LifoQueue  优先： PriorityQueue
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
REDIS_START_URLS_AS_SET = True
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PARAMS = {'password': 'nriat.123456',}
SCHEDULER_PERSIST = True# 是否在关闭时候保留原来的调度器和去重记录，True=保留，False=清空

# 密码登陆
# REDIS_URL="redis://[user]:password@localhost:port"

#连接MYSQL数据库
MYSQL_HOST = '192.168.0.227'
MYSQL_PORT = 3306
MYSQL_DBNAME = 'ec_cross_border'
MYSQL_USER = 'dev'
MYSQL_PASSWD = 'Data227or8Dev715#'

#爬行顺序
# DEPTH_PRIORITY = 1#正数以广度优先，加后面两个设置彻底以广度优先
# SCHEDULER_DISK_QUEUE  =  'scrapy.squeues.PickleFifoDiskQueue'
# SCHEDULER_MEMORY_QUEUE  =  'scrapy.squeues.FifoMemoryQueue'

#extend相关的东西
MYEXT_ENABLED=True      # 开启redis结束的扩展
IDLE_NUMBER=60          # 配置空闲持续时间单位为 360个 ，一个时间单位为5s

#pipeline
SAVE_PATH = r"D:\spider_data"
LIMIT_NUM_DATA = 10000
LIMIT_NUM_ERROR = 100000
LIMIT_NUM_CODE = 10000

#extension：
MYEXT_ITEMCOUNT = 1000#检查间隔
SEED_FILE_PATH = r"D:\spider_seed"
SPLIT_NUM = 10000
CHANGE_IP_NUM = 50