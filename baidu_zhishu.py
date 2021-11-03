# ‐*‐ coding: utf‐8 ‐*‐
"""
百度指数查询(pc指数及m指数)
http://index.baidu.com/api/SearchApi/index?area=0&word=[[{"name":"安华里","wordType":1}]]&days=30
excel每个sheet第1列放关键词,sheet名是类别
"""

import requests
from pyquery import PyQuery as pq
import random
import threading
import queue
import time
import gc
from openpyxl import load_workbook
from openpyxl import Workbook
import traceback
import threading
import pandas as pd

cookie1 = ' BIDUPSID=95E739A8EE050812705C1FDE2584A61E; PSTM=1563865961; BDUSS=Dk4ZVBCcWN3aVA1LUF-TlRrYTYxczR1TnFwSWtncVZzdzBUMkRpM2p-QTd2dlZlRVFBQUFBJCQAAAAAAAAAAAEAAADag5oxzI2IkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADsxzl47Mc5ed; BDUSS_BFESS=Dk4ZVBCcWN3aVA1LUF-TlRrYTYxczR1TnFwSWtncVZzdzBUMkRpM2p-QTd2dlZlRVFBQUFBJCQAAAAAAAAAAAEAAADag5oxzI2IkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADsxzl47Mc5ed; BAIDUID=E0D57438CE93313860A15516D710752C:SL=0:NR=10:FG=1; __yjs_duid=1_5ae4d8f5d697df213487ed86b671c45d1619745523512; H_WISE_SIDS=110085_114550_127969_169771_171234_173017_173293_174661_174666_175408_175584_175609_175653_175729_175755_175812_176157_176342_176346_176588_176615_176678_176766_176996_177018_177225_177317_177371_177378_177410_177520_177561_177563_177565_177630_177726_177748_177786_178003_178073_178327_178384_178398_8000060_8000117_8000120_8000138_8000149_8000163_8000172_8000177_8000179; BAIDUID_BFESS=9A755B15A74479CFABD57920BBD1A235:FG=1; bdindexid=rv6aop0qd747epr7edvqg5dh92; BDRCVFR[ZBpA1to4Avs]=9xWipS8B-FspA7EnHc1QhPEUf; delPer=0; PSINO=7; H_PS_PSSID=31660_26350; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1629714251,1630057957,1630318117,1630395314; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1630395322; ab_sr=1.0.1_YzhiZGExN2IwYzI0ZmU5YzUyMjQwOWY4MzQ0MTBiMDgyYjFhZmQ2ZThkZDQ3NzYyODYzMjYwMmQyNjQzZGI5NzJlMWU5MDRjMjAyZjI0NDJlODU3M2U1MWRlODM5OTMyZGViODIzMzIyY2EwYTU4MTg0ODNiMTA0NjBlYTY2YmVhODI0ZWVmODA3YzM3ZTRmNWJhNjZlZTE0ZjVkYWI2Yw==; __yjs_st=2_MWViODY2NTU0ZDRkZDdhMjFmM2M1ZWRhYjFkZmViYmIwY2Y5NDc3ZGRhZDgwNjY0MWI3YTU5MTI3YWYyOTA2MTk4YmJlNjViNjRiOTliYTNlNGJiNWU4Njc3YTgyYjc3NzIzZDIzMDBmMzczOTQ3ZWVkOGEyNzEwNTdiMWY3MGRjZWE5MGVmODNmMjM1Yjg5MTliODg4NDc2YTM0ZmQwNGY1YTI5NzkzZTljZTIyNGNkZGQzNGYzZDI5YTQzNzk2NjgyZmVkMmRiOWQxZmVjM2M2MDRmOWNmM2NlZWFmMTg3YTBlOGQ5YmFjMmY1ZWU3ZDcwMWFkNzVkMTc2YzZiN183XzdhYWUxMjEy; RT="z=1&dm=baidu.com&si=ketw8nnzvia&ss=kszr9vm6&sl=5&tt=2oa&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=ygm"'.strip()

# 读取文件获取关键词类别
def read_excel(filepath):
	q = queue.Queue()
	df = pd.read_excel(filepath)
	for index,row in df.iterrows():
		q.put(row)
	return q


def get_header():
	my_header = {
		'Accept':'application/json,text/plain,*/*',
		'Accept-Encoding':'deflate',
		'Accept-Language':'zh-CN,zh;q=0.9',
		'Connection':'keep-alive',
		'Cookie':cookie1,
		'Host':'index.baidu.com',
		'Referer':'http://index.baidu.com/v2/main/index.html',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0',
		}
	return my_header


# 获取源码
def get_html(url,retry=1):
	my_header = get_header()
	try:
		r = requests.get(url=url,headers=my_header,timeout=20)
	except Exception as e:
		print('获取源码失败',e)
		time.sleep(180)
		if retry > 0:
			get_html(url,retry-1)
	else:
		html = r.json()  # 用r.text有时候识别错误
		return html


# 解析数据
def parse_html(html):
	if html and 'status' in html:
		if html['status']==0:
			try:
				dic_data = html['data']['generalRatio'][0]
				print(dic_data)
				all_ = dic_data['all']['avg']
				pc = dic_data['pc']['avg']
				mo = dic_data['wise']['avg']
			except Exception as e:
				print('parse_html..',e)
			else:
				return all_,pc,mo
		if html['status'] == 10002:
			return ['无','无','无']
	else:
		print('sleep 30s,检查数据..',html)
		time.sleep(30)


def main():
	while True:
		row = q.get()
		print(row)
		kwd,city = row['kwd'],row['city']
		req_url = f'https://index.baidu.com/api/SearchApi/index?area=0&word=[[{{"name":"{kwd}","wordType":1}}]]&startDate=2021-07-28&endDate=2021-08-26'
		print(req_url)
		try:
			html = get_html(req_url)
			if not html:
				q.put([city,kwd])
				time.sleep(200)
				continue
			values = parse_html(html)
			if not values:
				q.put([city,kwd])
				continue
		except Exception as e:
			traceback.print_exc(file=open('log.txt', 'w'))
			print('main func',e)
		else:
			values = values if values else ['异常','异常','异常']
			values = [str(i) for i in values]
			values = '\t'.join(values)
			f.write(f'{kwd}\t{values}\t{city}\n')
			f.flush()
		finally:
			q.task_done()
			time.sleep(1.5)
		


if __name__ == "__main__":
	start = time.time()
	local_time = time.localtime()
	today = time.strftime('%Y%m%d', local_time)
	headers = list_headers = [i.strip() for i in open('headers.txt', 'r', encoding='utf-8')]
	excel_path = 'kwd.xlsx'
	q = read_excel(excel_path)
	f = open(f'{today}kwd_zhishu.txt','w',encoding='utf-8')
	# 设置线程数
	for i in list(range(1)):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()
	f.close()
	end = time.time()
	print((end - start)/60,'min')
