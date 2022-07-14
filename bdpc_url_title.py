# ‐*‐ coding: utf‐8 ‐*‐
"""
kwd.txt为词根,一行一个
采集搜索结果页的标题和对应的url
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import random
import traceback
import re

cookie_str = """
PSTM={pstm}; BIDUPSID={bid}; __yjs_duid=1_da77c7c82b6462b1717eb54848f615d81617973056097; BAIDUID={baidu_uid}:SL=0:NR=10:FG=1; MAWEBCUID=web_HZaROXCyXvOjHUxdDgsRzFWcFvyytfvmhKNANGkMBMqFBkpuhv; MSA_WH=375_667; sug=3; sugstore=0; ORIGIN=0; bdime=0; H_WISE_SIDS=110085_114550_127969_178384_178640_179349_179379_179432_179623_181133_181588_182233_182273_182290_182530_183035_183330_184012_184267_184319_184794_184891_184894_185029_185268_185519_185632_185652_185880_186015_186318_186412_186580_186596_186662_186820_186841_186844_187023_187067_187087_187214_187287_187345_187433_187447_187563_187670_187726_187815_187915_187926_187929_188182_188267_188296_188332_188425_188614_188670_188733_188741_188787_188843_188871_188897_188993_189043_189150_189269_189325; BD_UPN=12314353; BDSFRCVID_BFESS=RC8OJexroG0ksyjHeekft_0-Q-iJsNTTDYLtOwXPsp3LGJLVgbfZEG0PtqRcLAA-Df-rogKK0mOTHUAF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tJKj_CDMJDvDqTrP-trf5DCShUFsQftOB2Q-XPoO3KJOqPTFy-oqMPK3BN0LQCr0Wj7w-UbgylRM8P3y0bb2DUA1y4vpK-jhyeTxoUJ2-xoj8hjqqfOtqJDebPRiJPr9QgbP5lQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0HPonHj_bDTcX3J; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03845316300D%2FzLN%2BJ7zNDxJlhYo3r6ihnWZdQhCHqmpHB%2FaFPxcSiaftwmHTw6U6sD2k9NjOnzc9xn9ZXLol4a%2Fv%2BrX4jSTm3xXAC0MMRtJTsrovb7wOrWMklZn%2Btu0Y2bPrzQEhD8v33XC5d2wzV8of%2FCwlGL9wYRKizMlQKXcTxGPRs0fyl7EGfTzZZcnsjRFUfZM2Zg1sTk4oIICjApYJCygEfDY0j7ec9mZ8CGZRMEoYRw4HmqET2Ly35Fiux6HT2Rey1qtz6wGCsJXGaJaFEfkBODMTqW%2Bl53PsYDsjSZhr%2FiwI9Fpj64mD5DihHNueSzaCLc43XsUdX%2BItjyztTzjYd46%2BpePc1GD5UplANY0twdq9uHOypnmOF3Osnn%2FIpyc3n848304210330984578083840279038577; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; delPer=0; BD_CK_SAM=1; PSINO=7; BDRCVFR[YDNdHN8k-cs]=9xWipS8B-FspA7EnHc1QhPEUf; BDRCVFR[PaHiFN6tims]=9xWipS8B-FspA7EnHc1QhPEUf; BAIDUID_BFESS=80D966DD9D440BC71840BB7C71BB6F3F:FG=1; BD_HOME=1; H_PS_PSSID={pssid}; H_PS_645EC=366ff4TlhurQ5jf7Sys3Jkhh4Z%2FSvN9YUdYCwahPTRb5UT6uc6vpB9zHVo8; BA_HECTOR={hector}; BDSVRTM=194; COOKIE_SESSION=17015_0_5_8_5_10_1_0_4_6_1_1_246351_0_0_0_1634523437_0_1634540448%7C9%231466123_207_1634200920%7C9; WWW_ST=1634540457971
"""


# 生成随机cookie
def get_cookie():
	pstm = int(time.time()) - random.randint(300, 1800)
	seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	bid = ''.join([random.choice(seed) for _ in range(32)])
	baidu_uid = ''.join([random.choice(seed) for _ in range(32)])
	pps_1 = [random.randint(33666, 34227) for i in range(random.randint(6, 12))]
	pssid = '_'.join([str(x) for x in (pps_1 + [26350])])
	str1 = '012345678901234567890123456789abcdefghijklmnopqrstuvwxyz'
	hector = ''.join([random.choice(str1) for _ in range(27)])
	return cookie_str.strip().format(pstm=pstm, bid=bid, baidu_uid=baidu_uid, pssid=pssid, hector=hector)


class BdpcTitle(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)

	# 读取txt文件 获取待查询url
	@staticmethod
	def read_txt(filepath):
		q = queue.Queue()
		for kwd in open(filepath, encoding='utf-8'):
			kwd = kwd.strip()
			q.put(kwd)
		return q

	# 获取某待查询url的serp源码
	def get_html(self, url, retry=1):
		try:
			r = requests.get(url=url, headers=my_header, timeout=15)
		except Exception as e:
			print('获取源码失败', url, e)
			if retry > 0:
				self.get_html(url, retry - 1)
		else:
			html = r.content.decode('utf-8')
			return html,r.url

	# 获取源码title和url
	def get_encrpt_urls(self, html):
		encrypt_title_urls = []
		real_title_urls = []
		doc = pq(html)
		div_list = doc('#content_left .result').items()  # 自然排名
		div_op_list = doc('#content_left .result-op').items()  # 非自然排名
		for div in div_list:
			rank = div.attr('id') if div.attr('id') else 'id_xxx'
			if rank:
				a = div('h3 a')  # 空对象pyquery.pyquery.PyQuery为假
				encrypt_url = a.attr('href') if a else None
				title = div('h3').text().strip()
				title = re.sub(r'\s+', '', title)
				encrypt_title_urls.append((title, encrypt_url))
		for div in div_op_list:
			rank_op = div.attr('id') if div.attr('id') else 'id_xxx'
			if rank_op:
				link = div.attr('mu')  # 真实url,有些op样式没有mu属性
				title = div('h3').text().strip()
				title = re.sub(r'\s+', '', title)
				if link:
					real_title_urls.append((title, link))
				else:
					encrypt_url = div('article a').attr('href')
					encrypt_title_urls.append((title, encrypt_url))
		return encrypt_title_urls, real_title_urls

	# 解密某条加密url
	def decrypt_url(self, encrypt_url, retry=1):
		try:
			encrypt_url = encrypt_url.replace('http://', 'https://')
			r = requests.head(encrypt_url, headers=my_header)
		except Exception as e:
			print(encrypt_url, '解密失败', e)
			if retry > 0:
				self.decrypt_url(encrypt_url, retry - 1)
		else:
			return r.headers['Location']

	# 线程函数
	def run(self):
		global my_header
		while 1:
			kwd = q.get()
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
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49',
				'Cookie': get_cookie(),
			}
			try:
				url = f"https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=48020221_12_hao_pg&wd={kwd}"
				print(kwd,url)
				html_serp_url = self.get_html(url)
				html,serp_url  = html_serp_url if html_serp_url else (None,None)
				if not html:
					continue
				title_obj = re.search('<title>(.*?)</title>',html,re.S|re.I)
				title = title_obj.group() if title_obj else '--'
				if '_百度搜索' not in title:
					print('源码异常,可能反爬')
					time.sleep(120)
					continue
				encrypt_title_urls, real_title_urls = self.get_encrpt_urls(html)
			except Exception as e:
				traceback.print_exc()
			else:
				for element in encrypt_title_urls:
					title, encrypt_url = element
					real_url = self.decrypt_url(encrypt_url)
					f.write(f'{kwd}\t{title}\t{real_url}\n')
					print(title, real_url)
					time.sleep(0.3)
				for element in real_title_urls:
					title, real_url = element
					f.write(f'{kwd}\t{title}\t{real_url}\n')
				f.flush()
			finally:
				q.task_done()
				time.sleep(2)


if __name__ == "__main__":
	q = BdpcTitle.read_txt('kwd.txt')
	f = open('bdpc_title_url.txt', 'w+', encoding='utf-8')
	# 设置线程数
	for i in list(range(1)):
		t = BdpcTitle()
		t.setDaemon(True)
		t.start()
	q.join()
	f.flush()
	f.close()
