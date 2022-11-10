# -*- coding: utf-8 -*-
"""
Description: 百度搜索结果爬虫
Author: brooks
Date: 2022/10/26
"""
from random import choice, randint
from urllib.parse import quote
from threading import Thread
from queue import Queue
from pyquery import PyQuery as pq
import requests
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

RSV_T = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'
RSV_PQ = '123456789abcdef'


def fetch(word):
	rsv_t = ''.join(choice(RSV_T) for _ in range(60))
	rsv_pq = ''.join([choice(RSV_PQ) for _ in range(8)] + list('000') + [choice(RSV_PQ) for _ in range(5)])
	url = f"https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd={quote(word)}&oq={quote(word)}&rsv_pq={rsv_pq}&rsv_t={quote(rsv_t)}&rqlang=cn&rsv_enter=0&rsv_dl=tb&rsv_btype=t&rsv_sug3=1&rsv_sug1=1&rsv_sug7=100&prefixsug={quote(quote(word))}&rsp=8&rsv_sug4={randint(3000,6000)}&inputT={randint(1000,3000)}"
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
	try:
		r = requests.get(url, headers=headers, timeout=5)
	except requests.exceptions.Timeout:
		return fetch(word)
	except requests.exceptions.RequestException:
		return
	r.encoding = 'utf-8'
	return r.text


def parse_response(source):
	doc = pq(source)
	list_item = doc.find('#rs_new td a')
	relate_word = []
	for item in list_item:
		relate_word.append(item.text.strip())
	# 大家还在搜
	other_search = doc.find('#content_left>.result-op div.list_1V4Yg a.item_3WKCf')
	for item in other_search:
		relate_word.append(item.text.strip())
	return relate_word


class BaiduSpider(Thread):
	def __init__(self, queue: Queue, writer):
		super().__init__()
		self.queue = queue
		self.writer = writer
	
	def run(self):
		while True:
			try:
				word = self.queue.get()
				source = fetch(word)
				if source is None:
					self.queue.put(word)
					continue
				relates = parse_response(source)
				print(f'{word} found {len(relates)}')
				for item in relates:
					self.writer.write(f'{item}\n')
					self.writer.flush()
			finally:
				self.queue.task_done()


if __name__ == '__main__':
	word_queue = Queue()
	with open('keywords.txt', encoding='utf-8') as f:
		for line in f:
			word_queue.put(line.strip())
	
	result = open('result.txt', 'w', encoding = 'utf-8')
	start = time.time()
	for _ in range(50):
		t = BaiduSpider(word_queue, result)
		t.daemon = True
		t.start()
	
	word_queue.join()
	result.close()
	print(f'done! comsume {time.time() - start:.2f} seconds')
