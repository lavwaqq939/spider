#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-08-15 21:44:27
# @Author  : 金建峰 (jinjianfeng_@139.com)
# @Link    : http://www.cnblogs.com/xingyunsyc/
# @Version : $Id$

import re
import sys
import requests

try:
	from importlib import reload # py3 实际不会使用，只是为了不显示语法错误
except:
	reload(sys)
	sys.setdefaultencoding('utf-8')

sys.path.append('..')

from Util.utilFunction import robustCrawl,getHtmlTree
from Util.WebRequest import WebRequest

requests.packages.urllib3.disable_warnings()

class GetFreeProxy(object):
	"""docstring for GetFreeProxy"""
	def __init__(self):
		pass

	@staticmethod
	def freeProxyFirst(page_count=2):
		"""
		西刺代理 http://www.xicidaili.com
		:return:
		"""
		url_list = [
			'http://www.xicidaili.com/nn/', # 高匿
			'http://www.xicidaili.com/nt/', # 透明
		]
		for each_url in url_list:
			for i in range(1,page_count + 1):
				page_url = each_url + str(i)
				tree = getHtmlTree(page_url)
				proxy_list = tree.xpath('.//table[@id="ip_list"]//tr[position()>1]')
				for proxy in proxy_list:
					try:
						yield ':'.join(proxy.xpath('./td/text()')[0:2])
					except Exception as e:
						pass
