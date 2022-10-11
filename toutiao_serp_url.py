"""
读取excel
按照关键词类别在头条搜索
采集搜索结果页的url及title信息
"""

#‐*‐coding:utf‐8‐*‐
import requests
import threading
import queue,re
from pyquery import PyQuery as pq
import time,traceback,random
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import pandas as pd
from urllib.parse import unquote


def close_handle():
	if len(driver.window_handles) > 1:
		for handle in driver.window_handles[0:-1]:
			driver.switch_to.window(handle)
			time.sleep(1)
			driver.close()
		# 检测关闭结束
		while True:
			if len(driver.window_handles) == 1:
				break
		# 切到唯一窗口
		driver.switch_to.window(driver.window_handles[0])


def read_excel(filepath):
		q = queue.Queue()
		df = pd.read_excel(filepath).dropna()
		for index,row in df.iterrows():
			q.put(row)
		return q



def get_driver(chrome_path,chromedriver_path,ua):
	ua = ua
	option = Options()
	option.binary_location = chrome_path
	# option.add_argument('disable-infobars')
	option.add_argument("user-agent=" + ua)
	option.add_argument("--no-sandbox")
	option.add_argument("--disable-dev-shm-usage")
	option.add_argument("--disable-gpu")
	option.add_argument("--disable-features=NetworkService")
	option.add_argument("window-size=1000,1080")
	option.add_argument("--disable-features=VizDisplayCompositor")
	# option.add_argument('headless')
	option.add_argument('log-level=3') #屏蔽日志
	option.add_argument('--ignore-certificate-errors-spki-list') #屏蔽ssl error
	option.add_argument('-ignore -ssl-errors') #屏蔽ssl error
	option.add_experimental_option("excludeSwitches", ["enable-automation"]) 
	option.add_experimental_option('useAutomationExtension', False)
	No_Image_loading = {"profile.managed_default_content_settings.images": 1}
	option.add_experimental_option("prefs", No_Image_loading)
	# 屏蔽webdriver特征
	option.add_argument("--disable-blink-features")
	option.add_argument("--disable-blink-features=AutomationControlled")
	driver = webdriver.Chrome(options=option,executable_path=chromedriver_path)
	return driver


# 获取源码
def get_html(url):
	global OneHandle_UseNum
	if OneHandle_UseNum > OneHandle_MaxNum:
		driver.execute_script("window.open('')")
		time.sleep(1)
		close_handle()
	driver.get(url)
	OneHandle_UseNum += 1
	try:
		div_obj=WebDriverWait(driver,10,0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "cs-tabs-bar-wrap")))
	except Exception as e:
		traceback.print_exc()
	else:
		html = driver.page_source
		return html


def parse(html):
	row_list = []
	doc= pq(str(html))
	title = doc('title').text()
	if '- 头条搜索' in title:
		div_list = doc('div.s-result-list .result-content div.cs-card-content').items()
		for div in div_list:
			a = div('a.text-ellipsis')
			link = a.attr('href')
			link = unquote(link, 'utf-8').replace('/search/jump?url=','').replace('\n','')
			
			title_serp = a.text()
			title = re.sub(r'\s+','',title_serp)
			# title是否有飘红
			is_red = '是' if '<em>' in a.html() else '否'

			huida_num_desc = div('.cs-source-content span:last').text().strip()
			huida_num = re.sub('共|个|回答>','',huida_num_desc)
			print(huida_num)
			if title:
				row_list.append([title,link,huida_num,is_red])
	else:
		time.sleep(120)
	return row_list


# 线程函数
def main():
	global IsHeader
	while 1:
		row = q.get()
		kwd = row['关键词']
		url = f'https://so.toutiao.com/search?dvpf=pc&source=input&keyword={kwd}&pd=question&page_num=0'
		try:
			html = get_html(url)
			row_list = parse(html)
		except Exception as e:
			traceback.print_exc() 
		else:
			for elements in row_list:
				row['title'] ,row['url'],row['回答数'],row['是否飘红'] = elements
				df = row.to_frame().T
				with lock:
					if IsHeader == 0:
						df.to_csv(CsvFile,encoding='utf-8-sig',mode='w+',index=False)
						IsHeader = 1
					else:
						df.to_csv(CsvFile,encoding='utf-8-sig',mode='a+',index=False,header=False)
		finally:
			q.task_done()
			time.sleep(3)


if __name__ == "__main__":
	OneHandle_UseNum,OneHandle_MaxNum = 1,1 # 计数1个handle打开网页次数(防止浏览器崩溃)
	chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
	chromedriver_path = 'D:/install/pyhon36/chromedriver.exe'
	ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
	driver = get_driver(chrome_path,chromedriver_path,ua)
	q = read_excel('kwd-vrrw.net.xlsx')
	CsvFile = 'toutiao_serpUrl_res-vrrw.net.csv'
	IsHeader =0
	lock = threading.Lock()

	# driver.get('https://www.toutiao.com')
	# driver.execute_script('window.alert ("30s内 请设置谷歌允许js弹窗")')
	# time.sleep(30)
	# 设置线程数
	for i in list(range(1)):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()
