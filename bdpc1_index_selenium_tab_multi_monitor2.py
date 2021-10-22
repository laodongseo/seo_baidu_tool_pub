# ‐*‐ coding: utf‐8 ‐*‐
"""
selenium3
selenium持续操作浏览器浏览器会崩溃!所以:
脚本限制1个handle打开网页个数,持续切换标签页打开url(先手动设置浏览器：设置-隐私和安全性-网站设置-弹出式窗口和重定向 设置为允许)

功能:
   1)指定几个域名,分关键词种类监控首页词数
   2)抓取serp所有url,提取域名并统计各域名首页覆盖率
   3)通过tpl属性记录serp排名url的特征
   4)支持顶级域名或者其他域名
提示:
  1)含自然排名和百度开放平台的排名
  2)百度开放平台的样式mu属性值为排名url,mu不存在提取article里的url
  3)2020xiaoqu_kwd_city_new.xlsx:sheet名为关键词种类,sheet第一列放关键词
结果:
	bdpc1_index_info.txt:各监控站点词的排名及url,如有2个url排名,只取第一个
	bdpc1_index_all.txt:serp所有url及样式特征
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
PSTM=1615340407; BIDUPSID={0}; __yjs_duid=1_a1942d4ca1a959bb32e3ffff0cf07ad41617946073654; BAIDUID={1}:SL=0:NR=10:FG=1; MAWEBCUID=web_HZaROXCyXvOjHUxdDgsRzFWcFvyytfvmhKNANGkMBMqFBkpuhv; MSA_WH=375_667; sug=3; sugstore=0; ORIGIN=0; bdime=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; plus_cv=1::m:7.94e+147; H_WISE_SIDS=110085_114550_127969_178384_178640_179349_179379_179432_179623_181133_181588_182233_182273_182290_182530_183035_183330_184012_184267_184319_184794_184891_184894_185029_185268_185519_185632_185652_185880_186015_186318_186412_186580_186596_186662_186820_186841_186844_187023_187067_187087_187214_187287_187345_187433_187447_187563_187670_187726_187815_187915_187926_187929_188182_188267_188296_188332_188425_188614_188670_188733_188741_188787_188843_188871_188897_188993_189043_189150_189269_189325; BD_UPN=12314353; BDSFRCVID_BFESS=Os4OJexroG0ksyjHj78Kt_0-QXWFFS6TDYLtOwXPsp3LGJLVgbfZEG0Pt_m2Fut-Df-rogKK0mOTHUAF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tRk8oK-atDvDqTrP-trf5DCShUFsb-RlB2Q-XPoO3KJ-_nD6yhnMbT83BN0LQCrRBKOrbfbgy4op8P3y0bb2DUA1y4vpKMRUX2TxoUJ25fj8enrDqtnWhfkebPRiJPr9QgbP5lQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wDT8hD6PVKgTa54cbb4o2WbCQHxnr8pcN2b5oQT8BBULfBpRJ5avJMKtEL66U8n7s0lOUWJDkXpJvQnJjt2JxaqRC5h7R_p5jDh3Mbl_qbUTle4ROamby0hvctn6cShnaLfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDHt8J50ttJ3aQ5rtKRTffjrnhPF3y6_dXP6-hnjy3bRqMbD5WU7MepbmBT0V0DuvXUnrQq3Ry6r42-39LPO2hpRjyxv4bU4iBPoxJpOJ5H6B0brIHR7WDqnvbURvD-ug3-7P3x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIEoCtytIthbK0r5nJbq4P0-f602tbq--o2WbCQbJ3O8pcNLTDK2-PbyUjBBp4OWeQJMKtELRo0sKQw0qO1j4_eMtTKKU7CWGvasC3_JtoPqh5jDh3Y3jksD-4Je4bp3aRy0hvctn6cShna5fjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2b6QhDGujt6_jJJ3aQ5rtKRTffjrnhPF3XnJ3XP6-hnjy3bRWQ-T_WnFbbhvmBT0V0qkiQ4jgtq3RymJJ2-39LPO2hpRjyxv4bPDEW4oxJpOJXKDHKt52HlbtKtovbURvD-ug3-7P3x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIE3-oJqCDBMI-G3j; b2b_first=1634117200; RT="z=1&dm=baidu.com&si=k97d09l8cca&ss=kupb6uur&sl=2&tt=54d&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=69z&ul=ez5&hd=f0p"; BAIDUID_BFESS=5942B6B2489AF018E9B0CB23042B5468:FG=1; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03841883355QCv5WIGZhFF2RU2ldgqghNHNXdJoiIMJjMw3VrKvYDWLN843luZvUtDMgHy%2FrHeuXpI1A%2FgXs5QSqQzBpIyIPzxdefaxCtfoz4ZTp%2BVmatTvZ6Tk%2FRtD0J9m9tF3AW9f7BMa9p%2Fwo5Ckye%2FWiWcCezAOgXJV4O9wttVjJ0Qwio59pwKbU4E7yPwystOjptuXOmE%2B0GeaJ9z3BqH5FUBbNd5RZ8dCcfA4Z6HdkPuXgNzaycR04gjZKx6jNtSzpKCoT%2FTPSamtBvce5vLAl%2F2ETb%2FIXvOwRek%2ByBRG10TRfAiY9j2dBIWTRPu0xRnBW8C4LF0NHJjUZ%2BRwSRz8siCiQJ%2FOgoNFtAzE40JzFqj85Je0XylvPmWB3Ksg4jwfVJGa97817693573772344993757455054810; uc_login_unique=f7f2abaa99a6bf1ab5078b309c80e571; uc_recom_mark=cmVjb21tYXJrXzExMjgyMTQ5; BD_HOME=1; delPer=0; BD_CK_SAM=1; PSINO=2; H_PS_PSSID=34837_34446_34067_31254_34712_34584_34504_34829_34578_26350_34691; COOKIE_SESSION=8075_0_8_8_6_32_1_0_5_7_28_1_8092_0_31_0_1634185046_0_1634185015%7C9%231124514_198_1632734797%7C9; H_PS_645EC=86b1TxTvOccdY2fVDfR7xFZHwiRoleFeR61vT2OITGo2qf9H9sy%2FXz2OJf0; BA_HECTOR=0085850k2125a0859l1gmffmd0r; BDSVRTM=0; WWW_ST=1634189034018
"""

# 生成随机cookie
def get_cookie():
	global cookie_str
	seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	uid = ''.join([random.choice(seed) for _ in range(32)])
	psid = ''.join([random.choice(seed) for _ in range(32)])
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
	driver = webdriver.Chrome(options=option,executable_path=chromedriver_path)
	return driver


# 只解密加密url用
def get_header():
	my_header = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Encoding': 'deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
		'Cookie':get_cookie(),
		'Host': 'www.baidu.com',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-User': '?1',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': random.choice(list_ua),
		}
	return my_header


def close_handle():
	global driver
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


class bdpcIndexMonitor(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	@staticmethod
	def read_excel(filepath):
		q = queue.Queue()
		group_list = []
		kwd_dict = {}
		wb_kwd = load_workbook(filepath)
		for sheet_obj in wb_kwd:
			sheet_name = sheet_obj.title
			group_list.append(sheet_name)
			kwd_dict[sheet_name] = []
			col_a = sheet_obj['A']
			for cell in col_a:
				kwd = (cell.value)
				# 加个判断吧
				if kwd:
					q.put([sheet_name, kwd])
		return q, group_list


	# 获取源码
	def get_html(self,kwd):
		global driver,OneHandle_UrlNum
		if OneHandle_UrlNum > 3:
			OneHandle_UrlNum = 1
			# driver.switch_to.new_window('tab') # selenium4
			driver.execute_script("window.open('https://www.baidu.com/')")
			close_handle()
		else:
			driver.get('https://www.baidu.com/')
		OneHandle_UrlNum += 1
		input = WebDriverWait(driver, 30).until(
			EC.visibility_of_element_located((By.ID, "kw"))
		)
		input_click_js = 'document.getElementById("kw").click()'
		driver.execute_script(input_click_js)  # 点击输入框

		input_js = f'document.getElementById("kw").value="{kwd}"'
		driver.execute_script(input_js)  # 输入搜索词

		baidu = WebDriverWait(driver, 20).until(
			EC.visibility_of_element_located((By.ID, "su"))
		)
		click_js = 'document.getElementById("su").click()'
		driver.execute_script(click_js)  # 点击搜索

		# 元素加载,判断是否为正常搜索结果页
		try:
			bottom = WebDriverWait(driver, 20).until(
				EC.visibility_of_element_located((By.ID, "help"))
			)
		except Exception as e:
			print(e)
			if '安全验证' in driver.title:
					print(driver.title,'sleep 30s')
					time.sleep(30)
			return
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
				rank = div.attr('id') if div.attr('id') else 'id_xxx'
				tpl = div.attr('tpl') if div.attr('tpl') else 'tpl_xxx'
				if rank:
						a = div('h3 a') # 空对象pyquery.pyquery.PyQuery为假
						encrypt_url = a.attr('href') if a else None
						encrypt_url_list.append((encrypt_url, rank, tpl))
			for div in div_op_list:
				rank_op = div.attr('id') if div.attr('id') else 'id_xxx'
				tpl = div.attr('tpl') if div.attr('tpl') else 'tpl_xxx'
				if rank_op:
					link = div.attr('mu')  # 真实url,有些op样式没有mu属性
					if link:
						real_urls.append((link, rank_op, tpl))
					else:
						encrypt_url = div('article a').attr('href')
						encrypt_url_list.append((encrypt_url, rank_op, tpl))

		else:
			print('源码异常,可能反爬', title)
			time.sleep(60)

		return encrypt_url_list, real_urls


	# 解密某条加密url
	def decrypt_url(self, encrypt_url, my_header, retry=1):
		# encrypt_url可能是None
		if encrypt_url:
			try:
				encrypt_url = encrypt_url.replace('http://', 'https://') if 'https://' not in encrypt_url else encrypt_url
				r = requests.head(encrypt_url, headers=my_header,timeout=60)
			except Exception as e:
				print(encrypt_url, '解密失败sleep 120s', e)
				time.sleep(120)
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


	# 提取某url的顶级域名
	def get_top_domain(self,real_url):
		top_domain = ''
		if real_url:
			try:
				obj = tld.get_tld(real_url,as_object=True)
				top_domain = obj.fld
			except Exception as e:
				print(e,'top domain:error')
		return top_domain


	# 获取某词serp源码首页排名的顶级域名
	def get_top_domains(self,real_urls_rank):
		domain_url_dicts = {}
		for real_url, my_order, tpl in real_urls_rank:
			if real_url:
				top_domain = self.get_top_domain(real_url)
				# 一个词某域名多个url有排名,算一次
				domain_url_dicts[top_domain] = (real_url,my_order,tpl) if top_domain not in domain_url_dicts else domain_url_dicts[top_domain]
		return domain_url_dicts


	# 线程函数
	def run(self):
		global driver,webdriver_chrome_ids
		while 1:
			group_kwd = q.get()
			group, kwd = group_kwd
			print(group,kwd)
			try:
				html_now_url = self.get_html(kwd)
				if not html_now_url:
					q.put(group_kwd)
					continue
				html,now_url = html_now_url
				encrypt_url_list_rank, real_urls_rank = self.get_encrpt_urls(html, now_url)
			except Exception as e:
				traceback.print_exc(file=open(f'{today}log.txt', 'a'))
				print(e,'杀死残留进程,重启selenium')
				q.put(group_kwd)
				driver.quit()
				kill_process(webdriver_chrome_ids)
				gc.collect()
				driver = get_driver(chrome_path, chromedriver_path, ua)
				webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
				print(f'webdriver+chrome的pid:{webdriver_chrome_ids}')
			else:
				for my_serp_url, my_order, tpl in encrypt_url_list_rank:
					my_header = get_header()
					my_real_url = self.decrypt_url(my_serp_url, my_header)
					lock.acquire()
					f_all.write(f'{kwd}\t{my_real_url}\t{my_order}\t{tpl}\t{group}\n')
					f_all.flush()
					lock.release()
					time.sleep(0.2)
					real_urls_rank.append((my_real_url, my_order, tpl))

				domain_url_dicts = self.get_top_domains(real_urls_rank)
				if domain_url_dicts:
					domain_all = domain_url_dicts.keys()
					# 目标站点是否出现
					for domain in domains:
						lock.acquire()
						if domain not in domain_all:
							f.write(f'{kwd}\t无\t无\t{group}\t{domain}\n')
						else:
							# my_url可能为None
							my_url,my_order,tpl = domain_url_dicts[domain]
							f.write(f'{kwd}\t{my_url}\t{my_order}\t{group}\t{domain}\t{tpl}\n')
						f.flush()
						lock.release()
			finally:
				del group_kwd, kwd, group
				gc.collect()
				q.task_done()


if __name__ == "__main__":
	OneHandle_UrlNum = 1 # 计数1个标签打开几个网页(防止浏览器崩溃)
	local_time = time.localtime()
	today = time.strftime('%Y%m%d', local_time)
	list_ua = [i.strip() for i in open('ua_pc.txt', 'r', encoding='utf-8')]
	domains = ['5i5j.com', 'lianjia.com', 'anjuke.com', 'fang.com','ke.com']  # 目标域名
	my_domain = '5i5j.com'
	chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
	chromedriver_path = 'D:/install/pyhon36/chromedriver.exe'
	ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
	driver = get_driver(chrome_path,chromedriver_path,ua)
	webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
	print(f'webdriver+chrome的pid:{webdriver_chrome_ids}')
	q, group_list = bdpcIndexMonitor.read_excel('城市大词+竞价转化词_city.xlsx')  # 关键词队列及分类
	all_num = q.qsize()  # 总词数
	f = open(f'{today}bdpc1_index_info.txt', 'w+', encoding="utf-8")
	f_all = open(f'{today}bdpc1_index_all.txt', 'w+', encoding="utf-8")
	file_path = f.name
	lock = threading.Lock()
	# 设置线程数
	for i in list(range(1)):
		t = bdpcIndexMonitor()
		t.setDaemon(True)
		t.start()
	q.join()
	f.close()
	f_all.close()
	
	# 统计查询成功的词数
	with open(file_path, 'r', encoding='utf-8') as fp:
		success = int(sum(1 for x in fp) / len(domains))
	end = time.time()
	print(f'end...查询成功{success}个')
