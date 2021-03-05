#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-07-17 11:50:26
# @Author  : 金建峰 (jinjianfeng_@139.com)
# @Link    : http://www.cnblogs.com/yingyunsyc/
# @Version : $Id$

import os
import re
import json
import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from config import *
from sshtunnel import SSHTunnelForwarder
import pymongo
from hashlib import md5
from multiprocessing import Pool

headers = {
'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

def get_index_page(offset,keyword):
	data = {
	'offset': offset,
    'format': 'json',
    'keyword': keyword,
    'autoload': 'true',
    'count': 20,
    'cur_tab': 1,
    'from': 'search_tab'
	}
	url = 'https://www.toutiao.com/search_content/?'+urlencode(data)
	try:
		response = requests.get(url)
		if response.status_code == 200:
			return response.text
		return None
	except RequestException:
		print('求情索引页出错')
		return None

def parse_page_index(html):
	data = json.loads(html)
	if data and 'data' in data.keys():
		for item in data.get('data'):
			yield item.get('article_url')

def get_page_detail(url):
	try:
		response = requests.get(url,headers=headers)
		if response.status_code == 200:
			return response.text
		return None
	except RequestException:
		print('请求详情页出错',url)
		return None

def parse_page_detail(html,url):
	soup = BeautifulSoup(html,'lxml')
	title = soup.select('title')[0].get_text()
	images_parttern =re.compile('gallery:.*?({.*?]})')
	result = re.search(images_parttern,html)
	jsonstr = result.group(1).replace('\\\/','/').replace('\\\\','\\').replace('\\"','"')
	if jsonstr:
	#	http_parttern = re.compile('count":.*?(http://.*?)",".*?url_list')
	#	images = re.search(http_parttern,jsonstr)
		data = json.loads(jsonstr)
		if data and 'sub_images' in data.keys():
			sub_images = data.get('sub_images')
			images = [item.get('url') for item in sub_images]
			for image in images:	download_image(image)
			return {
				'title':title,
				'url':url,
				'images':images
			}

def connect_to_mongo(SSH_IP,SSH_PORT,SSH_USER,SSH_PASSWORD,MONGO_IP,MONGO_PORT,MONGO_DB,MONGO_TABLE):
	server = SSHTunnelForwarder((SSH_IP,SSH_PORT),ssh_username = SSH_USER,
		ssh_password = SSH_PASSWORD,remote_bind_address = (MONGO_IP,MONGO_PORT),
		local_bind_address=('0.0.0.0', 27017))
	server.start()
	client = pymongo.MongoClient(host = MONGO_IP)
	db = client[MONGO_DB]
	return db

def save_to_mongo(result,db):
	if db[MONGO_TABLE].insert(result):
		return True
	return False

def download_image(url):
	print('正在下载',url)
	try:
		response = requests.get(url)
		if response.status_code == 200:
			save_image(response.content)
		return None
	except RequestException:
		print('请求图片页出错',url)
		return None

def save_image(content):
	file_path = '{0}/{1}.{2}'.format(SAVE_FILE_PATH,md5(content).hexdigest(),'jpg')
	if not os.path.exists(file_path):
		with open(file_path,'wb') as f:
			f.write(content)
			f.close()

def main(offset):
	html = get_index_page(offset,KEYWORD)
	for url in parse_page_index(html):
		if url is not None:
			html = get_page_detail(url)
			result = parse_page_detail(html,url)
			db = connect_to_mongo(SSH_IP,SSH_PORT,SSH_USER,SSH_PASSWORD,
				MONGO_IP,MONGO_PORT,MONGO_DB,MONGO_TABLE)
			save_to_mongo(result,db)

if __name__ == '__main__':
	groups = [x*20 for x in range(GROUP_START,GROUP_END+1)]
	pool = Pool()
	pool.map(main,groups)
