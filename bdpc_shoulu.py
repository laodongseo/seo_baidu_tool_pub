# ‐*‐ coding: utf‐8 ‐*‐
"""
博客:www.python66.com
查询【自然排名的】url是否收录
pc_url.txt,一行一个url,必须带http或https
区分https或者http
区分https://aaa/bbb和https://aaa/bbb/
线程数默认是1,可自行设置
(链接a定向到了b,有时搜索a显示收录,但实际是b,此时脚本判断a为未收录)
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import gc
import random
import traceback
import re
from urllib.parse import quote


RSV_T = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'
RSV_PQ = '123456789abcdef'

def get_header():
	headers = {
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"Accept-Encoding": "gzip, deflate",
		"Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
		"Cache-Control": "no-cache",
		"Connection": "keep-alive",
		"Cookie": "BIDUPSID=E4EBDADA6EABBA7D547D787F442C64F3; PSTM=1666744901; BAIDUID=E4EBDADA6EABBA7D2F1DAADB50B6B439:FG=1; BD_UPN=123253; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDUSS=d6dU82ZmhEZkdQYXduY2QzeXo2YTVoNzVqZ0o2ek1nTlNyNXJrSUE1a2dWWUJqSUFBQUFBJCQAAAAAAAAAAAEAAACmAH90zeLDstCtu-HBqrrPyMsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDIWGMgyFhjM3; BDUSS_BFESS=d6dU82ZmhEZkdQYXduY2QzeXo2YTVoNzVqZ0o2ek1nTlNyNXJrSUE1a2dWWUJqSUFBQUFBJCQAAAAAAAAAAAEAAACmAH90zeLDstCtu-HBqrrPyMsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDIWGMgyFhjM3; BAIDUID_BFESS=E4EBDADA6EABBA7D2F1DAADB50B6B439:FG=1; channel=baidusearch; ab_sr=1.0.1_NmRiZThjNTcyMTVjOTcyZDgxNzM4ZGIxNjdlMDIxOTc3YzY3NTQ1YmQ5NGIzYTk5MGQxNDA3OTJkM2NiMGJlOGYwYWViZGEyMTgxODI2ZTcxYTZmYmNiMDFlMTM5ZmZiZTY2MjJlNDEzZGFiMTA4YTcyNDk4OWUxMDVhMjAzOTc5ODkxOTg1NmZhZmZkZmQ5ZDAzZDY4YWZhMzMxNzVjY2YxNTdiNzdmMzViODY2NmUyYWFjOTAxY2Y0ZTA5MmY5; BD_HOME=1; BD_CK_SAM=1; PSINO=6; sugstore=0; BA_HECTOR=00a185248101a0048h8h0fk31hlhn7b1b; ZFY=6Uz9JVPmW1RvzbKEqEn1FgPIZ8nXbq2AuV26bx4n2EI:C; COOKIE_SESSION=9_0_6_6_1_11_0_0_5_7_2_0_0_0_0_0_1666764414_0_1666768611%7C9%230_0_1666768611%7C1; delPer=1; H_PS_PSSID=36548_37551_37355_37491_36885_36789_37533_37499_26350_37478_37452; H_PS_645EC=6e93SUzO%2FZ5xyMLfwspagSoXjf6tEwaZmykQfDLIGdmVYRrtDIZUfyfnwcg; baikeVisitId=5f6dff23-0c77-4aae-9d0b-fc663b372d90; BDSVRTM=218",
		"Host": "www.baidu.com",
		"Pragma": "no-cache",
		"Referer": "https://www.baidu.com/",
		"sec-ch-ua": "\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"",
		"sec-ch-ua-mobile": "?0",
		"sec-ch-ua-platform": "\"macOS\"",
		"Sec-Fetch-Dest": "document",
		"Sec-Fetch-Mode": "navigate",
		"Sec-Fetch-Site": "same-origin",
		"Sec-Fetch-User": "?1",
		"Upgrade-Insecure-Requests": "1",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
	}
	return headers


class BdpcShoulu(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)

	# 读取txt文件 获取待查询url
	@staticmethod
	def read_txt(filepath):
		q = queue.Queue()
		for url in open(filepath, encoding='utf-8'):
			url = url.strip()
			q.put(url)
		return q


	# 获取serp源码
	def get_html(self,url,my_header,retry=1):
		try:
			r = requests.get(url=url,headers=my_header,timeout=20)
		except Exception as e:
			print('获取源码失败',e)
			time.sleep(20)
			if retry > 0:
				self.get_html(url,retry-1)
		else:
			html = r.content.decode('utf-8',errors='ignore')
			url = r.url  # 反爬会重定向,取验证码页面地址
			return html,url


	# 获取自然排名的加密url
	def get_encrpt_urls(self,html,url):
		encrypt_url_list = []
		doc = pq(html)
		title = doc('title').text()
		a_list = doc('h3.t a').items()
		for a in a_list:
			encrypt_url = a.attr('href')
			if encrypt_url.find('http://www.baidu.com/link?url=') == 0:
				encrypt_url_list.append(encrypt_url)
		return encrypt_url_list


	# 解密某条加密url
	def decrypt_url(self,encrypt_url,my_header,retry=1):
		try:
			encrypt_url = encrypt_url.replace('http://','https://')
			r = requests.head(encrypt_url,headers=my_header,timeout=10)
		except Exception as e:
			print(encrypt_url,'解密失败',e)
			time.sleep(6)
			if retry > 0:
				self.decrypt_url(encrypt_url,retry-1)
		else:
			real_url = r.headers['Location']
			return real_url


	# 获取结果页真实url
	def get_real_urls(self, encrypt_url_list,my_header):
		if encrypt_url_list:
			real_url_list = [self.decrypt_url(encrypt_url,my_header) for encrypt_url in encrypt_url_list]
			return real_url_list
		else:
			return []


	# 线程函数
	def run(self):
		global shoulu_num,check_num
		while 1:
			target_url = q.get()
			print(target_url)
			rsv_t = ''.join(random.choice(RSV_T) for _ in range(60))
			rsv_pq = ''.join([random.choice(RSV_PQ) for _ in range(8)] + list('000') + [random.choice(RSV_PQ) for _ in range(5)])
			rand_time = random.randint(3000,6000)
			url = f"https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd={quote(target_url)}&oq={quote(target_url)}&rsv_pq={rsv_pq}&rsv_t={quote(rsv_t)}&rqlang=cn&rsv_enter=0&rsv_dl=tb&rsv_btype=t&rsv_sug3=1&rsv_sug1=1&rsv_sug7=100&prefixsug={quote(quote(target_url))}&rsp=8&rsv_sug4={rand_time}&inputT={rand_time}"
			my_header = get_header()
			try:
				html_now_url = self.get_html(url,my_header)
				html,now_url = html_now_url if html_now_url else ('','')
				title_re = re.search('<title>(.*?)</title>',html,re.S|re.I)
				title = title_re.group() if title_re else ''
				if '_百度搜索' not in title or 'https://www.baidu.com/s?ie=utf-8' not in now_url:
					q.put(target_url)
					print(f'暂停30 s,非正常页:{title},{now_url}')
					time.sleep(30)
					continue
				encrypt_url_list = self.get_encrpt_urls(html,now_url)
			except Exception as e:
				traceback.print_exc()
			else:
				if not encrypt_url_list:
					real_urls = []
				else:
					real_urls = self.get_real_urls(encrypt_url_list,my_header)
				# 防止多线程写入文件错乱
				lock.acquire()
				check_num += 1
				if target_url in real_urls:
					shoulu_num += 1
					f.write(f'{target_url}\t收录\n')
				else:
					f.write(f'{target_url}\t未收录\n')
				lock.release()
			finally:
				f.flush()
				del target_url
				gc.collect()
				q.task_done()
				# time.sleep(2)


if __name__ == "__main__":

	start = time.time()
	check_num,shoulu_num = 0,0
	lock = threading.Lock() # 锁
	q = BdpcShoulu.read_txt('url.txt') # url队列
	f = open('pc_shoulu.txt','w+',encoding='utf-8')
	# 设置线程数
	for i in list(range(10)):
		t = BdpcShoulu()
		t.setDaemon(True)
		t.start()
	q.join()
	f.flush()
	f.close()
	end = time.time()
	spent_time = (end - start) / 60
	print(f'耗时{spent_time}min,成功查询{check_num},收录{shoulu_num}个')
