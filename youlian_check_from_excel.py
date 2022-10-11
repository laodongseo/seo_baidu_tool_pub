# ‐*‐ coding: utf‐8 ‐*‐
"""
读取excel文件
检查对方网站是否有本站链接
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import gc
import re
import random
from urllib.parse import urlparse
import pandas as pd
import traceback
import cchardet


class Spider_Content(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	@staticmethod
	def read(filepath):
		q = queue.Queue()
		for index,row in pd.read_excel(filepath).iterrows():
			q.put(row)
		return q


	# 获取源码
	def get_html(self, url, retry=0):
		try:
			r = requests.get(url=url, headers=user_agent,timeout=20)
		except Exception as e:
			print('获取源码失败', url, e)
			time.sleep(3)
			if retry > 0:
				self.get_html(url, retry - 1)
		else:
			bin_html = r.content
			encoding = cchardet.detect(bin_html)['encoding']
			html = bin_html.decode(encoding,errors='ignore')
			return html


	def parse(self, html):
		if MyDomain in html:
			a_list = pq('a').items()
			for a in a_list:
				url  = a.attr('href')
				text = a.text().strip()
				if '5i5j.com' in str(url):
					return text,url
		else:
			return 0


	def run(self):
		while 1:
			row = q.get()
			link = row['网址']
			print(link)
			try:
				html = self.get_html(link)
				if not html:
					f.write(f'{str_values}\t查询失败\n')
					continue
				res_status = self.parse(html)
			except Exception as e:
				traceback.print_exc()
			else:
				str_values = '\t'.join(row.to_list())
				with lock:
					if res_status == 0:
						f.write(f'{str_values}\t被下链\n')
					else:
						text,url = res_status if res_status else (None,None)
						f.write(f'{str_values}\t{text}\t{url}\n')
				f.flush()
			finally:
				q.task_done()
				gc.collect()
				time.sleep(0.2)


if __name__ == "__main__":
	MyDomain = '5i5j.com'
	f = open('youlian_check_res.txt','w',encoding='utf-8')
	user_agent = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding':'deflate',
'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,pt;q=0.5',
'Cache-Control':'no-cache',
'Pragma':'no-cache',
'Proxy-Connection':'keep-alive',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29',
		}
	q = Spider_Content.read('友情链接-在线.xlsx')
	lock = threading.Lock()

	# 设置线程数
	for i in list(range(4)):
		t = Spider_Content()
		t.setDaemon(True)
		t.start()
	q.join()
	f.flush()
	f.close()
