# ‐*‐ coding: utf‐8 ‐*‐
"""
selenium4版本
selenium持续操作浏览器浏览器会崩溃,所以,
多线程脚本,默认是1
记录搜索结果的个数
"""

from pyquery import PyQuery as pq
import threading
import queue
import time
import gc
import random
import urllib3
import os,re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import traceback
import psutil
import pandas as pd
from selenium.webdriver.chrome.service import Service

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


str_uas = """
Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.41
Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3870.400 QQBrowser/10.8.4405.400
Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36
Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36
Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0
"""
list_ua = [i.strip() for i in str_uas.split('\n') if i.strip()]


def set_driver(driver):
	try:
		# 防止反爬
		driver.get('http://www.python66.com/stealth.min.js')
		time.sleep(0.5)
		js_hidden = driver.page_source
		driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
		  "source": js_hidden
		})

		# 设置允许弹窗(headless模式会执行失败)
		# driver.get(url_pop)
		# time.sleep(0.5)
		# driver.execute_script(js_allow_pop)
	except Exception as e:
		traceback.print_exc()
	finally:
		return driver


# 获取chromedriver及其启动的浏览器pid
def get_webdriver_chrome_ids(driver):
	"""
	浏览器pid是chromedriver的子进程
	"""
	all_ids = []
	main_id = driver.service.process.pid
	all_ids.append(main_id)
	p = psutil.Process(main_id)
	child_ids = p.children(recursive=True)
	[all_ids.append(id_obj.pid) for id_obj in child_ids]
	return all_ids


# 根据pid杀死进程
def kill_process(p_ids):
	try:
		for p_id in p_ids:
			os.system(f'taskkill  /f /pid {p_id}')
	except Exception as e:
		pass
	time.sleep(1)


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
	# option.add_argument("--window-size=1920x1080")
	option.add_argument("--disable-features=VizDisplayCompositor")
	option.add_argument('headless')
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
	s = Service(executable_path=chromedriver_path)
	driver = webdriver.Chrome(service=s,options=option)
	driver = set_driver(driver)
	return driver



class BdpcShoulu(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	@staticmethod
	def read_excel(filepath):
		q = queue.Queue()
		for index,row in pd.read_excel(filepath).dropna().iterrows():
			q.put(row)
		return q


	# 获取源码,异常由run函数try捕获
	def get_html(self,kwd):
		global driver,OneHandle_UseNum
		html = now_url = ''
		if OneHandle_UseNum > OneHandle_MaxNum:
			OneHandle_UseNum = 0
			# driver.switch_to.new_window('tab') # selenium4
			driver.execute_script("window.open('https://www.baidu.com/')")
			close_handle()
		else:
			driver.get('https://www.baidu.com/')
		OneHandle_UseNum += 1
		input = WebDriverWait(driver, 30).until(
			EC.visibility_of_element_located((By.ID, "kw"))
		)
		input_click_js = 'document.getElementById("kw").click()'
		driver.execute_script(input_click_js)  # 点击输入框

		input_js = 'document.getElementById("kw").value="{0}"'.format(kwd)
		driver.execute_script(input_js)  # 输入搜索词

		baidu = WebDriverWait(driver, 20).until(
			EC.visibility_of_element_located((By.ID, "su"))
		)
		click_js = 'document.getElementById("su").click()'
		driver.execute_script(click_js)  # 点击搜索

		# 等待首页元素加载完毕
		# 此处异常由run函数的try捕获
		bottom = WebDriverWait(driver, 20).until(
			EC.visibility_of_element_located((By.ID, "help"))
		)
		# 页面下拉
		js_xiala = 'window.scrollBy(0,{0} * {1})'.format('document.body.scrollHeight', random.random() / 5)
		driver.execute_script(js_xiala)
		html = driver.page_source
		now_url = driver.current_url
		return html,now_url


	def parse(self, html):
		doc = pq(html)
		text = doc('span.hint_PIwZX').text().strip()
		obj = re.search('百度为您找到相关结果约(.*?)个',text,re.S|re.I)
		if obj:
			text_num = obj.group(1).replace(',','')
			return text_num


	# 线程函数
	def run(self):
		global driver,webdriver_chrome_ids,check_num
		while 1:
			row = q.get()
			kwd = row['kwd']
			try:
				html,now_url = self.get_html(kwd)
				text_num = self.parse(html)
				print(text_num)
			except Exception as e:
				traceback.print_exc(file=open(f'{today}log.txt', 'a'))
				print(e, '杀死残留进程,重启selenium')
				q.put(row)
				driver.quit()
				kill_process(webdriver_chrome_ids)
				gc.collect()
				time.sleep(5)
				driver = get_driver(chrome_path, chromedriver_path, ua)
				webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
				print(f'chrome的pid:{webdriver_chrome_ids}')
				with open('bdpc1_script_ids.txt', 'a', encoding='utf-8') as f_pid:
					f_pid.write('\n'.join([str(id) for id in webdriver_chrome_ids]))
			else:
				# 防止多线程写入文件错乱
				lock.acquire()
				check_num += 1
				f.write(f'{kwd}\t{text_num}\n')
				f.flush()
				lock.release()
			finally:
				del row
				gc.collect()
				q.task_done()
				time.sleep(0.2)


if __name__ == "__main__":
	start = time.time()
	local_time = time.localtime()
	today = time.strftime('%Y%m%d', local_time)
	OneHandle_UseNum,OneHandle_MaxNum = 1,1 # 计数1个handle打开网页次数(防止浏览器崩溃)
	chrome_path = r"C:/Program Files\Google/Chrome/Application/chrome.exe"
	chromedriver_path = r'E:/chromedriver\E:/chromedriver.exe'
	ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
	driver = get_driver(chrome_path,chromedriver_path,ua)
	webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
	print(f'chrome的pid:{webdriver_chrome_ids}')
	with open('bdpc1_script_ids.txt','w',encoding='utf-8') as f_pid:
		f_pid.write('\n'.join([str(id) for id in webdriver_chrome_ids]))
	

	check_num = 0
	lock = threading.Lock() # 锁
	kwd_excel = 'kwd.xlsx'
	q = BdpcShoulu.read_excel(kwd_excel) # url队列
	print(q.qsize())
	f = open(f'{os.path.splitext(kwd_excel)[0]}_serpnum{today}.txt','w+',encoding='utf-8')
	# 设置线程数
	for i in list(range(1)):
		t = BdpcShoulu()
		t.daemon = True
		t.start()
	q.join()
	f.flush()
	f.close()
	end = time.time()
	spent_time = (end - start) / 60
	print(f'耗时{spent_time}min,成功查询{check_num}')

