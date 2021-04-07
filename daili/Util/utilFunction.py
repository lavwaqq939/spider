#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-08-15 22:37:14
# @Author  : 金建峰 (jinjianfeng_@139.com)
# @Link    : http://www.cnblogs.com/xingyunsyc/
# @Version : $Id$

import sys
import requests
import time
from lxml import etree

sys.path.append('../')
#from Util.LogHandler import LogHandler
from Util.WebRequest import WebRequest

def getHtmlTree(url, **kwargs):
	"""
	获取html树
	:param url:
	:param kwargs:
	:return:
	"""

	header = {'Connection': 'keep-alive',
              'Cache-Control': 'max-age=0',
              'Upgrade-Insecure-Requests': '1',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate, sdch',
              'Accept-Language': 'zh-CN,zh;q=0.8',
              }

    # TODO 取代理服务器用代理服务器访问
    wr = WebRequest()

    time.sleep(2)

    html = wr.get(url=url, header=header).content
    return etree.HTML(html)
