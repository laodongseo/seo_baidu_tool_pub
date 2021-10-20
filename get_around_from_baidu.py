# ‐*‐ coding: utf‐8 ‐*‐
"""
 
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import gc
import json
import pandas as pd
import time
import traceback

ak = 'iMplFNfYyAf4e7EleegtObtcOZdliriG'


class BdmoReal(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取excel文件
    @staticmethod
    def read_excel(excel_path):
        q = queue.Queue()
        df = pd.read_excel(excel_path)
        for idx, series_row in df.iterrows(): 
            # print(series_row)
            q.put(series_row)
        return q

    # 获取源码
    def get_html(self, url, retry=2):
        try:
            r = requests.get(url=url, headers=my_header, timeout=20)
        except Exception as e:
            print('获取源码失败', url, e)
            if retry > 0:
                self.get_html(url, retry - 1)
        else:
            # print(r.text)
            html = r.json()
            status = html['status'] if 'status' in html else ''
            if status == 0:
                return html

    # 获取数据
    def get_data(self,html):
        datas = []
        if html:
            try:
                data_list = html['results']
                for one_data in data_list:
                    name = one_data['name']
                    address = one_data['address']
                    datas.append((name,address))
            except Exception as e:
                print('提取失败', e)
        else:
            print('源码异常')
        return datas

    # 提取接口数据组合
    def make_content(self,xiaoqu,datas,distance,item):
        content = ''
        if len(datas) == 0:
            content = '{0}{1}米以内暂无{2}信息。'.format(xiaoqu,distance,item)
        else:
            content = '{0}{1}米以内有{2}家{3}场所。分别是：'.format(xiaoqu,distance,len(datas),item)
            num = 1
            for data in datas:
                name,address = data
                text = '{0}、{1}，{2}。'.format(num,name,address)
                content = '{0}{1}'.format(content,text)
                num += 1
        return content



    # 线程函数
    def run(self):
        while 1:
            series = q.get()
            id,xiaoqu,x,y = series['id'],series['小区名'],series['x'],series['y'],
            print(id,xiaoqu)
            try:
                content_last = ''
                for info in info_dicts.items():
                    item,distance = info
                    url = "http://api.map.baidu.com/place/v2/search?query={0}&location={1},{2}&radius={3}&output=json&ak=iMplFNfYyAf4e7EleegtObtcOZdliriG".format(item,y,x,distance)
                    print(url)
                    html = self.get_html(url)
                    datas = self.get_data(html)
                    content = self.make_content(xiaoqu,datas,distance,item)
                    content_last = '{0}{1}'.format(content_last,content)
                f.write('{0}\t{1}\t{2}\n'.format(id,xiaoqu,content_last))
                f.flush()       
            except Exception as e:
                print(e)
                traceback.print_exc(file=open('log-jt.txt', 'w'))
            finally:
                del series
                gc.collect()
                q.task_done()
                time.sleep(2)

if __name__ == "__main__":
    # info_dicts = {'医院':2000,'公交站':500,'地铁站':500,'超市':500,'银行':500,'药店':500,'购物':1000,'健身房':1000,'游泳馆':1000,'餐饮':1000}
    info_dicts = {'购物':1000,'健身房':1000,'游泳馆':1000,'餐饮':1000}
    # 结果保存文件
    f = open('xiaoqu_购物娱乐餐饮.txt','w',encoding='utf-8')
    # # head设置
    my_header = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding':'deflate',
'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'BIDUPSID=95E739A8EE050812705C1FDE2584A61E; PSTM=1563865961; BDUSS=Dk4ZVBCcWN3aVA1LUF-TlRrYTYxczR1TnFwSWtncVZzdzBUMkRpM2p-QTd2dlZlRVFBQUFBJCQAAAAAAAAAAAEAAADag5oxzI2IkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADsxzl47Mc5ed; Hm_lvt_5650c092812f8659cdfe23eeb42024ef=1602472419; BAIDUID=E0D57438CE93313860A15516D710752C:SL=0:NR=10:FG=1; H_WISE_SIDS=148077_153759_153767_158347_149355_150967_152056_156813_156286_150775_154258_148867_155225_154738_153243_153628_157235_154173_150772_156387_153065_156516_127969_154412_154175_155329_158527_146732_131423_155885_114550_157965_107316_158320_154190_155344_155255_158488_157790_144966_157782_154619_157814_139882_156849_156725_157188_154148_147551_158424_158367_153447_158126_157697_154639_154359_158686_110085_157006; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03544648944g6p4%2B0fkCp3BSwVsMTmdIWuM0GAnr4lrpaRUJkAXd%2Bs0FqEVeyTEtLWS%2FfjuHjDDjuVXY7K4KTRucMuo1YmilaY52bMtht%2BrrXvyMbwz647If7WwUbU6jFE6Mg33fQf9%2FDJd%2FK9zEb6vaF4Of6jDwQzt1jRLJ8WKWq%2FrrwFvAFJMizZAdOrk%2Bh5v4GX2BmQVkqehMwQ%2F2sGKYwQSGP%2BPdc%2F5q72s%2FMZWIu0CbNH27uXQ1GU4O6ckdWRWzBbvwMyNuoSmfruML8w9S7CLvI%2Fljc65s5iSHrAwB%2F0gmc7VoQu12YYEOJ7DwrDJTTq1fNT2oVv3TAm%2FQwSGpoALaHIuKQpMSq31mHQngiI9doObeEBtlD4LhNieCCztBoXPIAXV43924086237816049699089008714510; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; PSINO=7; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; __yjsv5_shitong=1.0_7_3d1d43e1ff826d9923ded0a36d16a55a2a8d_300_1604479827882_60.247.59.67_c154ca22; yjs_js_security_passport=44817cf192e44e44ebbe0c70a696c8dcaa99aee5_1604479828_js; H_PS_PSSID=32813_1422_32854_32939_31660_32970_32706_32961; BA_HECTOR=8hah018424a08kbjiv1fq4s210o',
'Host':'api.map.baidu.com',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
    }
    # 关键词队列
    q = BdmoReal.read_excel('南昌小区_500_test.xlsx')
    # 设置线程数
    for i in list(range(1)):
        t = BdmoReal()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()

