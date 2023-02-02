# -*- coding: utf-8 -*-
"""
搜狗验证码识别
"""

import requests,time,re
from pyquery import PyQuery as pq
import queue
import threading
import traceback   
import ssl
import pandas as pd
import io,time
from PIL import Image
import pytesseract

tesseract_cmd = r'D:\install\tessractOCR\tesseract' # tessractOCR.exe
pytesseract.pytesseract.tesseract_cmd =tesseract_cmd

#设置忽略SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36 SE 2.X MetaSr 1.0'

def get_html(url,retry=1):
	cookie = cookiejar.CookieJar()
	handler = request.HTTPCookieProcessor(cookie)
	opener = request.build_opener(handler)
	opener.addheaders=[('User-Agent',UA)]
	response = opener.open('https://www.sogou.com')
	cookie_result = ""
	for item in cookie:
		cookie_result = cookie_result + item.name + "=" + item.value + ";"
	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
		'Connection': 'keep-alive',
		'User-Agent': UA,
		'Cookie': cookie_result
	}
	try:
		r = requests.get(url,headers=headers)
	except Exception as e:
		traceback.print_exc()
		time.sleep(30)
		if retry > 0:
			get_html(url,retry-1)
	else:
		return r.text

def parse_img(codebytes,threshold=95):
	img = Image.open(io.BytesIO(codebytes))
	img.save('12.png')
	table = []
	for i in range(256):
		if i < threshold:
			table.append(0)
		else:
			table.append(1)
	img = img.convert('L')
	image = img.point(table, '1')   #二值化
	image.save('1.png')
	# image = Image.open(r'aaa.png') 
	text = pytesseract.image_to_string(image)
	print(text,type(text))



def get_html():
	headers = {
		'Accept':'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
'Accept-Encoding':'deflate',
'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,pt;q=0.5',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Cookie':'pgv_pvi=803115008; SUID=433BF73C1721A00A000000006001012E; SUV=1610678580404418; front_screen_dpi=1; front_screen_resolution=1440*900; ssuid=8566186496; GOTO=; FREQUENCY=1617084823435_11; SGINPUT_UPSCREEN=1665622911041; wuid=AAEpdl0MQQAAAAqMGhkiNQAA1wA=; IPLOC=CN1100; SMYUV=1672794210306274; ABTEST=0|1672969035|v17; browerV=3; osV=1; ariaDefaultTheme=undefined; arialoadData=false; PHPSESSID=uugvsk3610v9jnouuntc0ijcj6; sst0=121; SNUID=D35A23A1D2D62161F845DB5ED38E15FC; ld=KZllllllll20HTHnlllllp5bYn6llllltspwlylllR9llllllklll5@@@@@@@@@@; refresh=1',
'Host':'www.sogou.com',
'Pragma':'no-cache',
'Referer':'http://www.sogou.com/antispider/?m=1&antip=web_hb&from=%2Fweb%3Fquery%3D%25E5%258C%2597%25E4%25BA%25AC%25E6%2588%25BF%25E4%25BA%25A7%26_ast%3D1675320993%26_asf%3Dwww.sogou.com%26w%3D01029901%26p%3D40040100%26dp%3D1%26cid%3D%26s_from%3Dresult_up&suuid=417fdaa8-a4bd-4319-abc7-c0db5986b28c',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70',
	}
	code_url = f'http://www.sogou.com/antispider/util/seccode.php?tc={int(time.time())*1000}'
	codebytes = requests.get(code_url,headers=headers).content
	parse_img(codebytes)

get_html()


