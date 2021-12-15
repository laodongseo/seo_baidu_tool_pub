# ‐*‐ coding: utf‐8 ‐*‐
"""
提取百度pc下拉词
准备kwd.txt,一行一个
下拉接口抓包获取,目前返回的是json数据
默认线程数1
"""
import requests
import threading
import queue
import gc
import traceback
import random

cookie_str = """
PSTM=1615340407; BIDUPSID={0}; __yjs_duid=1_a1942d4ca1a959bb32e3ffff0cf07ad41617946073654; BAIDUID={1}:SL=0:NR=10:FG=1; MAWEBCUID=web_HZaROXCyXvOjHUxdDgsRzFWcFvyytfvmhKNANGkMBMqFBkpuhv; MSA_WH=375_667; sug=3; sugstore=0; ORIGIN=0; bdime=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; plus_cv=1::m:7.94e+147; H_WISE_SIDS=110085_114550_127969_178384_178640_179349_179379_179432_179623_181133_181588_182233_182273_182290_182530_183035_183330_184012_184267_184319_184794_184891_184894_185029_185268_185519_185632_185652_185880_186015_186318_186412_186580_186596_186662_186820_186841_186844_187023_187067_187087_187214_187287_187345_187433_187447_187563_187670_187726_187815_187915_187926_187929_188182_188267_188296_188332_188425_188614_188670_188733_188741_188787_188843_188871_188897_188993_189043_189150_189269_189325; BD_UPN=12314353; BDSFRCVID_BFESS=Os4OJexroG0ksyjHj78Kt_0-QXWFFS6TDYLtOwXPsp3LGJLVgbfZEG0Pt_m2Fut-Df-rogKK0mOTHUAF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tRk8oK-atDvDqTrP-trf5DCShUFsb-RlB2Q-XPoO3KJ-_nD6yhnMbT83BN0LQCrRBKOrbfbgy4op8P3y0bb2DUA1y4vpKMRUX2TxoUJ25fj8enrDqtnWhfkebPRiJPr9QgbP5lQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wDT8hD6PVKgTa54cbb4o2WbCQHxnr8pcN2b5oQT8BBULfBpRJ5avJMKtEL66U8n7s0lOUWJDkXpJvQnJjt2JxaqRC5h7R_p5jDh3Mbl_qbUTle4ROamby0hvctn6cShnaLfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDHt8J50ttJ3aQ5rtKRTffjrnhPF3y6_dXP6-hnjy3bRqMbD5WU7MepbmBT0V0DuvXUnrQq3Ry6r42-39LPO2hpRjyxv4bU4iBPoxJpOJ5H6B0brIHR7WDqnvbURvD-ug3-7P3x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIEoCtytIthbK0r5nJbq4P0-f602tbq--o2WbCQbJ3O8pcNLTDK2-PbyUjBBp4OWeQJMKtELRo0sKQw0qO1j4_eMtTKKU7CWGvasC3_JtoPqh5jDh3Y3jksD-4Je4bp3aRy0hvctn6cShna5fjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2b6QhDGujt6_jJJ3aQ5rtKRTffjrnhPF3XnJ3XP6-hnjy3bRWQ-T_WnFbbhvmBT0V0qkiQ4jgtq3RymJJ2-39LPO2hpRjyxv4bPDEW4oxJpOJXKDHKt52HlbtKtovbURvD-ug3-7P3x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIE3-oJqCDBMI-G3j; b2b_first=1634117200; RT="z=1&dm=baidu.com&si=k97d09l8cca&ss=kupb6uur&sl=2&tt=54d&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=69z&ul=ez5&hd=f0p"; BAIDUID_BFESS=5942B6B2489AF018E9B0CB23042B5468:FG=1; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03841883355QCv5WIGZhFF2RU2ldgqghNHNXdJoiIMJjMw3VrKvYDWLN843luZvUtDMgHy%2FrHeuXpI1A%2FgXs5QSqQzBpIyIPzxdefaxCtfoz4ZTp%2BVmatTvZ6Tk%2FRtD0J9m9tF3AW9f7BMa9p%2Fwo5Ckye%2FWiWcCezAOgXJV4O9wttVjJ0Qwio59pwKbU4E7yPwystOjptuXOmE%2B0GeaJ9z3BqH5FUBbNd5RZ8dCcfA4Z6HdkPuXgNzaycR04gjZKx6jNtSzpKCoT%2FTPSamtBvce5vLAl%2F2ETb%2FIXvOwRek%2ByBRG10TRfAiY9j2dBIWTRPu0xRnBW8C4LF0NHJjUZ%2BRwSRz8siCiQJ%2FOgoNFtAzE40JzFqj85Je0XylvPmWB3Ksg4jwfVJGa97817693573772344993757455054810; uc_login_unique=f7f2abaa99a6bf1ab5078b309c80e571; uc_recom_mark=cmVjb21tYXJrXzExMjgyMTQ5; BD_HOME=1; delPer=0; BD_CK_SAM=1; PSINO=2; H_PS_PSSID=34837_34446_34067_31254_34712_34584_34504_34829_34578_26350_34691; COOKIE_SESSION=8075_0_8_8_6_32_1_0_5_7_28_1_8092_0_31_0_1634185046_0_1634185015%7C9%231124514_198_1632734797%7C9; H_PS_645EC=86b1TxTvOccdY2fVDfR7xFZHwiRoleFeR61vT2OITGo2qf9H9sy%2FXz2OJf0; BA_HECTOR=0085850k2125a0859l1gmffmd0r; BDSVRTM=0; WWW_ST=1634189034018
"""
# 生成随机cookie
def get_cookie():
	global cookie_str
	seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	uid = ''.join([random.choice(seed) for _ in range(32)])
	psid = ''.join([random.choice(seed) for _ in range(32)])
	cookie_str = cookie_str.strip().format(psid,uid)
	return cookie_str


# 获取某词下拉地址源码
def get_html(url,retry=2):
	my_header = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Encoding': 'deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
		'Cookie':get_cookie(),
		'Host': 'www.baidu.com',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-User': '?1',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/96.0.4664.93',
		}
	try:
		r = requests.get(url=url,headers=my_header, timeout=5)
	except Exception as e:
		print('获取源码失败', url, e)
		if retry > 0:
			get_html(url, retry - 1)
	else:
		html = r.json()
		return html


# 提取下拉词
def get_kwds(html,url):
	kwds = []
	if html and 'https://www.baidu.com/sugrec' in url:
		try:
			kwd_list = html['g']
		except Exception as e:
			pass
		else:
			for data_dict in kwd_list:
				kwd = data_dict['q']
				kwds.append(kwd)
	else:
		print('error,可能反爬')
		time.sleep(60)
	return kwds


# 线程函数
def main():
	while 1:
		kwd = q.get()
		url = 'https://www.baidu.com/sugrec?ie=utf-8&prod=pc&wd={}'.format(kwd)
		try:
			html = get_html(url)
			kwds = get_kwds(html,url)
		except Exception as e:
			traceback.print_exc()
		else:
			for wd in kwds:
				f.write(wd + '\n')
				print(wd)
			f.flush()
		finally:
			del kwd,url
			gc.collect()
			q.task_done()


if __name__ == "__main__":
	# 结果保存文件
	f = open('bdpc_xiala.txt','w',encoding='utf-8')
	# 关键词队列
	q = queue.Queue()
	for kwd in open('kwd.txt',encoding='utf-8'):
		kwd = kwd.strip()
		q.put(kwd)
	# 设置线程数
	for i in list(range(1)):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()
	f.flush()
	f.close()
