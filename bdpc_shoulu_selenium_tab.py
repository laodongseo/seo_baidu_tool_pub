# ‐*‐ coding: utf‐8 ‐*‐
"""
selenium持续操作浏览器浏览器会崩溃,所以,
当前脚本由reload_control_pc.py控制,定时重启
重启前会去重已抓取的词
多线程脚本,默认是1
"""

from pyquery import PyQuery as pq
import threading
import queue
import time
from urllib.parse import urlparse
from openpyxl import load_workbook
from openpyxl import Workbook
import time
import gc
import random
import urllib3
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import random
import traceback
import tld
import psutil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


cookie_str = """
PSTM=1615340407;BIDUPSID={0};__yjs_duid=1_a1942d4ca1a959bb32e3ffff0cf07ad41617946073654;BAIDUID={1}:SL=0:NR=10:FG=1;MAWEBCUID=web_HZaROXCyXvOjHUxdDgsRzFWcFvyytfvmhKNANGkMBMqFBkpuhv;MSA_WH=375_667;sug=3;sugstore=0;ORIGIN=0;bdime=0;BDSFRCVID_BFESS=vgkOJeC62xkxKfjH_8JJt_0-QbzD6yQTH6aoiNadLAIWb-7j6rFpEG0PMU8g0K4-gVGPogKK0mOTHUuF_2uxOjjg8UtVJeC6EG0Ptf8g0f5;H_BDCLCKID_SF_BFESS=tRk8oK-atDvDqTrP-trf5DCShUFsaqTWB2Q-XPoO3KJ-_nD6yhnMbUA3BN0LQCrRBKOrbfbgy4op8P3y0bb2DUA1y4vpKMRUX2TxoUJ25fj8enrDqtnWhfkebPRiJPr9QgbP5lQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wDT8hD6PVKgTa54cbb4o2WbCQ-b7P8pcN2b5oQT8BBULfBpRJ5bRJMKtEL66U8n7s0lOUWJDkXpJvQnJjt2JxaqRC5h7R_p5jDh3Mbl_qbUTle4ROamby0hvctn6cShnaLfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDHt8J50ttJ3aQ5rtKRTffjrnhPF3qqkmXP6-hnjy3bRqMbD5WU7MeU3mBT0V0DuvXUnrQq3Ry6r42-39LPO2hpRjyxv4bU4iBPoxJpOJ5H6B0brIHR7WDqnvbURvD-ug3-7P3x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIEoC0XtK-hhCvPKITD-tFO5eT22-usWJ6m2hcHMPoosIJCBPLbyh43bPOJy58LL4jR2b71LfbUotoHXnJi0btQDPvxBf7p52OUMh5TtUJMexjFbPTPqt4bht7yKMnitIj9-pnG0lQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuDj0WD5O0eats-bbfHD3t3RcVaJ3-qTrnhPF354-fXP6-35KHMI3OabQ_WUAWOlcmBT0V0tDhQaj8Ql37JD6yBlrq5pRNOf3PqjJ8jRDzK-oxJpOuQRbMopk2HR34sUJvbURvD-ug3-7P-x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-j5JIE3-oJqC-MMKoP;BD_UPN=12314353;BDORZ=B490B5EBF6F3CD402E515D22BCDA1598;H_WISE_SIDS=110085_114550_127969_164325_178384_178640_179349_179379_179432_179623_181133_181588_181824_182233_182273_182290_182531_183035_183330_183346_184012_184267_184319_184794_184809_184891_184894_185029_185036_185268_185519_185632_185652_185880_186015_186318_186412_186580_186596_186662_186820_186841_186844_187003_187023_187067_187087_187214_187287_187345_187433_187447_187563_187670_187726_187815_187915_187926_187929_188182_188267_188296_188332_188425_188670_188733_188741_188787_188843_188871_188897_188993_189150;plus_cv=1::m:7.94e+147;SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03840151844LlLPJ4liFkPcS35X7t9kqiG84PSafLS35mwGXc0pmTvgP0uWCxLOv4Xsl2WQc6exfIAxZyV%2FrqE938dOcfAe5RlZhu04YMuQWxGa8H8NumwrjcyyDqrr9H0bbVbwu6LdPbzLVV78TcJrlGG9tW5Cb7gRmq2bhCFBoAjAsClGkvNuIfu0nlcbyqLmWnUFJff3n%2Fsc00SQ9okPLUFYlI2zrruXHvG%2BoKdePpCANsg65qdKU5%2BCylf38e9egJ1SrBlKYGlN88O%2FNzuiA1%2BL3aXiXHfzuLJ%2Fq8ETDkV8%2BMqNcFaRg6PyqgKscfVme0ULDD%2Fk%2B1u8RLJ0BMCS85punosHbkKZq3kA3ifLp0GMwxY9%2BsCNEwRi6oS6Bvv7PoMeWqbD98264807454627712492692251154698;ab_sr=1.0.1_OWU1ZDlmNThlY2FlYWQ0ZjcxY2YxMmM2ZjdkZjg1ZjI1OWUwODViYTllNGEyNTQ5Y2JlYzVlNDdhOGVmNjAzMzU5ZGQyNmFlNDQ1OGE1ZTUyNjUwNTU4OGI3YmU2MDI3OGQwZWM1Yjk4ODhmYzgwNWQzMjI4YjhhNjk5NGRmNmVmNzg4ZTQyOTU0OWJmZTMxZGU5MTU1Yjk0ZDJiYWRkNQ==;H_PS_PSSID=31254_26350;BDRCVFR[PaHiFN6tims]=9xWipS8B-FspA7EnHc1QhPEUf;delPer=0;BD_CK_SAM=1;PSINO=7;H_PS_645EC=040fjM1HE7uylNwAjeRau944%2BjPtKpH6WePiuUl3qkhhXyLWouXO93lpYux%2Fmqm%2Bx6WFNQ2q;BA_HECTOR=8ga08l0l84ak2k0guj1gmafbc0r;WWW_ST=1634024820151
"""

# 生成随机cookie
def get_cookie():
	global cookie_str
	seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	psid = uid = ''
	for _ in range(32):
		s = random.choice(seed) 
		psid = f'{psid}{s}'
		s = random.choice(seed) 
		uid = f'{uid}{s}'
	cookie_str = cookie_str.strip().format(psid,uid)
	return cookie_str


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
	driver = webdriver.Chrome(options=option,executable_path=chromedriver_path )
	return driver


# 只解密加密url用
def get_header():
	my_header = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Encoding': 'deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
		# 'Cookie': get_cookie(),
		'Host': 'www.baidu.com',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-User': '?1',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': random.choice(list_ua),
		}
	return my_header


class BdpcShoulu(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	@staticmethod
	def read_txt(filepath):
		q = queue.Queue()
		for url in open(filepath, encoding='utf-8'):
			url = url.strip()
			q.put(url)
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

	# 获取某词serp源码所有url
	def get_encrpt_urls(self, html, url):
		encrypt_url_list = []
		real_urls = []
		doc = pq(html)
		title = doc('title').text()
		if '_百度搜索' in title and 'https://www.baidu.com/' in url:
			div_list = doc('#content_left .result').items()  # 自然排名
			div_op_list = doc('#content_left .result-op').items()  # 非自然排名
			for div in div_list:
				a = div('h3 a')
				if not a: # 空对象pyquery.pyquery.PyQuery 为假
					a = div('.c-result-content article section a') #专业问答样式
				if a:
					encrypt_url = a.attr('href')
					encrypt_url_list.append((encrypt_url))
			for div in div_op_list:
				link = div.attr('mu')  # 真实url,有些op样式没有mu属性
				# print(link,rank_op)
				if link:
					real_urls.append((link))
				else:
					a = div('article a')
					if a:
						encrypt_url = a.attr('href')
						encrypt_url_list.append((encrypt_url))
		else:
			print('源码异常,可能反爬', title)
			time.sleep(60)

		return encrypt_url_list, real_urls

	# 解密某条加密url
	def decrypt_url(self, encrypt_url, retry=1):
		real_url = None  # 默认None
		if encrypt_url:
			my_header = get_header()
			try:
				encrypt_url = encrypt_url.replace('http://', 'https://') if 'https://' not in encrypt_url else encrypt_url
				r = requests.head(encrypt_url, headers=my_header,timeout=60)
			except Exception as e:
				print(encrypt_url, '解密失败', e)
				time.sleep(200)
				if retry > 0:
					self.decrypt_url(encrypt_url, my_header, retry - 1)
			else:
				real_url = r.headers['Location'] if 'Location' in r.headers else None
		return real_url


	# 获取某词serp源码首页排名真实url
	def get_real_urls(self, encrypt_url_list):
		real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
		real_url_set = set(real_url_list)
		real_url_set.remove(None) if None in real_url_set else real_url_set
		real_url_list = list(real_url_set)
		return real_url_list


	# 线程函数
	def run(self):
		global driver,webdriver_chrome_ids,check_num,shoulu_num
		while 1:
			target_url = q.get()
			print('url:',target_url)
			try:
				html,now_url = self.get_html(target_url)
				encrypt_url_list, real_urls = self.get_encrpt_urls(html, now_url)
				real_url_list = self.get_real_urls(encrypt_url_list)
				real_urls.extend(real_url_list)
				print(real_urls)
			except Exception as e:
				traceback.print_exc(file=open(f'{today}log.txt', 'a'))
				print(e, '杀死残留进程,重启selenium')
				q.put(target_url)
				driver.quit()
				kill_process(webdriver_chrome_ids)
				gc.collect()
				time.sleep(20)
				driver = get_driver(chrome_path, chromedriver_path, ua)
				webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
				print(f'chrome的pid:{webdriver_chrome_ids}')
				with open('bdpc1_script_ids.txt', 'a', encoding='utf-8') as f_pid:
					f_pid.write('\n'.join([str(id) for id in webdriver_chrome_ids]))
			else:
				# 防止多线程写入文件错乱
				lock.acquire()
				check_num += 1
				if target_url in real_urls or target_url.replace('https','http') in real_urls:
					shoulu_num += 1
					f.write(f'{target_url}\t收录\n')
				else:
					f.write(f'{target_url}\t未收录\n')
				f.flush()
				lock.release()
			finally:
				del target_url
				gc.collect()
				q.task_done()
				time.sleep(2.5)


if __name__ == "__main__":
	start = time.time()
	local_time = time.localtime()
	today = time.strftime('%Y%m%d', local_time)
	OneHandle_UseNum,OneHandle_MaxNum = 1,1 # 计数1个handle打开网页次数(防止浏览器崩溃)
	list_ua = [i.strip() for i in open('ua_pc.txt', 'r', encoding='utf-8')]
	chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
	chromedriver_path = 'D:/install/pyhon36/chromedriver.exe'
	ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'

	driver = get_driver(chrome_path,chromedriver_path,ua)
	webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
	print(f'chrome的pid:{webdriver_chrome_ids}')
	with open('bdpc1_script_ids.txt','w',encoding='utf-8') as f_pid:
		f_pid.write('\n'.join([str(id) for id in webdriver_chrome_ids]))

	start = time.time()
	check_num,shoulu_num = 0,0
	lock = threading.Lock() # 锁
	list_ua = [i.strip() for i in open('ua_pc.txt', 'r', encoding='utf-8')]
	q = BdpcShoulu.read_txt('pc-url.txt') # url队列
	f = open('pc_shoulu.txt','w+',encoding='utf-8')
	# 设置线程数
	for i in list(range(1)):
		t = BdpcShoulu()
		t.setDaemon(True)
		t.start()
	q.join()
	f.flush()
	f.close()
	end = time.time()
	spent_time = (end - start) / 60
	print(f'耗时{spent_time}min,成功查询{check_num},收录{shoulu_num}个')
