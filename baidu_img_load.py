# ‐*‐ coding: utf‐8 ‐*‐
"""
批量关键词采集百度图片
准备关键词文件kwd.txt
设定每个关键词翻页多少页采集
设定每个翻页展示多少图片
"""
import requests
import threading
import queue
import time
import os
import random
import pandas as pd
import urllib
from urllib.parse import quote
import json
import copy


cookie_str = """
BDqhfp={kwd}; PSTM=1615340407; BIDUPSID=F2515E4F29BB88B255962F2CFE19C3F9; __yjs_duid=1_a1942d4ca1a959bb32e3ffff0cf07ad41617946073654; BAIDUID={uid}:SL=0:NR=10:FG=1; MAWEBCUID=web_HZaROXCyXvOjHUxdDgsRzFWcFvyytfvmhKNANGkMBMqFBkpuhv; H_WISE_SIDS=107311_110085_114550_127969_164870_178384_178640_179379_179432_179623_181588_182233_182273_182290_182530_183030_183330_184012_184319_184736_184794_184891_184894_185268_185632_185652_186015_186318_186595_186716_186844_187067_187087_187173_187201_187292_187347_187433_187449_187669_187726_187815_187819_187929_188031_188182_188296_188332_188425_188553_188614_188733_188741_188787_188843_188994_189150_189269_189325_189391_189414_189680_189703_189712_189731_189755_189757_190033_190110_190133_190209_190248_190473_190499_190518_190605_190652_190684_190794_190944_191067; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSFRCVID_BFESS=00AOJexroG0vzSoHACmSt_0-Q2KK0gOTDYLEOwXPsp3LGJLVgBVNEG0PtsqxpEt-oxrFogKK0mOTHUAF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tJujoDPhtDD3H48k-4QEbbQH-UnLqhDe3eOZ04n-ah02flRzjU7t3q4Q5bPjel_HW20JhCOm3UTdsq76Wh35K5tTQP6rLtbvyRv4KKJxbp75E4ctLt5ibj-bhUJiB5OLBan7-ljIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbC_4D5KWDjjLeU5eetjK2CntsJOOaCvdebvOy4oWK441Dhjr2Rj75HTg_Pb7tT6Ghlvojhu53M04XhO9-hvT-54e2p3FBUQJoMI6Qft20b0gKP5E3foayIIfXn7jWhk2Dq72yhoNQlRX5q79atTMfNTJ-qcH0KQpsIJM5-DWbT8IjHCHt5-jtRCOVbobHJoHjJbGq4bohjP7K4v9BtQO-DOxoPQKtI31qtQt3ROrDKuu0q37hJ5HQgnkQq5vbMnmqPtRXMJkXhKsWMcK0x-jLTPOoJ_K3qIVj4Jd54nJyUnQhtnnBpQC3H8HL4nv2JcJbM5m3x6qLTKkQN3T-PKO5bRu_CF-JK02hDD9eP55q4D_MfOtetJyaR3y5hOvWJ5WqR7jDbj-D5-nKqjhKJ3dtPjIb4JdMtQKShbXKxoc5pkrKp0eWUbZBNcMhn6q3l02V--9D4K-QxcDMl33-tRMW20jWl7mWU5NsxA45J7cM4IseboJLfT-0bc4KKJxbnLWeIJEjjCajTcyjG0eq-jeHDrKBRbaHJOoDDkxDMQcy4LbKxnxJn5ELKO75lOEL-brh56hDxRvD--g3-OkWUQ9babTQ-tbBp3k8MQTLljFQfbQ0hOebRvj36PLW-n-3J7JOpkxhfnxyhLFQRPH-Rv92DQMVU52QqcqEIQHQT3m5-5bbN3ut6T2-DA_oC0atKnP; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03860000133S7UsWX5eZZwrAzq7wn%2FmhhinfYz9vOusdfdm26xli5Xwt4QaFkkmjOCi6fCFCsHuRnA4r9CBbK27IxJOxWM2fy%2F%2FVWR9LK9juBs8Gk6%2BS%2FuAbN3LW43GFyG150Y0HokpzjWW8VDcQvmYKVg3MwJANuRTyBxEP%2F2dAAL2XzTjpCdiVH2YzwJRmTXe8AQOzrKxOBK%2BZfHn%2Fqsd54UmxCvY5uovF55U2ZrVwSgI8xkGJ4Gsx4akgGudF5ruvGWsukt794NaO9bvZEhl94B6dVhpo2EdgKufkIOp8AMKNnu9g9%2Bk1KFDLuKoIIjQ%2Bb%2F3Yzf6sFq6ZqyToNyFN9Eq0r2JpjAOtp8cYZXFa6Lwo%2F10nnuVLHUyzFSyd0En5EJe9qrl07803396710763121672211737350514; delPer=0; PSINO=7; BAIDU_WISE_UID=wapp_1636006738320_864; BDRCVFR[PaHiFN6tims]=9xWipS8B-FspA7EnHc1QhPEUf; BAIDUID_BFESS=DF511E0F6DA7605DB859F0C63ADB0C36:FG=1; BDRCVFR[dG2JNJb_ajR]=mk3SLVN4HKm; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; H_PS_PSSID=31254_26350; BA_HECTOR=8l8h8l0l2k05ak2l241go77o70r; indexPageSugList=%5B%22pip%20install%20opencv-python%22%5D; cleanHistoryStatus=0; userFrom=null; ab_sr=1.0.1_OTk5NjgxOWQwNDdiMWExYTZmMjVhNDhlZTZlZDI4M2VkN2Y0ODkwZjdjMjlkMzlmMjJkMWM3YTBmYzg5NDRmMjI4MDJjYTgxMjIwN2JhYmZlZTQ0MTk2NWUyMjVkODhkYjAzYmY2NWU5NzgzMjlkNjhkMjA1Mzg0YzY0YTY5MTk3MDU0MjUyMGVhNjViMzJmZjU3YzA2YTNiMjZhOGE3OQ==
"""

# 生成随机cookie
def get_cookie(kwd):
	global cookie_str
	kwd = urllib.parse.quote(kwd)
	seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	uid = ''.join([random.choice(seed) for _ in range(32)])
	cookie_str = cookie_str.strip().format(kwd=kwd,uid=uid)
	return cookie_str


def get_header(kwd):
	my_header = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Encoding': 'deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
		'Cookie':get_cookie(kwd),
		'Host': 'image.baidu.com',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-User': '?1',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40',
		}
	return my_header


# 读取txt文件 关键词队列
def read_file(filepath):
	q = queue.Queue()
	for kwd in open(filepath,encoding='utf-8'):
		kwd = kwd.strip()
		if kwd:
			q.put(kwd)
	return q


# 获取源码
def get_html(url, retry=1):
	try:
		r = requests.get(url=url, headers=my_header, timeout=10)
	except Exception as e:
		print(2-retry,'get html error', e)
		time.sleep(30)
		if retry > 0:
			self.get_html(url, retry - 1)
	else:
		html = r.text
		html = html.replace('\\', '\\\\')
		return json.loads(html)



# 解析出图片地址
def parse_html(html):
	if 'data' in html:
		dict_list = html['data']
		df = pd.DataFrame(dict_list)
		img_urls = df['thumbURL'].dropna().values.tolist()
		return img_urls


# 下载图片
def load_img(img_url,img_header,retry=1):
	try:
		r = requests.get(url=img_url, headers=img_header, timeout=10)
	except Exception as e:
		print(2-retry,'load img error', e)
		time.sleep(30)
		if retry > 0:
			self.get_html(img_url,img_header, retry - 1)
	else:
		status = r.status_code
		if status == 200:
			return r.content


# 线程函数
def run():
	global my_header
	while 1:
		kwd = q.get()
		for page_now in range(1,PageNum+1):
			url = f"https://image.baidu.com/search/acjson?tn=resultjson_com&logid=8646329858419699657&ipn=rj&ct=201326592&is=&fp=result&fr=&word={kwd}Word={kwd}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=&z=&ic=&hd=&latest=&copyright=&s=&se=&tab=&width=&height=&face=&istype=&qc=&nc=1&expermode=&nojc=&isAsync=&pn={page_now}&rn={OnePageImg}&gsm=5a&1636014717208="
			my_header = get_header(kwd)
			html = get_html(url)
			if not html:
				continue
			img_urls = parse_html(html)
			img_header =  copy.deepcopy(my_header)
			del img_header['Host']
			if img_urls:
				n = 1
				for img_url in img_urls:
					print(kwd,page_now,n)
					res_bin = load_img(img_url,img_header)
					if res_bin:
						img_path = os.path.join(SavePath,f'{kwd}-{page_now}_{n}.png')
						with open(img_path, 'wb') as f:
							f.write(res_bin)
					else:
						print(res_bin)
					n+=1
					time.sleep(4)
		q.task_done()


if __name__ == "__main__":
	start = time.time()
	SavePath = './bdimg/'
	# 设定每个词抓取前多少页的图片,每个翻页展示图片数
	PageNum,OnePageImg = 1,30 
	q = read_file('kwd.txt')
	if not os.path.exists(SavePath):
		os.mkdir(SavePath)


	# 设置线程数
	for i in list(range(1)):
		t = threading.Thread(target=run,)
		t.setDaemon(True)
		t.start()
	q.join()

	end = time.time()
	print('耗时{0}min'.format((end-start)/60) )
