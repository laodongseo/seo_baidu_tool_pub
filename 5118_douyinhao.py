# --*--coding: utf-8 --*--
"""
采集5118的抖音号
指定翻页
"""
import pandas as pd
import traceback
from pyquery import PyQuery as pq
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import pandas as pd
import demjson



def set_driver(driver):
	try:
		# 防止反爬
		driver.get('http://www.python66.com/stealth.min.js')
		time.sleep(0.5)
		js_hidden = driver.page_source
		driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
		  "source": js_hidden
		})

		# 设置允许弹窗(headless模式执行失败)
		# driver.get(url_pop)
		# time.sleep(0.5)
		# driver.execute_script(js_allow_pop)
	except Exception as e:
		traceback.print_exc()
	finally:
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


def get_driver(chrome_path,chromedriver_path):
	ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
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
	option.add_argument("--disable-blink-features")
	option.add_argument("--disable-blink-features=AutomationControlled")
	driver = webdriver.Chrome(options=option,executable_path=chromedriver_path)
	driver = set_driver(driver)
	return driver


def login_5118():
	url = 'https://www.5118.com/'
	driver.get(url)
	ele_user = WebDriverWait(driver, 20).until(
		EC.presence_of_element_located((By.CLASS_NAME, "login-dialog-btn"))
	)
	
	while True:
		try:
			name_login = WebDriverWait(driver, 20).until(
				EC.presence_of_element_located((By.CLASS_NAME, "user_img"))
			)
		except Exception as e:
			continue
		else:
			break
	print('login success...')
	time.sleep(2)


# 获取源码
def get_html(url):
	global OneHandle_UseNum
	if OneHandle_UseNum > OneHandle_MaxNum:
		driver.execute_script("window.open('')")
		time.sleep(1)
		close_handle(driver)
	driver.get(url)
	OneHandle_UseNum += 1
	time.sleep(1)
	html = driver.page_source
	return html


def parse_html(html):
	html = pq(html)('pre').text().strip()
	df_page = pd.DataFrame()
	dict_text = demjson.decode(html)
	if dict_text['errorCode'] == 0:
		person_contents = dict_text['data']['result']['hits']
		for person_content in person_contents:
			df_person = pd.DataFrame([person_content])
			df_page = df_page.append(df_person)
	return df_page


def run(url):
	global IsHeader
	html = get_html(url)
	df_page = parse_html(html)
	print(df_page.shape)
	if IsHeader == 0:
		df_page.to_csv(CsvFile,encoding='utf-8-sig',mode='w+',index=False)
		IsHeader = 1
	else:
		df_page.to_csv(CsvFile,encoding='utf-8-sig',mode='a+',index=False,header=False)


if __name__ == '__main__':
	OneHandle_UseNum,OneHandle_MaxNum = 1,1 # 计数1个handle打开网页次数(防止浏览器崩溃)
	ChromePath = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
	ChromeDriver_path = 'D:/install/pyhon36/chromedriver.exe'
	driver = get_driver(ChromePath,ChromeDriver_path)
	login_5118()

	page_num ,max_num = 1 , 22
	kwd_code_dict = {'倪师':('80e5a205',22),'倪海厦':('6a3577d6a205',14),'杏林':('7976f476',100)}
	for name,code_maxnum in kwd_code_dict.items():
		CsvFile = f'5118-douiyin-{name}.csv'
		IsHeader =0
		kwd_code,max_num = code_maxnum
		for i in range(0,max_num *20,20):
			print(i,'-----------')
			url = f'https://yxasync2.5118.com/api/videos/DouyinCodeList?SearchText={kwd_code}&searchType=douyinname&pageIndex={page_num}&sort=&praise=0&comment=0&from={i}&size=12&cateid=-1&video_count=0&video_count_end=999999999&video_count_up=0&fans_count=0&fans_count_end=999999999&fans_count_up=0&following_count=0&following_count_end=999999999&following_count_up=0&like_count=0&like_count_end=999999999&like_count_up=0&source=2'
			run(url)
			time.sleep(1.5)
			page_num+=1
