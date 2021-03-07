import requests
from multiprocessing import Pool
from requests.exceptions import RequestException
import re
import json

headers = {
	'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

def get_one_page(url):
	try:
		response = requests.get(url,headers = headers)
		if response.status_code == 200:
			return response.text
		return None
	except RequestException:
		print ('请求页出错',url)
		return None

def parse_one_page(html):
	partern = re.compile('<i.*?board-index.*?>(\\d+)</i>[\\s\\S]*?data-src="(.*?)"[\\s\\S]*?name.*?title="(.*?)"[\\s\\S]*?"star"[\\s\\S]*?主演：([\\s\\S]*?)</p>[\\s\\S]*?上映时间：(.*?)</p>[\\s\\S]*?integer">(.*?)</i>.*?fraction">(.*?)</i>[\\s\\S]*?</dd>')
	items = re.findall(partern,html)
	for item in items:
		yield {
			'index':item[0],
			'image':item[1],
			'title':item[2],
			'actor':item[3],
			'time':item[4],
			'score':item[5]+item[6]
			}

def write_to_file(content):
	with open('result.txt','a') as f:
		f.write(json.dumps(content)+'\n')
		f.close()

def main(offset):
	url = 'http://maoyan.com/board/4?offset=' +str(offset)
	html = get_one_page(url)
	for item in parse_one_page(html):
		write_to_file(item)
	print(url)

if __name__ == '__main__':
	pool = Pool()
	pool.map(main,[x*10 for x in range(10)])
