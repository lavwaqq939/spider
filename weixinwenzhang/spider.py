#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-08-19
# @Author  : ${author} (${email})
# @Link    : ${link}
# @Version : $Id$

import requests
from urllib.parse import urlencode

base_url = 'http://weixin.sogou.com/weixin?'

def get_index(keyword,page):
	data = {
		'query': keyword,
		'type': 2,
		'page': page
	}
	url = base_url + urlencode(data)
	print(url)

if __name__ == '__main__':
	get_index('风景',1)
