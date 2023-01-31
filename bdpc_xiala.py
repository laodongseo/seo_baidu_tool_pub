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
from urllib.parse import quote



RSV_T = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'
RSV_PQ = '123456789abcdef'




# 获取某词下拉地址源码
def get_html(url,retry=2):
	my_header = {
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
	kwd_list = html['g']
	for data_dict in kwd_list:
		kwd = data_dict['q']
		kwds.append(kwd)
	return kwds


# 线程函数
def main():
	while 1:
		kwd = q.get()
		rsv_t = ''.join(random.choice(RSV_T) for _ in range(60))
		rsv_pq = ''.join([random.choice(RSV_PQ) for _ in range(8)] + list('000') + [random.choice(RSV_PQ) for _ in range(5)])
		url = f"https://www.baidu.com/sugrec?ie=utf-8&prod=pc&wd={kwd}&rsv_pq={rsv_pq}&rsv_t={rsv_t}&inputT={random.randint(1000,3000)}"
		print(url)
		try:
			html = get_html(url)
			kwds = get_kwds(html,url)
		except Exception as e:
			traceback.print_exc()
		else:
			str_kwds = '\n'.join(kwds)
			threadLock.acquire()
			f.write(f'{str_kwds}\n') # 防止多线程写入错乱
			threadLock.release()
			f.flush()
		finally:
			del kwd,url
			gc.collect()
			q.task_done()


if __name__ == "__main__":
	threadLock = threading.Lock()  # 锁
	# 结果保存文件
	f = open('bdpc_xiala.txt','w',encoding='utf-8')
	# 关键词队列
	q = queue.Queue()
	for kwd in open('kwd.txt',encoding='utf-8'):
		kwd = kwd.strip()
		q.put(kwd)
	# 设置线程数
	for i in list(range(5)):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()
	f.flush()
	f.close()
