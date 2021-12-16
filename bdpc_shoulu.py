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


cookie_str = """
PSTM={pstm}; BIDUPSID={bid}; __yjs_duid=1_a1942d4ca1a959bb32e3ffff0cf07ad41617946073654; BAIDUID={baidu_uid}:SL=0:NR=10:FG=1; MAWEBCUID=web_HZaROXCyXvOjHUxdDgsRzFWcFvyytfvmhKNANGkMBMqFBkpuhv; MSA_WH=375_667; sug=3; sugstore=0; ORIGIN=0; bdime=0; H_WISE_SIDS=110085_114550_127969_178384_178640_179349_179379_179432_179623_181133_181588_182233_182273_182290_182530_183035_183330_184012_184267_184319_184794_184891_184894_185029_185268_185519_185632_185652_185880_186015_186318_186412_186580_186596_186662_186820_186841_186844_187023_187067_187087_187214_187287_187345_187433_187447_187563_187670_187726_187815_187915_187926_187929_188182_188267_188296_188332_188425_188614_188670_188733_188741_188787_188843_188871_188897_188993_189043_189150_189269_189325; BD_UPN=12314353; BDSFRCVID_BFESS=RC8OJexroG0ksyjHeekft_0-Q-iJsNTTDYLtOwXPsp3LGJLVgbfZEG0PtqRcLAA-Df-rogKK0mOTHUAF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tJKj_CDMJDvDqTrP-trf5DCShUFsQftOB2Q-XPoO3KJOqPTFy-oqMPK3BN0LQCr0Wj7w-UbgylRM8P3y0bb2DUA1y4vpK-jhyeTxoUJ2-xoj8hjqqfOtqJDebPRiJPr9QgbP5lQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0HPonHj_bDTcX3J; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03845316300D%2FzLN%2BJ7zNDxJlhYo3r6ihnWZdQhCHqmpHB%2FaFPxcSiaftwmHTw6U6sD2k9NjOnzc9xn9ZXLol4a%2Fv%2BrX4jSTm3xXAC0MMRtJTsrovb7wOrWMklZn%2Btu0Y2bPrzQEhD8v33XC5d2wzV8of%2FCwlGL9wYRKizMlQKXcTxGPRs0fyl7EGfTzZZcnsjRFUfZM2Zg1sTk4oIICjApYJCygEfDY0j7ec9mZ8CGZRMEoYRw4HmqET2Ly35Fiux6HT2Rey1qtz6wGCsJXGaJaFEfkBODMTqW%2Bl53PsYDsjSZhr%2FiwI9Fpj64mD5DihHNueSzaCLc43XsUdX%2BItjyztTzjYd46%2BpePc1GD5UplANY0twdq9uHOypnmOF3Osnn%2FIpyc3n848304210330984578083840279038577; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; PSINO=7; BDRCVFR[YDNdHN8k-cs]=9xWipS8B-FspA7EnHc1QhPEUf; BDRCVFR[PaHiFN6tims]=9xWipS8B-FspA7EnHc1QhPEUf; BAIDUID_BFESS=80D966DD9D440BC71840BB7C71BB6F3F:FG=1; BD_HOME=1; H_PS_PSSID={pssid}; H_PS_645EC=366ff4TlhurQ5jf7Sys3Jkhh4Z%2FSvN9YUdYCwahPTRb5UT6uc6vpB9zHVo8; BA_HECTOR={hector}; BDSVRTM=194; COOKIE_SESSION=17015_0_5_8_5_10_1_0_4_6_1_1_246351_0_0_0_1634523437_0_1634540448%7C9%231466123_207_1634200920%7C9; WWW_ST=1634540457971
"""

# 生成随机cookie
def get_cookie():
	pstm = int(time.time()) - random.randint(300, 1800)
	seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	bid = ''.join([random.choice(seed) for _ in range(32)])
	baidu_uid = ''.join([random.choice(seed) for _ in range(32)])
	pps_1 = [random.randint(33666, 34227) for i in range(random.randint(6, 12))]
	pssid = '_'.join([str(x) for x in (pps_1+[26350])])
	str1 = '012345678901234567890123456789abcdefghijklmnopqrstuvwxyz'
	hector = ''.join([random.choice(str1) for _ in range(27)])
	return cookie_str.strip().format(pstm=pstm,bid=bid,baidu_uid=baidu_uid,pssid=pssid,hector=hector)


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
	def get_html(self,url,my_header,retry=2):
		try:
			r = requests.get(url=url,headers=my_header,timeout=20)
		except Exception as e:
			print('获取源码失败',e)
			time.sleep(10)
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
			randomtime=random.randint(3000,6000)
			url = f"https://www.baidu.com/s?ie=utf-8&tn=50000021_hao_pg&ssl_sample=normal&word={target_url}&inputT={randomtime}&rsv_sug4={randomtime}"
			ua = random.choice(list_ua)
			my_header = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Encoding': 'deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
		'Host': 'www.baidu.com',
		'Sec-Fetch-Dest': 'document',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-User': '?1',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent':ua ,
		'Cookie': get_cookie(),
		}
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
	list_ua = [i.strip() for i in open('ua_pc.txt', 'r', encoding='utf-8')]
	q = BdpcShoulu.read_txt('pc-url.txt') # url队列
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
