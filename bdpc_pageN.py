# ‐*‐ coding: utf‐8 ‐*‐
"""
记录每个词前N的title、链接、排名位置
可以自由配置前几页
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
from urllib.parse import urlparse
import time
import gc
import random
from random import choice
from urllib.parse import quote
requests.packages.urllib3.disable_warnings()



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

class bdpcCoverPage5(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)

	@staticmethod
	def read_excel(filepath):
		q = queue.Queue()
		for kwd in open(filepath,'r',encoding='utf-8'):
			kwd = kwd.strip()
			if kwd:
				q.put(kwd)
		return q


	# 获取某词serp源码
	def get_html(self,url,retry=1):
		my_header = get_header()
		try:
			r = requests.get(url=url,headers=my_header,timeout=10)
		except Exception as e:
			print('获取源码失败',e)
			time.sleep(20)
			if retry > 0:
				self.get_html(url,retry-1)
		else:
			html = r.content.decode('utf-8',errors='ignore')  # 用r.text有时候识别错误
			url = r.url  # 反爬会重定向,取定向后的地址
			return html,url


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
				a = div('h3 a')
				if not a: # 空对象pyquery.pyquery.PyQuery 为假
					a = div('.c-result-content article section a')
				encrypt_url = a.attr('href')
				title = a.text().strip().replace('\n','')
				encrypt_url_list.append((encrypt_url, title,rank))
			for div in div_op_list:
				rank_op = div.attr('id') if div.attr('id') else 'id_xxx'
				link = div.attr('mu')  # 有些op样式没有mu属性
				if link:
					title = div('h3 a').text().strip().replace('\n','')
					real_urls.append((link, title,rank_op))
				else:
					a = div('article a')
					if a:
						encrypt_url = a.attr('href')
						title = a.text().strip().replace('\n','')
						real_urls.append((encrypt_url, title,rank_op))

		else:
			print('源码异常,可能反爬,暂停60 s', title)
			time.sleep(60)

		return encrypt_url_list, real_urls


	# 解密某条加密url
	def decrypt_url(self, encrypt_url, retry=1):
		if encrypt_url:
			my_header = get_header()
			try:
				encrypt_url = encrypt_url.replace('http://', 'https://') if 'https://' not in encrypt_url else encrypt_url
				r = requests.head(encrypt_url, headers=my_header,timeout=60)
			except Exception as e:
				print(encrypt_url, '解密失败,暂停45 s', e)
				time.sleep(45)
				if retry > 0:
					self.decrypt_url(encrypt_url, retry - 1)
			else:
				real_url = r.headers['Location'] if 'Location' in r.headers else None
				return real_url


	# 获取某词serp源码首页排名真实url
	def get_real_urls(self, encrypt_urls_rank):
		real_urls_rank = [(self.decrypt_url(encrypt_url),title,rank) for encrypt_url,title,rank in encrypt_urls_rank]
		return real_urls_rank


	# 线程函数
	def run(self):
		while 1:
			kwd = q.get()
			print(kwd)
			for page,page_num in page_dict.items():
				if page == '首页':
					rsv_t = ''.join(choice(RSV_T) for _ in range(60))
					rsv_pq = ''.join([choice(RSV_PQ) for _ in range(8)] + list('000') + [choice(RSV_PQ) for _ in range(5)])
					rand_time = random.randint(3000,6000)
					url = f"https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd={quote(kwd)}&oq={quote(kwd)}&rsv_pq={rsv_pq}&rsv_t={quote(rsv_t)}&rqlang=cn&rsv_enter=0&rsv_dl=tb&rsv_btype=t&rsv_sug3=1&rsv_sug1=1&rsv_sug7=100&prefixsug={quote(quote(kwd))}&rsp=8&rsv_sug4={rand_time}&inputT={rand_time}"

				else:
					rsv_t = ''.join(choice(RSV_T) for _ in range(60))
					rsv_pq = ''.join([choice(RSV_PQ) for _ in range(8)] + list('000') + [choice(RSV_PQ) for _ in range(5)])
					rand_time = random.randint(3000,6000)
					url = f"https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd={quote(kwd)}&oq={quote(kwd)}&rsv_pq={rsv_pq}&rsv_t={quote(rsv_t)}&rqlang=cn&rsv_enter=0&rsv_dl=tb&rsv_btype=t&rsv_sug3=1&rsv_sug1=1&rsv_sug7=100&prefixsug={quote(quote(kwd))}&rsp=8&rsv_sug4={rand_time}&inputT={rand_time}&pn={page_num}"

				# print(kwd,url)
				html_now_url = self.get_html(url)
				html,now_url = html_now_url if html_now_url else (None,None)
				if not html:
					continue
				encrypt_urls_rank,real_urls_op_rank = self.get_encrpt_urls(html,now_url)
				if encrypt_urls_rank:
					real_urls_rank = self.get_real_urls(encrypt_urls_rank)
					real_urls_rank.extend(real_urls_op_rank)
					for url,title,rank in real_urls_rank:
						lock.acquire()
						f.write(f'{today}\t{kwd}\t{page}\t{title}\t{url}\t{rank}\n')
						lock.release()
			f.flush()
			q.task_done()
			del kwd
			gc.collect()


if __name__ == "__main__":
	start = time.time()
	local_time = time.localtime()
	today = time.strftime('%Y-%m-%d',local_time)
	q = bdpcCoverPage5.read_excel('kwd.txt')  # 关键词队列
	page_dict = {'首页':'','二页':10,'三页':20,'四页':30,'五页':40,'六页':50,'七页':60,'八页':70,'九页':80}  # 查询页码
	lock = threading.Lock()
	f = open(f'./{today}_bdpc1_serp_info.txt','w',encoding="utf-8")
	# 设置线程数
	for i in list(range(4)):
		t = bdpcCoverPage5()
		t.setDaemon(True)
		t.start()
	q.join()
	f.close()
	end = time.time()
	print('耗时{0}min'.format((end - start) / 60))
