# -*- coding: utf-8 -*-
"""
查询搜狗转码地址的title
"""

import requests,time,re
from pyquery import PyQuery as pq
import queue
import threading
import traceback   
import ssl

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
		r = requests.get('https://m.sogou.com/')
	except Exception as e:
		traceback.print_exc()
		time.sleep(20)
		if retry > 0:
			init_cookie(retry-1)
	else:
		cookjar.update(r.cookies)
	finally:
		return cookjar


def get_html(url,retry=1):
	try:
		r = requests.get(url,headers=headers,cookies=CookJarObj,timeout=30)
	except Exception as e:
		traceback.print_exc()
		time.sleep(20)
		if retry > 0:
			get_html(url,retry-1)
	else:
		CookJarObj.update(r.cookies)
		return r.text


def main():
	while True:
		domain = q.get()
		url = f'http://wap.sogou.com/ntcweb?icfa=1301083&page=1&from=newsretry&g_ut=3&url=http://{domain}'
		try:
			html = get_html(url)
			if not html:
				title = '查询失败'
				CookJarObj = init_cookie()
				print('sleep....20')
				time.sleep(20)
			else:
				titleObj = re.search('<title>(.*?)</title>',html,re.S|re.I)
				title = titleObj.group(1)  if titleObj else '.....请手动检查.....'
		except Exception as e:
			traceback.print_exc()
		else:
			print(domain,title)
			with lock:
					print(f'{domain}\t{title}',file=file) if '您访问的页面为第三方网站' in title else True
					file.flush()
		finally:
			q.task_done()
			time.sleep(0.2)


if __name__ == "__main__":
	CookJarObj = init_cookie()
	q = queue.Queue()
	lock = threading.Lock()
	file=open('sgmo_zhuanma_title.txt',encoding='utf-8',mode='w+')
	for i in open('domains.txt','r',encoding='utf-8'):
		i = i.strip()
		q.put(i)

	for i in range(3):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()

	print('end...')
