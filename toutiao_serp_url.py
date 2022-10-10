"""
读取excel
按照关键词类别搜搜头条
采集搜索结果页的url
"""

#‐*‐coding:utf‐8‐*‐
import requests
import threading
import queue,re
from pyquery import PyQuery as pq
import time,traceback,random
from urllib import parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
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
	if '头条搜索' in title:
		a_list = doc('div.s-result-list div.cs-card-content a.text-ellipsis').items()
		for a in a_list:
			link = a.attr('href')
			link = unquote(link, 'utf-8').replace('/search/jump?url=','').replace('\n','')

			title_serp = a.text()
			title = re.sub(r'\s+','',title_serp)
			row_list.append([title,link])
	return row_list


# 线程函数
def main():
	global IsHeader
	while 1:
		row = q.get()
		kwd = row['kwd']
		url = f'https://so.toutiao.com/search?dvpf=pc&source=input&keyword={kwd}&pd=question&page_num=0'
		try:
			html = get_html(url)
			row_list = parse(html)
		except Exception as e:
			traceback.print_exc() 
		else:
			for title,url in row_list:
				row['title'] ,row['url'] = title,url
				df = row.to_frame().T
				if IsHeader == 0:
					df.to_csv(CsvFile,encoding='utf-8-sig',mode='w+',index=False)
					IsHeader = 1
				else:
					df.to_csv(CsvFile,encoding='utf-8-sig',mode='a+',index=False,header=False)
		finally:
			q.task_done()
			time.sleep(6)


if __name__ == "__main__":
	OneHandle_UseNum,OneHandle_MaxNum = 1,1 # 计数1个handle打开网页次数(防止浏览器崩溃)
	chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
	chromedriver_path = 'D:/install/pyhon36/chromedriver.exe'
	options = uc.ChromeOptions()
	# options.add_argument('--headless')
	driver = uc.Chrome(options=options,driver_executable_path=chromedriver_path,browser_executable_path=chrome_path)
	q = read_excel('kwd.xlsx')
	CsvFile = 'toutiao_serpUrl.csv'
	IsHeader =0

	driver.get('https://www.toutiao.com')
	driver.execute_script('window.alert ("60s内 请设置谷歌允许js弹窗")')
	# time.sleep(60)
	# 设置线程数
	for i in list(range(1)):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()
