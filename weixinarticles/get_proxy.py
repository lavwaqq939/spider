#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-08-19 10:25:06
# @Author  : 金建峰 (jinjianfeng_@139.com)
# @Link    : http://www.cnblogs.com/xingyunsyc/
# @Version : $Id$

import os
import requests

proxy_url = 'http://47.106.9.8:5010/get'

def get_proxy():
	try:
		response = requests.get(proxy_url)
		if response.status_code == 200:
			print(response.text)
		else:
			print(None)
	except:
		print('Error')

if __name__ == '__main__':
	get_proxy()
