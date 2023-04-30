"""
翻页采集爱站某网站各个栏目的词库
"""

#‐*‐coding:utf‐8‐*‐
import requests
import threading
import queue
from pyquery import PyQuery as pq
import time,traceback,random
from urllib import parse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc


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
		div_obj=WebDriverWait(driver,10,0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "baidurank-list")))
		html = driver.page_source
	except Exception as e:
		traceback.print_exc()
	else:
		return html

def is_login(driver):
	while True:
		html = driver.page_source
		doc= pq(str(html))
		text = doc('.nav-user-infos p').text().strip()
		if '会员' in text:
			print('login success...')
			break

def parse(html):
	contents = []
	next_page = ''
	if html:
		doc= pq(str(html))
		title = doc('title').text()
		if '的百度排名情况_' in title:
			tr_list = doc('.baidurank-list table tbody tr').items()
			for tr in tr_list:
				row = []
				td_list = tr('td:not(.path)').items()
				for td in td_list:
					if td.attr('class') == 'owner':
						a = td('a')
						link,title = a.attr('href'),a.text().strip()
						text = f'{link}\t{title}'
					else:
						text = td.text().strip()
					row.append(text)
				contents.append(row)
	return contents


# 线程函数
def main():
	while 1:
		url = q.get()
		print('url',url)
		try:
			html = get_html(url)
			contents = parse(html)
		except Exception as e:
			traceback.print_exc() 
		else:
			for row in contents:
				for element in row:
					f.write(f'{element}\t')
				f.write('\n')
				print(row)
			f.flush()
		finally:
			q.task_done()
			time.sleep(6)


if __name__ == "__main__":
	js_pop = 'document.querySelector("body > settings-ui").shadowRoot.querySelector("#main").shadowRoot.querySelector("settings-basic-page").shadowRoot.querySelector("#basicPage > settings-section.expanded > settings-privacy-page").shadowRoot.querySelector("#pages > settings-subpage.iron-selected > settings-category-default-radio-group").shadowRoot.querySelector("#enabledRadioOption").shadowRoot.querySelector("#button > div.disc").click()'
	OneHandle_UseNum,OneHandle_MaxNum = 1,1 # 计数1个handle打开网页次数(防止浏览器崩溃)
	config_list = [
	('keep1.net-pc','https://baidurank.aizhan.com/baidu/keep1.net/-1/0/{0}/position/1/',46),
	('keep1.net-mo','https://baidurank.aizhan.com/mobile/keep1.net/-1/0/{0}/position/1/',37),
	('youhuaxing.cn-pc','https://baidurank.aizhan.com/baidu/keep1.net/-1/0/{0}/position/1/',5),
	('youhuaxing.cn-mo','https://baidurank.aizhan.com/mobile/keep1.net/-1/0/{0}/position/1/',5)
	]
	chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
	chromedriver_path=r'D:/py3script/selenium测试/chromedriver.exe'
	options = uc.ChromeOptions()
	# options.add_argument('--headless')
	driver = uc.Chrome(options=options,driver_executable_path=chromedriver_path,browser_executable_path=chrome_path)
	driver.get('chrome://settings/content/popups?search=弹出')
	time.sleep(1)
	driver.execute_script(js_pop)
	time.sleep(1)
	driver.get('https://www.aizhan.com/')
	is_login(driver)
	for line in config_list:
		fname,url_type,max_num = line
		# 结果保存文件
		f = open(f'{fname}.txt', 'w+', encoding='utf-8')
		# url队列
		q = queue.Queue()
		for i in range(1,int(max_num) + 1):
			my_url = url_type.format(i) if max_num != 0 else url
			q.put(my_url)

		# 设置线程数
		for i in list(range(1)):
			t = threading.Thread(target=main)
			t.setDaemon(True)
			t.start()
		q.join()
		f.flush()
		f.close()
