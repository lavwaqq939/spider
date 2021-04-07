#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-08-18 20:22:31
# @Author  : 金建峰 (jinjianfeng_@139.com)
# @Link    : http://www.cnblogs.com/xingyunsyc/
# @Version : $Id$

from urllib.parse import urlencode
import requests
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq

base_url = 'http://weixin.sogou.com/weixin?'

headers = {
	'Cookie': 'SUV=00C147B0D38A14AA5A7BA466338EF310; CXID=B340920A1DD22385DE5654CD6A4EC6FA; SUID=AA148AD33765860A5AA2998200019D98; SMYUV=1523600682424620; UM_distinctid=162bdad71b67-0689dae5d15ec6-4446062d-100200-162bdad71b727d; usid=VMfvH3vS-dkemDCH; GOTO=; ld=QZllllllll2bSrs1lllllVHr6h6lllll1coUIyllll9llllljylll5@@@@@@@@@@; LSTMV=251%2C366; LCLKINT=3571; ad=Gyllllllll2btHYPlllllVHhCAGlllll1coUIyllllwlllllROxlw@@@@@@@@@@@; ABTEST=0|1534595141|v1; weixinIndexVisited=1; JSESSIONID=aaaAlaV7utVkI8pytDcvw; PHPSESSID=kcv1jvctfpf1p19kiadm72bit0; SUIR=AE1F81DF0C0978BFCD47338A0C761C0B; ppinf=5|1534598191|1535807791|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyNzolRTklODclOTElRTUlQkIlQkElRTUlQjMlQjB8Y3J0OjEwOjE1MzQ1OTgxOTF8cmVmbmljazoyNzolRTklODclOTElRTUlQkIlQkElRTUlQjMlQjB8dXNlcmlkOjQ0Om85dDJsdUJySTAxeERibk1UMWFSRU1uQmFFU2tAd2VpeGluLnNvaHUuY29tfA; pprdig=AAKwP6jnDlVmdWQwjhGTVLfpUJI2eKBG8yh5AW8Q9JgAfCyhj99Hsy9cq7P6uVUmCAtUjb82-bMZby9adv8aDfTCbnF11eR7UjTzUEd3FKhLeluxBrh4PyYIiko6Q2C9PbIx-fd1HsI9T1GlLuAXS0mRgfBmp4YrzNcobtpVP1M; sgid=17-35076907-AVt4HC9zQVmAXXa7ibcpDUxg; ppmdig=153459819100000060a808e70cc73ebcb5f5ea56b0a801e8; IPLOC=CN4101; sct=6; SNUID=C177EEB7646610D6C19426006455B88D; seccodeRight=success; successCount=1|Sat, 18 Aug 2018 13:32:17 GMT; refresh=1',
	'Host': 'weixin.sogou.com',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

keyword = '风景'

proxy_pool_url = 'http://47.106.9.8:5010/get'

proxy = None

max_count = 5

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
			response = requests.get(url,allow_redirects = False,headers = headers,proxies = proxies)
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
	except ConnectionError:
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
		if response.status_code == 200:
			return response.text
		return None
	except ConnectionError:
		return None

def parse_detail(html):
	doc = pq(html)
	title = doc('#activity-name').text()
	content = doc('#js_content').text()
	date = doc('#publish_time').text()

	return {
	'title':title,
	'content':content,
	'date':date
	}

def main():
	for page in range(11,12):
		html = get_index(keyword,page)
		article_urls = parse_index(html)
		for article_url in article_urls:
			print(article_url)
			doc = get_detail(article_url)
			dict_title = parse_detail(doc)
			print(dict_title)

if __name__ == '__main__':
	main()
