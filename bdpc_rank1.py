# ‐*‐ coding: utf‐8 ‐*‐
"""
kwd和url一对一查询 查自然排名(含快照)前十名
kwd_url.txt,每行放关键词和url,中间用制表符隔开(可从excel复制两列),
url加http或者https,区分http和https
区分http://aaa/bbb/和http://aaa/bbb
(cookie用自己登陆账号后的cooke否则很容易被反爬)
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import gc


class BdpcRank1(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取txt文件 获取待查询url
    @staticmethod
    def read_txt(filepath):
        q = queue.Queue()
        for line in open(filepath, encoding='utf-8'):
            kwd_url = line.strip().split('\t')
            q.put(kwd_url)
        return q

    # 获取某词的serp源码
    def get_html(self,url,retry=2):
        try:
            r = requests.get(url=url,headers=my_header,timeout=5)
        except Exception as e:
            print('获取源码失败',e)
            time.sleep(6)
            if retry > 0:
                self.get_html(url,retry-1)
        else:
            html = r.content.decode('utf-8',errors='ignore')  # 用r.text有时候识别错误
            url = r.url  # 反爬会重定向,取定向后的地址
            return html,url

    # 获取某词的serp源码上自然排名的所有url
    def get_encrpt_urls(self, html,url):
        encrypt_url_list_rank = []
        doc = pq(html)
        title = doc('title').text()
        if '_百度搜索' in title and 'https://www.baidu.com/s?tn=48020221' in url:
            div_list = doc('.result').items() # 自然排名/有快照
            # div_op_list = doc('.result-op').items() # 非自然排名
            for div in div_list:
                rank = div.attr('id')
                if rank:
                    try:
                        a_list = div('.t a').items()
                    except Exception as e:
                        print('未提取自然排名加密链接')
                    else:
                        for a in a_list:
                            encrypt_url = a.attr('href')
                            if encrypt_url.find('http://www.baidu.com/link?url=') == 0:
                                encrypt_url_list_rank.append((encrypt_url,rank))
        else:
            print(title,'源码异常,可能反爬')
            time.sleep(20)
                    
        return encrypt_url_list_rank

    # 解密某条加密url
    def decrypt_url(self, encrypt_url, retry=1):
        real_url = 'xxxx'
        try:
            encrypt_url = encrypt_url.replace('http://', 'https://')
            r = requests.head(encrypt_url, headers=my_header)
        except Exception as e:
            print(encrypt_url, '解密失败', e)
            if retry > 0:
                self.decrypt_url(encrypt_url, retry - 1)
        else:
            real_url = r.headers['Location']
        return real_url

    # 格式化成字典,键为url值为排名
    def make_dict(self,encrypt_urls_ranks):
        rank_dict = {}
        for encrypt_url_rank in encrypt_urls_ranks:
            encrypt_url,rank= encrypt_url_rank
            real_url = self.decrypt_url(encrypt_url)
            rank_dict[real_url] = rank
        return rank_dict

    # 线程函数
    def run(self):
        while 1:
            kwd_url = q.get()
            kwd = kwd_url[0]
            url_check = kwd_url[1]
            url = "https://www.baidu.com/s?tn=48020221_28_hao_pg&ie=utf-8&wd={0}".format(kwd)
            try:
                html,now_url = self.get_html(url)
                encrypt_url_list_rank = self.get_encrpt_urls(html,now_url)
            except Exception as e:
                print(e)
            else:
                if encrypt_url_list_rank:
                    rank_dict = self.make_dict(encrypt_url_list_rank)
                    url_keys = list(rank_dict.keys())
                    if url_check in url_keys:
                        rank = rank_dict[url_check]
                        f.write(kwd+'\t'+url_check+'\t'+str(rank)+'\n')
                        print(kwd,url_check,rank)
                    else:
                        f.write(kwd + '\t' + url_check + '\t' + '无' + '\n')
                        print(kwd, url_check, '无')
                    f.flush()
            finally:
                del kwd_url,kwd,url_check
                gc.collect()
                q.task_done()


if __name__ == "__main__":

    my_header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Cookie':'BIDUPSID=EB1F44AB7896D7EFA4F0FD243C29FF17; PSTM=1567562976; BAIDUID=EB1F44AB7896D7EFA4F0FD243C29FF17:SL=0:NR=10:FG=1; BDUSS=BZWlZuSXpNWmNjM3BTSktnM2xhbGhIdUlqeW1ITEdvclpzSHpIS3p2WUMwc2hkRVFBQUFBJCQAAAAAAAAAAAEAAAAGtiZkNzcyNDgzMjAwZG9uZwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJFoV0CRaFdeF; plus_cv=1::m:49a3f4a6; MSA_WH=400_655; lsv=globalTjs_3a11c3d-globalT_androidcss_4630b37-wwwT_androidcss_c5f9a54-searchboxcss_591d86b-globalBcss_aad48cc-wwwBcss_777000e-framejs_c9ac861-atomentryjs_5cd4b30-globalBjs_99ad350-wwwjs_b674808; BD_UPN=19314353; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BDICON=10294984.98; delPer=0; BD_CK_SAM=1; rsv_i=c2b6G%2F3avQC%2FfgLjK6Tg5dByzXJGjTHszykjx0XgYlZZgizi3%2F9wOVrzCucTWKLxPYYUs%2BqPpygizpeQMUWhVScLKRxzaaw; FEED_SIDS=732051_1030_14; plus_lsv=f197ee21ffd230fd; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1572225355,1572415847,1572418912; Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1572418912; BAIDULOC=12966109.384666294_4841881.341700486_100_131_1572418911981; SE_LAUNCH=5%3A26206981_0%3A26206981; BDPASSGATE=IlPT2AEptyoA_yiU4VKH3kIN8efjWvW4AfvESkplQFStfCaWmhH3BrUzWz0HSieXBDP6wZTXdMsDxXTqXlVXa_EqnBsZolpOaSaXzKGoucHtVM69-t5yILXoHUE2sA8PbRhL-3MEF2ZELlQvcgjchQZrchW8z3JTpxz1z5Xocc0T1UKR2VLJxJyTS7xvRHvcPNuz94rXnEpKKSmBUADHRVjYcSQyWXkD5NOtjsAm1Q0WrkoXGurSRvAa1G8vJpFeXAio1fWU60ul269v5HViViwh9UOI7u46MnJZ; H_WISE_SIDS=137151_137734_137755_136649_137663_137071_128070_134982_136665_120196_136768_137002_137788_136366_132909_136456_137690_135847_131246_137746_132378_136681_118893_118876_118846_118827_118802_132782_136800_136431_136093_133352_136862_137089_129652_136194_124637_137105_137572_133847_132551_137468_134046_129646_131423_137212_137466_136034_110085_127969_137613_131951_136611_137252_128196_137696_136636_137767_137207_134347_134231_137618_137449; kleck=638cabc3ad33a7a082343c4553a47c42; BDRCVFR[x4e6higC8W6]=mk3SLVN4HKm; PSINO=7; H_PS_PSSID=1440_21084_20697_29567_29220; sug=3; sugstore=0; ORIGIN=0; bdime=0; H_PS_645EC=db34IWhem1lYO7OwXVBPbsx2yQuIu3jmqGT9FUp09TItjsTj8omDTLnov6%2BIZQe6dqc',
        'Host':'www.baidu.com',
        'Upgrade-Insecure-Requests':'1'}
    q = BdpcRank1.read_txt('kwd_url.txt')
    f = open('bdpc_rank1.txt','w',encoding='utf-8')
    # 设置线程数
    for i in list(range(2)):
        t = BdpcRank1()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()

