# config.py
# MediaCrawler 配置文件
# 可以通过GUI修改这些设置

# ============ 基本配置 ============
# 目标平台：xhs（小红书）、dy（抖音）、ks（快手）、bili（B站）、wb（微博）、tieba（贴吧）、zhihu（知乎）
PLATFORM = 'xhs'

# 数据存储方式：json、excel、csv、db、sqlite
SAVE_DATA_OPTION = 'csv'

# ============ 搜索关键词配置 ============
# 关键词列表（GUI会修改这里）
KEYWORDS = ['高铁司机']

# 搜索类型（根据平台不同可能的值）
SEARCH_TYPE = 'video'  # 可以是：video, post, article, all 等

# 搜索模式
SEARCH_MODE = 'keyword'  # keyword, user, hashtag, etc.

# ============ CSV导出设置 ============
CSV_FILENAME_PREFIX = 'crawler_data'
CSV_ENCODING = 'utf-8'
CSV_INCLUDE_HEADER = True
CSV_OUTPUT_DIR = 'output'

# ============ 爬取限制配置 ============
MAX_CRAWL_COUNT = 100# 最大爬取数量
CRAWL_PAGES = 10# 爬取页数
REQUEST_DELAY = 1.0# 请求延迟（秒）
ENABLE_GET_WORDCLOUD = False  # 是否生成词云

# ============ 数据库配置 ============
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4'
}

SQLITE_CONFIG = {
    'db_path': 'media_crawler.db'
}

# ============ 代理设置 ============
PROXY = None
# PROXY = "http://127.0.0.1:10809"

# ============ 浏览器设置 ============
HEADLESS = False   # 是否使用无头模式
SLOW_MOTION = 0    # 操作延迟（毫秒）
TIMEOUT = 30       # 超时时间（秒）

# ============ 平台特定配置 ============
# 小红书配置
XHS_CONFIG = {
    "search_tab": "综合",
    "sort_type": "general"
}

# 抖音配置
DY_CONFIG = {
    "search_tab": "视频",
    "sort_type": "0"
}

# B站配置
BILI_CONFIG = {
    "search_type": "video",
    "order": "totalrank"
}

# 微博配置
WB_CONFIG = {
    "type": "all"
}
