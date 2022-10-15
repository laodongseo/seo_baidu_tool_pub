# ‐*‐ coding: utf‐8 ‐*‐
import requests
import time
import pandas as pd
import traceback
import urllib
"""
多域名推送
excel每个sheet的表头：url token   domain
支持多个sheet
"""


# 获取源码
def get_html(url,retry=1):
	my_header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42'}
	try:
		r = requests.get(url=url,headers=my_header, timeout=10)
	except requests.exceptions.RequestException as e: # 或者 except Exception as e:
		print('请求源码失败', url, e)
		time.sleep(10)
		if retry > 0:
			get_html(url, retry - 1)
	else:
		html = r.text
		return html


# all_urls二维列表,每个元素为2000url
def push_url(all_urls,retry=1):
	if  all_urls == []:
		return '下一个'
	post_url = f'http://data.zz.baidu.com/urls?site=www.flashthai.com&token=tfkrX8WWhCT0WGCW'
	print(post_url)
	for data_urls in all_urls:
		try:
			str_urls = '\n'.join(data_urls)
			str_urls = str_urls.encode('utf-8') # 防止中文url报错
			r = requests.post(post_url,data=str_urls,headers=user_agent,timeout=10)
		except Exception as e:
			print('请求失败,暂停15秒')
			traceback.print_exc()
			time.sleep(15)
			if retry > 0:
				push_url(all_urls,retry-1)
		else:
			html = r.json()
			status = r.status_code
			if status == 200:
				if html['success'] > 0:
					print('提交')
				else:
					print('推送数据为0,请检查配置')
					return '下一个'
			else:
				print(html)
				return '下一个'



# 读取excel,每个sheet化成二维列表
def main_func(sitemap_txturl):
			html = get_html(sitemap_txturl)
			urls = [i.strip() for i in html.split('\n') if i.strip()]
			if len(urls) >1999:
				list_format = [urls[i:i + 2000] for i in range(0, len(urls), 2000)]
			else:
				list_format = [urls]  # 如果连接数量 <2000则取全部连接
			# 死循环每个域名把配额用到无法接收单次的推送量
			post_num = 0
			while 1:
				res = push_url(list_format)
				time.sleep(1)
				post_num+=1
				print(post_num,'次')
				if '下一个' == res:
					break


if __name__ == "__main__":
	f = open('push_fail.txt','w',encoding='utf-8') # 推送失败的url
	user_agent = {
		'User - Agent':'curl / 7.12.1',
		'Host':'data.zz.baidu.com',
		'Content - Type':'text/plain',
		'Content - Length':'83'
	}

	main_func('http://www.flashthai.com/sitemap.txt')
	
	f.close()

