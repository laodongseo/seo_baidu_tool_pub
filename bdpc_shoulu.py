# ‐*‐ coding: utf‐8 ‐*‐
"""
准备url.txt,一行一个url,必须带http或https
区分https或者http
区分https://aaa/bbb和https://aaa/bbb/
查询某个url是否收录
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue
import time


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

    # 获取某待查询url的serp源码
    def get_html(self, url, retry=2):
        try:
            r = requests.get(url=url, headers=user_agent, timeout=5)
        except Exception as e:
            print('获取源码失败', url, e)
            if retry > 0:
                self.get_html(url, retry - 1)
        else:
            html = r.text
            return html

    # 获取某待查询url的serp源码上自然排名的所有url
    def get_encrpt_urls(self, html):
        encrypt_url_list = []
        if html and '_百度搜索' in html:
            doc = pq(html)
            try:
                a_list = doc('.t a').items()
            except Exception as e:
                print('未找到加密url,链接未收录', e)
            else:
                for a in a_list:
                    encrypt_url = a.attr('href')
                    if encrypt_url.find('http://www.baidu.com/link?url=') == 0:
                        encrypt_url_list.append(encrypt_url)
        else:
            print('源码不正常,可能有反爬')
        # print(encrypt_url_list)
        return encrypt_url_list

    # 解密某条加密url
    def decrypt_url(self, encrypt_url, retry=1):
        try:
            encrypt_url = encrypt_url.replace('http://', 'https://')
            r = requests.head(encrypt_url, headers=user_agent)
        except Exception as e:
            print(encrypt_url, '解密失败', e)
            if retry > 0:
                self.decrypt_url(encrypt_url, retry - 1)
        else:
            # print(r.headers['Location'])
            return r.headers['Location']

    # 获取某待查询url首页的真实url
    def get_real_urls(self, encrypt_url_list):
        if encrypt_url_list:
            real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
            return real_url_list
        else:
            return []

    # 检查链接是否有收录
    def check_include(self, url, real_urls):
        # print(real_urls)
        if url in real_urls:
            return 1
        else:
            return 0

    # 线程函数
    def run(self):
        while 1:
            target_url = q.get()
            # 查询该target_url是否收录  url带上tn等参数 否则会被反爬
            url = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=87048150_dg&wd={0}".format(target_url)
            html = self.get_html(url)
            encrypt_url_list = self.get_encrpt_urls(html)
            real_urls = self.get_real_urls(encrypt_url_list)
            print(real_urls)
            num = self.check_include(target_url, real_urls)
            if num == 1:
                print(target_url,"收录")
                f.write(target_url+'\t'+'收录\n')
            elif num == 0:
                print(target_url,"未收录")
                f.write(target_url + '\t' + '未收录\n')

            q.task_done()


if __name__ == "__main__":

    start = time.time()
    user_agent = {
        'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Mobile Safari/537.36 SE 2.X MetaSr 1.0',
        'Cookie':'BIDUPSID=EB1F44AB7896D7EFA4F0FD243C29FF17; PSTM=1567562976; BAIDUID=EB1F44AB7896D7EFA4F0FD243C29FF17:SL=0:NR=10:FG=1; BDUSS=BZWlZuSXpNWmNjM3BTSktnM2xhbGhIdUlqeW1ITEdvclpzSHpIS3p2WUMwc2hkRVFBQUFBJCQAAAAAAAAAAAEAAAAGtiZkNzcyNDgzMjAwZG9uZwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJFoV0CRaFdeF; plus_cv=1::m:49a3f4a6; MSA_WH=400_655; lsv=globalTjs_3a11c3d-globalT_androidcss_4630b37-wwwT_androidcss_c5f9a54-searchboxcss_591d86b-globalBcss_aad48cc-wwwBcss_777000e-framejs_c9ac861-atomentryjs_5cd4b30-globalBjs_99ad350-wwwjs_b674808; BD_UPN=19314353; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BDICON=10294984.98; delPer=0; BD_CK_SAM=1; rsv_i=c2b6G%2F3avQC%2FfgLjK6Tg5dByzXJGjTHszykjx0XgYlZZgizi3%2F9wOVrzCucTWKLxPYYUs%2BqPpygizpeQMUWhVScLKRxzaaw; FEED_SIDS=732051_1030_14; plus_lsv=f197ee21ffd230fd; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1572225355,1572415847,1572418912; Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1572418912; BAIDULOC=12966109.384666294_4841881.341700486_100_131_1572418911981; SE_LAUNCH=5%3A26206981_0%3A26206981; BDPASSGATE=IlPT2AEptyoA_yiU4VKH3kIN8efjWvW4AfvESkplQFStfCaWmhH3BrUzWz0HSieXBDP6wZTXdMsDxXTqXlVXa_EqnBsZolpOaSaXzKGoucHtVM69-t5yILXoHUE2sA8PbRhL-3MEF2ZELlQvcgjchQZrchW8z3JTpxz1z5Xocc0T1UKR2VLJxJyTS7xvRHvcPNuz94rXnEpKKSmBUADHRVjYcSQyWXkD5NOtjsAm1Q0WrkoXGurSRvAa1G8vJpFeXAio1fWU60ul269v5HViViwh9UOI7u46MnJZ; H_WISE_SIDS=137151_137734_137755_136649_137663_137071_128070_134982_136665_120196_136768_137002_137788_136366_132909_136456_137690_135847_131246_137746_132378_136681_118893_118876_118846_118827_118802_132782_136800_136431_136093_133352_136862_137089_129652_136194_124637_137105_137572_133847_132551_137468_134046_129646_131423_137212_137466_136034_110085_127969_137613_131951_136611_137252_128196_137696_136636_137767_137207_134347_134231_137618_137449; kleck=638cabc3ad33a7a082343c4553a47c42; BDRCVFR[x4e6higC8W6]=mk3SLVN4HKm; PSINO=7; H_PS_PSSID=1440_21084_20697_29567_29220; sug=3; sugstore=0; ORIGIN=0; bdime=0; H_PS_645EC=db34IWhem1lYO7OwXVBPbsx2yQuIu3jmqGT9FUp09TItjsTj8omDTLnov6%2BIZQe6dqc',
        'Host':'www.baidu.com',
        'Upgrade-Insecure-Requests':'1'}
    q = BdpcShoulu.read_txt('pc_url.txt')
    f = open('bdpc_shoulu.txt','w+',encoding='utf-8')
    # 设置线程数
    for i in list(range(1)):
        t = BdpcShoulu()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
    end = time.time()
    print('耗时{0}min'.format((end - start) / 60))

