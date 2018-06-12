import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
import re
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
import os
from hashlib import md5
from multiprocessing import Pool
client = MongoClient('localhost',27017)
db = client['toutiao']


def get_page(offset,keyword):
	data = {
		"offset": offset,
		"format": "json",
		"keyword": keyword,
		"autoload": "true",
		"count": "20",
		"cur_tab": 3,
		
		}
	headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
	url = 'https://www.toutiao.com/search_content/?' + urlencode(data) + '&from=gallery'
	
	try:
		response = requests.get(url,headers = headers)
		if response.status_code == 200:
			return response.text
		return None
	except RequestException:
		print('请求索引页出错')
		return None

def parse_page(html):
	
	page_urls = []
	data = json.loads(html)

	if data and 'data' in data.keys():
		for item in data.get('data'):
			page_urls.append(item.get('article_url'))
		# print(page_urls)
		return page_urls



def get_page_detail(url):
	try:
		headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
		response = requests.get(url,headers = headers)
		
		if response.status_code == 200:
			# print(response.text)
			return response.text
		return None
	except RequestException:
		print('请求详情页出错',url)
		return None

def parse_page_detail(html):
	soup = bs(html,'lxml')
	# print('===================================')
	title = soup.title.string
	print(title)
	# image_pattern = re.compile(r'http:\\\\/\\\\/[\s\S]*?\\\\/origin\\\\/pgc-image\\\\/[\s\S]*?\\',re.S)
	image_pattern = re.compile(r'url.*?"(http:.*?)"',re.S)
	result = re.findall(image_pattern,html)
	# print(result)
	if result:
		l = []
		for i in result[0::4]:
			image_url = i.replace("\\","")
			download_image(image_url)
			l.append(image_url)
		return {
			'tittle':title,
			'images':l,
		}
		#怎么才能让inages存成列表
	# title = re.compile("BASE_DATA.galleryInfo[\s\S]*?title: '([\s\S]*?)'",re.S)

def save_to_mango(urls):
	if db['toutiao'].insert(urls):
		print('存储到MongoDB成功',urls)
		return True
	return False

# 正则得用'gallery: JSON.parse\\((.*?)\\)' 而且得 loads两次 json.loads(json.loads())
def download_image(image_url):
	print('正在下载',image_url)
	try:
		response = requests.get(image_url)
		if response.status_code == 200:
			save_image(response.content)
		return None
	except RequestException:
		print('请求图片出错',image_url)
		return None

def save_image(content):
	file_path = "{0}/{1}.{2}".format(os.getcwd(),md5(content).hexdigest(),"jpg")
	if not os.path.exists(file_path):
		with open (file_path,'wb') as f:
			f.write(content)
			f.close()




def  main(offset,keyword):
	html = get_page(offset,keyword)
	# print(html)
	# urls = parse_page(html)
	# save_to_mango(urls)
	for url in parse_page(html):
		# print(url)
		html = get_page_detail(url)
		# print(html)
		if html:
			result = parse_page_detail(html)
			# print(result)
			save_to_mango(result)

if __name__ == '__main__':
	# for i in range(100):
	main(0, '街拍')
	pool = Pool()
	pool.map(main,range(10))
