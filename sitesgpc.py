# -*- coding: utf-8 -*-
"""
查询搜狗pc收录及快照日期
"""

import requests,time,re
from pyquery import PyQuery as pq
import queue
import threading
import traceback   
import ssl
import pandas as pd

#设置忽略SSL验证
ssl._create_default_https_context = ssl._create_unverified_context



headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding': 'deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
	}


def init_cookie(retry=1):
	cookjar = requests.cookies.RequestsCookieJar()
	try:
		r = requests.get('https://www.sogou.com/',headers=headers)
	except Exception as e:
		traceback.print_exc()
		time.sleep(30)
		if retry > 0:
			init_cookie(retry-1)
	else:
		cookjar.update(r.cookies)
	finally:
		return cookjar


def get_html(url,retry=2):
	CookJarObj = init_cookie()
	print(CookJarObj)
	try:
		r = requests.get(url,headers=headers,cookies=CookJarObj)
	except Exception as e:
		traceback.print_exc()
		time.sleep(30)
		if retry > 0:
			get_html(url,retry-1)
	else:
		return r.text


def parse_html(html):
	doc = pq(html)
	serp_str = doc('p.num-tips').text()
	gb = re.search(r'.*约(\d+)条.*',serp_str,re.S|re.I)
	serp_num = gb.group(1) if gb else ''

	spans = doc('div.vrwrap .citeurl span.cite-date').items()
	kuaizhaos = ()
	for span in spans:
		str_info = span.text()
		str_ = re.sub(r'\s+','',str_info)
		kuaizhaos += (str_,)
	row_kuaizhao = '#'.join(set(kuaizhaos))
	return row_kuaizhao,serp_num


def main():
	global IsHeader
	while True:
		domain = q.get()
		url = f'http://www.sogou.com/web?query=site:{domain}'
		html = get_html(url)
		titleObj = re.search('<title>(.*?)</title>',html,re.S|re.I)
		title = titleObj.group(1)
		if domain not in title:
			print('sleep 60 s',title)
			time.sleep(60)
		serp_num = row_kuaizhao = '' # 默认值
		try:
			if isinstance(html,str):
				res_serp = parse_html(html)
				if isinstance(res_serp,tuple):
					row_kuaizhao,serp_num = res_serp
				else:
					print('检查源码')
			else:
				print('检查请求结果')
		except Exception as e:
			traceback.print_exc()
		else:
			with lock:
				print(domain,serp_num,row_kuaizhao)
				df = pd.DataFrame([[domain,serp_num,row_kuaizhao]],columns=['domain','结果数','快照日期'])
				if IsHeader == 0:
					df.to_csv(CsvFile,encoding='utf-8-sig',mode='w+',index=False)
					IsHeader = 1
				else:
					df.to_csv(CsvFile,encoding='utf-8-sig',mode='a+',index=False,header=False)
		finally:
			q.task_done()
			time.sleep(4)


if __name__ == "__main__":
	CsvFile = f'sgpc_kz.csv'
	IsHeader =0
	q = queue.Queue()
	lock = threading.Lock()
	for i in open('domains.txt','r',encoding='utf-8'):
		i = i.strip()
		q.put(i)

	for i in range(1):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()

	print('end...')
