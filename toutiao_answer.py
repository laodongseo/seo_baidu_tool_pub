"""
读取excel中的url(so.toutiao.com)
采集头条的回答
"""

#‐*‐coding:utf‐8‐*‐
import requests
import threading
import queue,re,json
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


# 设置允许弹窗
js_allow_pop = """
document.querySelector("body > settings-ui").shadowRoot.querySelector("#main").shadowRoot.querySelector("settings-basic-page").shadowRoot.querySelector("#basicPage > settings-section.expanded > settings-privacy-page").shadowRoot.querySelector("#pages > settings-subpage.iron-selected > settings-category-default-radio-group").shadowRoot.querySelector("#enabledRadioOption").shadowRoot.querySelector("#button > div.disc").click()
""".strip()
url_pop = 'chrome://settings/content/popups'


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

def get_driver(chrome_path,chromedriver_path,ua):
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
	option.add_argument("--disable-blink-features")
	option.add_argument("--disable-blink-features=AutomationControlled")
	driver = webdriver.Chrome(options=option,executable_path=chromedriver_path)
	driver = set_driver(driver)
	return driver


def close_handle(driver):
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
		bool_con = df['url'].str.contains(r'so.toutiao.com')
		print('so.toutiao.com:',bool_con.sum())
		for index,row in df[bool_con].iterrows():
			q.put(row)
		return q


# 获取源码
def get_html(driver,url):
	global OneHandle_UseNum
	if OneHandle_UseNum > OneHandle_MaxNum:
		driver.execute_script("window.open('')")
		time.sleep(1)
		close_handle(driver)
	driver.get(url)
	OneHandle_UseNum += 1
	try:
		WebDriverWait(driver,10,0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "s-container")))
	except Exception as e:
		traceback.print_exc()
	else:
		return driver.page_source


def parse(html):
	line_list = []
	doc = pq(str(html))
	title = doc('title').text()
	if '大家都在问' in title:
		text_str = doc('script[data-for=s-spa-card-json]').text()
		dict_content = json.loads(text_str)
		answer_list = dict_content['data']['question_details']['data']['answers']
		for answer_dict in answer_list:
			an_author = answer_dict['uname']
			an_time = answer_dict['update_time']
			an_html = answer_dict['content']
			an_html = f'<add_html>{an_html}</add_html>' # 防止只有1个p标签,find方法返回空
			doc_answer = pq(str(an_html))
			p_list = doc_answer.find('p').items()
			texts = [f'<p>　　{p.text().strip()}</p>' for p in p_list if p.text().strip()]
			text_html = ''.join(texts)
			answer_len = len(text_html)
			line_list.append([an_author,an_time,text_html,answer_len])
	return line_list


# 线程函数 
def main():
	global IsHeader
	driver = get_driver(ChromePath,ChromeDriver_path,UA)
	while 1:
		row = q.get()
		url = row['url']
		print(url)
		try:
			html = get_html(driver,url)
			line_list = parse(html)
		except Exception as e:
			traceback.print_exc()
			print('出错:',url)
			print(html,file=open('error.txt','a+',encoding='utf-8'))
			time.sleep(60)
		else:
			if isinstance(line_list,list):
				for elements in line_list:
					row['回答人'] ,row['回答时间'],row['答案html'],row['文章长度'] = elements
					df = row.to_frame().T
					with lock:
						if IsHeader == 0:
							df.to_csv(CsvFile,encoding='utf-8-sig',mode='w+',index=False)
							IsHeader = 1
						else:
							df.to_csv(CsvFile,encoding='utf-8-sig',mode='a+',index=False,header=False)
		finally:
			q.task_done()
			time.sleep(0.2)


if __name__ == "__main__":
	OneHandle_UseNum,OneHandle_MaxNum = 1,1 # 计数1个handle打开网页次数(防止浏览器崩溃)
	ChromePath = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
	ChromeDriver_path = 'D:/install/pyhon36/chromedriver.exe'
	UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
	q = read_excel('toutiao_serpUrl_res-vrrw.net.xlsx')
	CsvFile = 'toutiao_answer_res.csv'
	IsHeader =0
	lock = threading.Lock()

	# 设置线程数
	for i in list(range(6)):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()
