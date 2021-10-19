# coding: utf-8
"""
www2.baidu.com竞价后台拓词
登录抓包填写userid
登录抓包填写token
抓包复制cookie
"""
import threading
import queue
import pandas as pd
import requests
import random
import time
import json



def GenSecretKey():
	s = "0123456789abcdef"
	part1 = ''.join([random.choice(s) for _ in range(4)])
	part2 = ''.join([random.choice(s) for _ in range(3)])
	part3 = ''.join([random.choice(s) for _ in range(4)])
	t = str(int(time.time()) * 1000)
	SecretKey = f'4b534c47-{part1}-4{part2}-{part3}-{t[0:12]}'
	return SecretKey


def get_kwd(txt_path):
	q = queue.Queue()
	for kwd in open(txt_path,'r',encoding='utf-8'):
		kwd = kwd.strip()
		q.put(kwd)
	return q


def post_html(kwd,retry=1):
	form_data = {
	'reqid':Reqid,
	'eventId':Eventid,
	'userid':MyUserid,
	'token':MyToken,
	'path':'lightning/GET/KeywordSuggestService/getKeywordRecommendPassive',
	'params':{"keyWordRecommendFilter":{"device":0,"positiveWords":[],"negativeWords":[],"keywordRecommendReasons":[],"searchRegions":"9999999","regionExtend":False,"removeDuplicate":False,"removeBrandWords":False,"removeCampaignDuplicate":False,"fieldFilters":[]},"source":"web","queryBy":0,"pageNo":1,"pageSize":3000,"wordQuerys":[kwd],"querySessions":[kwd],"entryMessage":"kr_station"}
	}

	form_data["params"] = json.dumps(form_data["params"])

	try:
		r = requests.post(url=PostUrl,headers=headers,data=form_data,timeout=15)
	except Exception as e:
		print(f'{2-retry}error,{e},暂停60 s')
		time.sleep(60)
		if retry > 0:
			post_html(kwd,retry-1)
	else:
		page_source = r.json()
		return page_source


def parse_html(html):
	df = pd.DataFrame(dtype=object)
	if html['status'] == 0:
		kwd_items = html['data']['keywordRecommendItems'] if 'keywordRecommendItems' in html['data'] else []
		df = pd.DataFrame(kwd_items)
	return df


def main():
	global IsHeader
	now = int(time.time())
	while True:
		kwd = q.get()
		html = post_html(kwd)
		if not html:
			q.task_done()
			continue
		df = parse_html(html)
		if df.shape[0] > 0:
			if IsHeader == 0:
				df.to_csv(f'fengchao_kwd_{now}.csv',encoding='utf_8_sig',mode='w+',index=False)
				IsHeader = 1
			else:
				df.to_csv(f'fengchao_kwd_{now}.csv',encoding='utf_8_sig',mode='a+',index=False,header=False)
		q.task_done()
		time.sleep(3)



if __name__ == "__main__":
	IsHeader = 0 # df.to_csv只第一行写表头
	q = get_kwd(txt_path = 'kwd.txt') # 关键词文件
	MyUserid = 11282149 # 登录抓包填写userid
	MyToken = 644925111 # 登录抓包填写token
	Reqid = GenSecretKey()
	Eventid = GenSecretKey()
	PostUrl = f"https://fengchao.baidu.com/hairuo/request.ajax?path=lightning%2FGET%2FKeywordSuggestService%2FgetKeywordRecommendPassive&reqid={Reqid}"
	headers = {
	'authority':'fengchao.baidu.com',
	'method':'POST',
	'path':f'/hairuo/request.ajax?path=lightning%2FGET%2FKeywordSuggestService%2FaddKeywordRecommendLog&reqid={Reqid}',
	'scheme':'https',
	'accept':'application/json',
	'accept-encoding':'deflate',
	'accept-language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,pt;q=0.5',
	'cache-control':'no-cache',
	'content-length':'16994',
	'content-type':'application/x-www-form-urlencoded',
	'origin':'https://fengchao.baidu.com',
	'pragma':'no-cache',
	'referer':f'https://fengchao.baidu.com/fc/manage/new/user/{MyUserid}/kr',
	'sec-ch-ua':'"Chromium";v="94", "Microsoft Edge";v="94", ";Not A Brand";v="99"',
	'sec-ch-ua-mobile':'?0',
	'sec-ch-ua-platform':'"Windows"',
	'sec-fetch-dest':'empty',
	'sec-fetch-mode':'cors',
	'sec-fetch-site':'same-origin',
	'cookie': open('cookie.txt').readlines()[0].strip(),
	'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50',
	}
	for i in range(1):
		t = threading.Thread(target=main,)
		t.daemon = True
		t.start()
	q.join()

