# ‐*‐ coding: utf‐8 ‐*‐
"""
excel文件kwd.xlsx,sheet名字即关键词分类名,sheet第一列是关键词
指定一批词,指定几个目标域名,监控这批词目标域名首页词各有多少
如果某词某域名首页有N个url排名,计为1个
默认线程2,cookie必须为登陆账号后的cookie
"""

from openpyxl import load_workbook
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import gc


class bdpcMonitor(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取excel文件 做好关键词分类
    @staticmethod
    def read_excel(filepath):
        q = queue.Queue()
        group_list = []
        wb_kwd = load_workbook(filepath)
        for sheet_obj in wb_kwd:
            sheet_name = sheet_obj.title
            group_list.append(sheet_name)
            col_a = sheet_obj['A']
            for cell in col_a:
                 kwd = (cell.value)
                 q.put({kwd:sheet_name})
        return q,group_list

    # 初始化结果字典
    @staticmethod
    def result_init(group_list):
        for domain in target_domain:
            result[domain] = {}
            for group in group_list:
                result[domain][group] = 0
        print("初始化结果字典成功")

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

    # 获取某词serp源码首页排名真实url
    def get_real_urls(self,encrypt_url_list):
        if encrypt_url_list:
            real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
            return real_url_list
        else:
            return []

    # 统计每个域名排名的词数
    def run(self):
        global success_num
        while 1:
            kwd_dict = q.get()
            kwd,group = list(kwd_dict.items())[0]
            try:
                url = "https://www.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
                html,now_url = self.get_html(url)
                encrypt_url_list = self.get_encrpt_urls(html,now_url)
                real_urls = self.get_real_urls(encrypt_url_list)
                if real_urls:
                    # 干掉None 防止列表转字符串出错
                    set_real_urls = set(real_urls)
                    real_urls = [i for i in set_real_urls]
                    real_urls.remove(None) if None in real_urls else real_urls
                    # 某词serp排名的真实url合并为一个字符串
                    domain_str = ''.join(real_urls)
            except Exception as e:
                print(e)
            else:
                if domain_str:
                    threadLock.acquire()
                    success_num += 1
                    for domain in target_domain:
                        if domain in domain_str:
                            result[domain][group] += 1
                    threadLock.release()
                    print('查询成功{0}个'.format(success_num))
            finally:
                del kwd, group
                gc.collect()
                q.task_done()

    # 保存数据
    @staticmethod
    def save():
        print(result)
        print ('开始save.....')
        with open('result.txt','w',encoding="utf-8") as f:
            for domain,data_dict in result.items():
                for key,value in data_dict.items():
                    f.write(date+'\t'+domain+ '\t'+key+'\t'+str(value)+'\n')


if __name__ == "__main__":
    start = time.time()

    # 全局变量 待监控域名列表
    target_domain = ['www.renrenche.com','www.guazi.com','www.che168.com',
                     'www.iautos.cn','so.iautos.cn','www.hx2car.com','58.com',

                     'taoche.com','www.51auto.com','www.xin.com']
    my_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Cookie': 'BIDUPSID=EB1F44AB7896D7EFA4F0FD243C29FF17; PSTM=1567562976; BAIDUID=EB1F44AB7896D7EFA4F0FD243C29FF17:SL=0:NR=10:FG=1; BDUSS=BZWlZuSXpNWmNjM3BTSktnM2xhbGhIdUlqeW1ITEdvclpzSHpIS3p2WUMwc2hkRVFBQUFBJCQAAAAAAAAAAAEAAAAGtiZkNzcyNDgzMjAwZG9uZwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJFoV0CRaFdeF; plus_cv=1::m:49a3f4a6; MSA_WH=400_655; lsv=globalTjs_3a11c3d-globalT_androidcss_4630b37-wwwT_androidcss_c5f9a54-searchboxcss_591d86b-globalBcss_aad48cc-wwwBcss_777000e-framejs_c9ac861-atomentryjs_5cd4b30-globalBjs_99ad350-wwwjs_b674808; BD_UPN=19314353; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BDICON=10294984.98; delPer=0; BD_CK_SAM=1; rsv_i=c2b6G%2F3avQC%2FfgLjK6Tg5dByzXJGjTHszykjx0XgYlZZgizi3%2F9wOVrzCucTWKLxPYYUs%2BqPpygizpeQMUWhVScLKRxzaaw; FEED_SIDS=732051_1030_14; plus_lsv=f197ee21ffd230fd; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1572225355,1572415847,1572418912; Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1572418912; BAIDULOC=12966109.384666294_4841881.341700486_100_131_1572418911981; SE_LAUNCH=5%3A26206981_0%3A26206981; BDPASSGATE=IlPT2AEptyoA_yiU4VKH3kIN8efjWvW4AfvESkplQFStfCaWmhH3BrUzWz0HSieXBDP6wZTXdMsDxXTqXlVXa_EqnBsZolpOaSaXzKGoucHtVM69-t5yILXoHUE2sA8PbRhL-3MEF2ZELlQvcgjchQZrchW8z3JTpxz1z5Xocc0T1UKR2VLJxJyTS7xvRHvcPNuz94rXnEpKKSmBUADHRVjYcSQyWXkD5NOtjsAm1Q0WrkoXGurSRvAa1G8vJpFeXAio1fWU60ul269v5HViViwh9UOI7u46MnJZ; H_WISE_SIDS=137151_137734_137755_136649_137663_137071_128070_134982_136665_120196_136768_137002_137788_136366_132909_136456_137690_135847_131246_137746_132378_136681_118893_118876_118846_118827_118802_132782_136800_136431_136093_133352_136862_137089_129652_136194_124637_137105_137572_133847_132551_137468_134046_129646_131423_137212_137466_136034_110085_127969_137613_131951_136611_137252_128196_137696_136636_137767_137207_134347_134231_137618_137449; kleck=638cabc3ad33a7a082343c4553a47c42; BDRCVFR[x4e6higC8W6]=mk3SLVN4HKm; PSINO=7; H_PS_PSSID=1440_21084_20697_29567_29220; sug=3; sugstore=0; ORIGIN=0; bdime=0; H_PS_645EC=db34IWhem1lYO7OwXVBPbsx2yQuIu3jmqGT9FUp09TItjsTj8omDTLnov6%2BIZQe6dqc',
        'Host': 'www.baidu.com',
        'Upgrade-Insecure-Requests': '1'
        }
    threadLock = threading.Lock()  # 锁
    result = {}   # 结果保存字典
    success_num = 0  # 查询成功个数
    date = time.strftime("%Y-%m-%d", time.localtime()) # 查询日期

    q,group_list = bdpcMonitor.read_excel('kwd.xlsx')
    bdpcMonitor.result_init(group_list)
    all_num = q.qsize()

    # 设置线程数
    for i in list(range(1)):
        t = bdpcMonitor()
        t.setDaemon(True)
        t.start()
    q.join()

    bdpcMonitor.save()
    end = time.time()
    print('关键词共{0}个,查询成功{1}个,耗时{2}min'.format(all_num,success_num,(end-start)/60) )
