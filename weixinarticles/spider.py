#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-08-18 20:22:31
# @Author  : 金建峰 (jinjianfeng_@139.com)
# @Link    : http://www.cnblogs.com/xingyunsyc/
# @Version : $Id$

from urllib.parse import urlencode
import requests
from requests.exceptions import Timeout, ConnectionError
from pyquery import PyQuery as pq
import sys

sys.path.append('..')
from conmongodb.config import *
from conmongodb.mongo import connect_mongo

base_url = 'http://weixin.sogou.com/weixin?'

headers = {
	'Cookie': 'SUV=00C147B0D38A14AA5A7BA466338EF310; CXID=B340920A1DD22385DE5654CD6A4EC6FA; SUID=AA148AD33765860A5AA2998200019D98; SMYUV=1523600682424620; UM_distinctid=162bdad71b67-0689dae5d15ec6-4446062d-100200-162bdad71b727d; usid=VMfvH3vS-dkemDCH; GOTO=; ad=Gyllllllll2btHYPlllllVHhCAGlllll1coUIyllllwlllllROxlw@@@@@@@@@@@; ABTEST=0|1534595141|v1; weixinIndexVisited=1; SUIR=AE1F81DF0C0978BFCD47338A0C761C0B; ppinf=5|1534598191|1535807791|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyNzolRTklODclOTElRTUlQkIlQkElRTUlQjMlQjB8Y3J0OjEwOjE1MzQ1OTgxOTF8cmVmbmljazoyNzolRTklODclOTElRTUlQkIlQkElRTUlQjMlQjB8dXNlcmlkOjQ0Om85dDJsdUJySTAxeERibk1UMWFSRU1uQmFFU2tAd2VpeGluLnNvaHUuY29tfA; pprdig=AAKwP6jnDlVmdWQwjhGTVLfpUJI2eKBG8yh5AW8Q9JgAfCyhj99Hsy9cq7P6uVUmCAtUjb82-bMZby9adv8aDfTCbnF11eR7UjTzUEd3FKhLeluxBrh4PyYIiko6Q2C9PbIx-fd1HsI9T1GlLuAXS0mRgfBmp4YrzNcobtpVP1M; sgid=17-35076907-AVt4HC9zQVmAXXa7ibcpDUxg; IPLOC=CN4101; sct=9; ld=vyllllllll2bSrs1lllllVHfAMclllll1coUIyllllwlllllVllll5@@@@@@@@@@; LSTMV=347%2C321; LCLKINT=2811; JSESSIONID=aaaVQtkczoTgW52LbIBvw; PHPSESSID=qa84lkeg5qkt6uruu75ofoc062; ppmdig=1535188441000000318f555bf3b0449e3f95238c97e122b9; session_id_crm-bo=crm-bo_b446d87b-67cb-45ee-a804-2a9a0bea01e8; SNUID=61D14E16C4C1B1FAA7BE8D87C52553DE; seccodeRight=success; successCount=1|Sat, 25 Aug 2018 09:53:02 GMT',
	'Host': 'weixin.sogou.com',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

keyword = '风景'

proxy_pool_url = 'http://47.106.9.8:5010/get'

proxy = None

max_count = 2

def get_proxy():
	try:
		response = requests.get(proxy_pool_url)
		if response.status_code == 200:
			return response.text
		return None
	except ConnectionError:
		return None

def get_html(url,count = 1):
	print('Crawling',url)
	print('Tring Count',count)
	global proxy
	if count >= max_count:
		print('Tried Too Many Counts')
		return None
	try:
		if proxy:
			proxies = {
				'http':'http://' +proxy
			}
			response = requests.get(url,allow_redirects = False,headers = headers,proxies = proxies,timeout = 3)
		else:
			response = requests.get(url,allow_redirects = False,headers = headers)
		if response.status_code == 200:
			return response.text
		if response.status_code == 302:
			proxy = get_proxy()
			if proxy:
				print('Using Proxy',proxy)
				return get_html(url)
			else:
				print('Get Proxy Failed')
				return None
	except (ConnectionError, Timeout):
		print('Error Occurred',count)
		proxy = get_proxy()
		count += 1
		return get_html(url,count)

def get_index(keyword,page):
	data={
		'query': keyword,
		'type': 2,
		'page': page
	}
	queries = urlencode(data)
	url = base_url + queries
	html = get_html(url)
	return html

def parse_index(html):
	doc = pq(html)
	items = doc('.news-box .news-list li .txt-box h3 a').items()
	for item in items:
		yield item.attr('href')

def get_detail(url):
	try:
		response = requests.get(url)
		if response.status_code == 200 :
			return response.text
		return None
	except ConnectionError:
		return None

def parse_detail(html):
	doc = pq(html)
	title = doc('#activity-name').text()
	content = doc('#js_content').text()
	date = doc('#publish_time').text()
	nickname = doc('#js_name').text()
	wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()

	return {
	'title':title,
	'content':content,
	'date':date,
	'nickname':nickname,
	'wechat':wechat
	}

def save_to_mongo():
	db = connect_mongo()
	if db[MONGO_TABLE]:
		print('连接到MongoDB成功')
		return db[MONGO_TABLE]
	return None

def main():
	try:
		table = save_to_mongo()
		article = []
		for page in range(1,101):
			html = get_index(keyword,page)
			if html:
				article_urls = parse_index(html)
				for article_url in article_urls:
					article_html = get_detail(article_url)
					if article_html:
						dict_title = parse_detail(article_html)
						article.append(dict_title)
		print('开始存储到MongoDB数据库')
		table.insert(article)
		print('存储到MongoDB成功')
	except Exception as e:
		raise e
	finally:
		exit()


if __name__ == '__main__':
	main()
