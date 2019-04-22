#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author :wulicaicai
# IDE  : PyCharm
import time
from scrapy import cmdline

# cmdline.execute('scrapy crawl souq'.split())  # 爬取saudi url

# time.sleep(20)
# cmdline.execute('scrapy crawl souq_uae'.split())  # 爬取 uae url

# cmdline.execute('scrapy crawl souq_product'.split())  # 爬取  saudi  产品信息

cmdline.execute('scrapy crawl souq_product_uae'.split())  # 爬取  uae  产品信息

# ''' 保存csv文件 '''
# cmdline.execute('scrapy crawl souq -o souq.csv'.split())

# ''' 保存json文件 '''
# cmdline.execute('scrapy crawl souq -o souq.json'.split())
