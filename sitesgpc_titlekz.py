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
from urllib import request
from http import cookiejar

#设置忽略SSL验证
ssl._create_default_https_context = ssl._create_unverified_context




def get_html(url,retry=1):
	UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0'
	cookie = cookiejar.CookieJar()
	handler = request.HTTPCookieProcessor(cookie)
	opener = request.build_opener(handler)
	opener.addheaders=[('User-Agent',UA)]
	response = opener.open('https://www.sogou.com')
	cookie_result = ""
	for item in cookie:
		cookie_result = cookie_result + item.name + "=" + item.value + ";"
	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'User-Agent': UA,
		'Cookie': cookie_result
	}
	try:
		r = requests.get(url,headers=headers)
	except Exception as e:
		traceback.print_exc()
		time.sleep(30)
		if retry > 0:
			get_html(url,retry-1)
	else:
		return r.text


def parse_html(html,domain):
	serp_dicts = []
	doc = pq(html)
	serp_str = doc('p.num-tips').text().strip()
	gb = re.search(r'.*约(.*?)条.*',serp_str,re.S|re.I)
	serp_num = gb.group(1) if gb else ''
	serp_num = serp_num.replace(',','')

	div_objs = doc('div.vrwrap').items()
	for div_obj in div_objs:
		if div_obj('h3.site-tit'):
			continue
		dict_item = {}
		title = div_obj('h3 a').text().strip()
		time_str = div_obj('span.cite-date').text().strip()
		time_str = re.sub(r'^\s*-\s+','',time_str)
		dict_item['domain'] = domain
		dict_item['收录数'] = serp_num
		dict_item['title'] = title
		dict_item['快照时间'] = time_str
		serp_dicts.append(dict_item)
	return serp_dicts


def main():
	global IsHeader
	while True:
		domain = q.get()
		url = f'https://www.sogou.com/sogou?ie=utf8&query=site:{domain}'
		html = get_html(url)
		titleObj = re.search('<title>(.*?)</title>',html,re.S|re.I)
		title = titleObj.group(1)
		if domain not in title:
			print('sleep 60 s',title)
			file=open('111.txt',encoding='utf-8',mode='w')
			file.write(html)
			file.flush()
			time.sleep(30)
		try:
			serp_dicts = parse_html(html,domain)
		except Exception as e:
			traceback.print_exc()
		else:
			if isinstance(serp_dicts,list):
				with lock:
					print(serp_dicts)
					df = pd.DataFrame(serp_dicts)
					if IsHeader == 0:
						df.to_csv(CsvFile,encoding='utf-8-sig',mode='w+',index=False)
						IsHeader = 1
					else:
						df.to_csv(CsvFile,encoding='utf-8-sig',mode='a+',index=False,header=False)
		finally:
			q.task_done()
			time.sleep(3)


if __name__ == "__main__":
	CsvFile = f'sgpc_titlekz.csv'
	IsHeader =0
	q = queue.Queue()
	lock = threading.Lock()
	for i in open('domains.txt','r',encoding='utf-8'):
		i = i.strip()
		q.put(i)

	for i in range(2):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()

	print('end...')
