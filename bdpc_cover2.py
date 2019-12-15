# ‐*‐ coding: utf‐8 ‐*‐
"""
批量查行业词--提取首页排名url--计算各域名首页词数
一个关键词serp上同一个域名出现N个url排名 计算1次
默认线程2
请求头一定换成登陆账号后的cookie
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
from urllib.parse import urlparse
import gc


class bdpcCover(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取txt文件 关键词队列
    @staticmethod
    def read_file(filepath):
        q = queue.Queue()
        for kwd in open(filepath,encoding='utf-8'):
            kwd = kwd.strip()
            q.put(kwd)
        return q

    # 获取某词的serp源码
    def get_html(self, url, retry=2):
        try:
            r = requests.get(url=url, headers=my_header, timeout=5)
        except Exception as e:
            print('获取源码失败', e)
            time.sleep(6)
            if retry > 0:
                self.get_html(url, retry - 1)
        else:
            html = r.content.decode('utf-8', errors='ignore')  # 用r.text有时候识别错误
            url = r.url  # 反爬会重定向,取定向后的地址
        return html, url

    # 获取某待查询url的serp源码所有排名url
    def get_encrpt_urls(self, html, url):
        encrypt_url_list = []
        doc = pq(str(html))
        title = doc('title').text()
        if '_百度搜索' in title and 'https://www.baidu.com/s?ie=utf-8' in url:
            try:
                a_list = doc('.t a').items()
            except Exception as e:
                print('未提取到serp上的解密url', e)
            else:
                for a in a_list:
                    encrypt_url = a.attr('href')
                    if encrypt_url.find('http://www.baidu.com/link?url=') == 0:
                        encrypt_url_list.append(encrypt_url)
        else:
            print(title, '源码异常,可能反爬')
            time.sleep(100)
        return encrypt_url_list

    # 解密某条加密url
    def decrypt_url(self,encrypt_url,retry=1):
        real_url = None # 默认None
        try:
            encrypt_url = encrypt_url.replace('http://','https://')
            # print(encrypt_url)
            r = requests.head(encrypt_url,headers=my_header)
        except Exception as e:
            print(encrypt_url,'解密失败',e)
            time.sleep(6)
            if retry > 0:
                self.decrypt_url(encrypt_url,retry-1)
        else:
            real_url = r.headers['Location']
            return real_url

    # 获取结果页排名真实url
    def get_real_urls(self, encrypt_url_list):
        if encrypt_url_list:
            real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
            return real_url_list
        else:
            return []

    # 提取某条url域名部分
    def get_domain(self,real_url):
        try:
           res = urlparse(real_url)
        except Exception as e:
           print (e,real_url)
           domain = "xxx"
        else:
           domain = res.netloc
        return domain

    # 获取某词serp源码首页排名真实url的域名部分
    def get_domains(self,real_url_list):
            domain_list = [self.get_domain(real_url) for real_url in real_url_list]
            domain_set = set(domain_list) # 去重域名
            return domain_set

    # 线程函数
    def run(self):
        global success_num
        while 1:
            kwd = q.get()
            url = "https://www.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
            try:
                html,url = self.get_html(url)
                encrypt_url_list = self.get_encrpt_urls(html,url)
                real_url_list = self.get_real_urls(encrypt_url_list)
                for real_url in real_url_list:
                    f.write(real_url + '\n')
                f.flush()
                domain_set = self.get_domains(real_url_list)
            except Exception as e:
                print(e)
            else:
                if domain_set:
                    threadLock.acquire()
                    for domain in domain_set:
                        result[domain] = result[domain]+1 if domain in result else 1
                    success_num += 1
                    threadLock.release()
                    print('查询成功{0}个'.format(success_num))
            finally:
                del kwd
                gc.collect()
                q.task_done()

    # 保存数据
    @staticmethod
    def save(result):
        print ('开始save.....')
        res_sort = sorted(result.items(), key=lambda s: s[1], reverse=True)
        print(res_sort)
        with open('bdpc_result1.txt','w',encoding="utf-8") as f:
            for domain,value in res_sort:
                    f.write(str(domain)+'\t'+str(value)+'\n')


if __name__ == "__main__":
    start = time.time()
    f = open('bdpc_real.txt','w',encoding='utf-8') # 记录排名的url
    my_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Cookie': 'BIDUPSID=EB1F44AB7896D7EFA4F0FD243C29FF17; PSTM=1567562976; BAIDUID=EB1F44AB7896D7EFA4F0FD243C29FF17:SL=0:NR=10:FG=1; BDUSS=BZWlZuSXpNWmNjM3BTSktnM2xhbGhIdUlqeW1ITEdvclpzSHpIS3p2WUMwc2hkRVFBQUFBJCQAAAAAAAAAAAEAAAAGtiZkNzcyNDgzMjAwZG9uZwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJFoV0CRaFdeF; plus_cv=1::m:49a3f4a6; MSA_WH=400_655; lsv=globalTjs_3a11c3d-globalT_androidcss_4630b37-wwwT_androidcss_c5f9a54-searchboxcss_591d86b-globalBcss_aad48cc-wwwBcss_777000e-framejs_c9ac861-atomentryjs_5cd4b30-globalBjs_99ad350-wwwjs_b674808; BD_UPN=19314353; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BDICON=10294984.98; delPer=0; BD_CK_SAM=1; rsv_i=c2b6G%2F3avQC%2FfgLjK6Tg5dByzXJGjTHszykjx0XgYlZZgizi3%2F9wOVrzCucTWKLxPYYUs%2BqPpygizpeQMUWhVScLKRxzaaw; FEED_SIDS=732051_1030_14; plus_lsv=f197ee21ffd230fd; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1572225355,1572415847,1572418912; Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1572418912; BAIDULOC=12966109.384666294_4841881.341700486_100_131_1572418911981; SE_LAUNCH=5%3A26206981_0%3A26206981; BDPASSGATE=IlPT2AEptyoA_yiU4VKH3kIN8efjWvW4AfvESkplQFStfCaWmhH3BrUzWz0HSieXBDP6wZTXdMsDxXTqXlVXa_EqnBsZolpOaSaXzKGoucHtVM69-t5yILXoHUE2sA8PbRhL-3MEF2ZELlQvcgjchQZrchW8z3JTpxz1z5Xocc0T1UKR2VLJxJyTS7xvRHvcPNuz94rXnEpKKSmBUADHRVjYcSQyWXkD5NOtjsAm1Q0WrkoXGurSRvAa1G8vJpFeXAio1fWU60ul269v5HViViwh9UOI7u46MnJZ; H_WISE_SIDS=137151_137734_137755_136649_137663_137071_128070_134982_136665_120196_136768_137002_137788_136366_132909_136456_137690_135847_131246_137746_132378_136681_118893_118876_118846_118827_118802_132782_136800_136431_136093_133352_136862_137089_129652_136194_124637_137105_137572_133847_132551_137468_134046_129646_131423_137212_137466_136034_110085_127969_137613_131951_136611_137252_128196_137696_136636_137767_137207_134347_134231_137618_137449; kleck=638cabc3ad33a7a082343c4553a47c42; BDRCVFR[x4e6higC8W6]=mk3SLVN4HKm; PSINO=7; H_PS_PSSID=1440_21084_20697_29567_29220; sug=3; sugstore=0; ORIGIN=0; bdime=0; H_PS_645EC=db34IWhem1lYO7OwXVBPbsx2yQuIu3jmqGT9FUp09TItjsTj8omDTLnov6%2BIZQe6dqc',
        'Host': 'www.baidu.com',
        'Upgrade-Insecure-Requests': '1'
        }
    threadLock = threading.Lock()  # 锁
    result = {}   # 初始结果保存字典
    success_num = 0  # 查询成功个数
    q = bdpcCover.read_file('kwd.txt')
    all_num = q.qsize() # 总词数

    # 设置线程数
    for i in list(range(2)):
        t = bdpcCover()
        t.setDaemon(True)
        t.start()
    q.join()

    # 结果保存文件
    bdpcCover.save(result)
    f.flush()
    f.close()
    end = time.time()
    print('\n关键词共{0}个,查询成功{1}个,耗时{2}min'.format(all_num,success_num,(end-start)/60) )
