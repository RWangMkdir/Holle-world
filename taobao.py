# 流程框架：
# 	一、搜索关键字
# 	二、分析页码并翻页
# 	三、分析提取商品内容
# 	四、存储至MongoDB
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from pyquery import PyQuery as pq
from pymongo import MongoClient
import json

client = MongoClient('localhost',27017)
db = client['taobaokouhong']



browser = webdriver.Chrome() 
wait = WebDriverWait(browser,10)
def search():
	try:
		browser.get('https://www.taobao.com')
		input = wait.until(
			EC.presence_of_element_located((By.CSS_SELECTOR,'#q'))
			).send_keys('手机')
		# element.send_keys('美食')
		submit = wait.until(
			EC.element_to_be_clickable((By.CSS_SELECTOR,'#J_TSearchForm > div.search-button > button'))
			).click()
		total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#spulist-pager > div > div > div > div.total')))
		get_products()
		return total.text
		
		# submit.click()
		# browser.save_screenshot('taobao.png')
	except TimeoutException:
		return search()
def next_page(page_number):
	try:
		input = wait.until(
				EC.presence_of_element_located((By.CSS_SELECTOR,'#spulist-pager > div > div > div > div.form > input'))
				)
		submit = wait.until(
				EC.element_to_be_clickable((By.CSS_SELECTOR,'#spulist-pager > div > div > div > div.form > span.btn.J_Submit'))
				)
		input.clear()
		input.send_keys(page_number)
		submit.click()
		wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#spulist-pager > div > div > div > ul > li.item.active > span'),str(page_number)))
		get_products()
	except TimeoutException:
		next_page(page_number)

def get_products():
	wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#spulist-grid .m-grid')))
	html = browser.page_source
	# print(html)
	doc = pq(html)
	items = doc('#spulist-grid .m-grid')#.items()
	print(items)
	# for item in items:
	# 	product = {
	# 		# 'image': item.find('.pic .img').attr('src'),
	# 		'price': item.find('.price').text(),
	# 		'deal': item.find('.deal-cnt').text()[:-3],
	# 		'title': item.find('.title').text(),
	# 		'shop': item.find('.shop').text(),
	# 		'location': item.find('.location').text(),
	# 	}

	# 	print(product)
		# save_mongo(product)

def save_mongo(result):
	json_str = json.dumps(result)  
	product_info = open("taobao_phone_info.json", "a")
	product_info.write(json_str)
	product_info.close()
	try:
		if db['taobaophone'].insert(result):
			print('存储到MongoDB成功',result)
			
	except Exception:
		print('存储到MongoDB失败',result)

def main():

	total = search()
	total = int(re.compile('(\d+)').search(total).group(1))
	for i in range(2,total + 1):
		next_page(i)

	browser.close()




if __name__ == '__main__':
	main()
	
