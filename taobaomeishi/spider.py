from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
import re
from mongo import connect_mongo
from config import MONGO_TABLE,KEYWORD
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

def search(KEYWORD):
	print('正在搜索')
	try:
		browser.get('https://www.taobao.com')
		input = wait.until(
	        EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
	    )
		sumbit = wait.until(
	        EC.element_to_be_clickable((By.CSS_SELECTOR,"#J_TSearchForm > div.search-button > button"))
	    )
		input.send_keys(KEYWORD)
		sumbit.click()
		total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.total")))
		get_products()
		return total.text
	except TimeoutException:
		return search(KEYWORD)

def next_page(page_number):
	print('正在翻页',page_number)
	try:
		input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#J_BottomSearchForm > button")))
		sumbit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
		input.clear()
		input.send_keys(page_number)
		sumbit.click()
		wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > ul > li.item.active > span"),str(page_number)))
		get_products()
	except TimeoutException:
		next_page(page_number)
	except Exception:
		print('可能是submit.click()执行过快')
		next_page(page_number)

def get_products():
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-itemlist .items .item")))
		html = browser.page_source
		doc = pq(html)
		items = doc("#mainsrp-itemlist .items .item").items()
		partern = re.compile('"(//g-search.*?webp)"')
		for item in items:
			content = item.find('.pic .img').attr('src')
			product = {
				'image':content,
				#'image':partern.search(str(content)).group(1),
				'price':item.find('.price').text()[2:],
				'deal':item.find('.deal-cnt').text()[:-3],
				'title':item.find('.title').text(),
				'shop':item.find('.shop').text(),
				'location':item.find('.location').text()
			}
			#save_to_mongo(product)
			print(product)

def save_to_mongo(product):
	db = connect_mongo()
	if db[MONGO_TABLE].insert(product):
		print('存储到MongoDB成功')
		return True
	return False

def main():
		total = search(KEYWORD)
		total = int(re.compile('(\\d+)').search(total).group(1))
		for x in range(2,total+1):
			next_page(x)
		browser.close()

if __name__ == '__main__':
	main()
