# ‐*‐ coding: utf‐8 ‐*‐
# 事先准备excel文件，每个sheet存储一类关键词，sheet名字即关键词分类

from openpyxl import Workbook
from openpyxl import load_workbook
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time

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

    # 获取某词serp源码
    def get_html(self,url,retry=2):
        try:
            r = requests.get(url=url,headers=user_agent,timeout=5)
        except Exception as e:
            print('获取源码失败',url,e)
            if retry > 0:
                self.get_html(url,retry-1)
        else:
            html = r.text
            return html

    # 获取某词serp源码上10条加密url
    def get_encrpt_urls(self,url):
        encrypt_url_list = []
        html = self.get_html(url)
        if html and '_百度搜索' in html:
            doc = pq(html)
            try:
                a_list = doc('.t a').items()
            except Exception as e:
                print('未提取到serp上的解密url', e, url)
            else:
                for a in a_list:
                    encrypt_url = a.attr('href')
                    if encrypt_url.find('http://www.baidu.com/link?url=') == 0:
                        encrypt_url_list.append(encrypt_url)
        return encrypt_url_list

    # 解密某词serp源码的加密url
    def decrypt_url(self,encrypt_url,retry=1):
        try:
            encrypt_url = encrypt_url.replace('http://','https://')
            r = requests.head(encrypt_url,headers=user_agent)
        except Exception as e:
            print(encrypt_url,'解密失败',e)
            if retry > 0:
                self.decrypt_url(encrypt_url,retry-1)
        else:
            return r.headers['Location']

    # 获取某词serp源码首页排名真实url
    def get_real_urls(self,url):
        encrypt_url_list = self.get_encrpt_urls(url)
        if encrypt_url_list:
            real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
            return real_url_list
        else:
            print('检查网页源代码',url)

    # 统计每个域名排名的词数
    def run(self):
        global success_num
        while 1:
            kwd_dict = q.get()
            # print(kwd_dict)
            for kwd,group in kwd_dict.items():
                url = "https://www.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
                real_urls = self.get_real_urls(url)
                if real_urls:
                    domain_str = ''.join(real_urls)
                    try:
                        threadLock.acquire()
                        success_num += 1
                        for domain in target_domain:
                            if domain in domain_str:
                                result[domain][group] += 1
                        print('查询成功{0}个'.format(success_num))
                    except Exception as e:
                        print(e)
                    finally:
                        print (kwd)
                        threadLock.release()
            q.task_done()

    # 保存数据
    @staticmethod
    def save():
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
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    threadLock = threading.Lock()  # 锁
    result = {}   # 结果保存字典
    success_num = 0  # 查询成功个数
    date = time.strftime("%Y-%m-%d", time.localtime()) # 询日期

    q,group_list = bdpcMonitor.read_excel('kwd.xlsx')
    bdpcMonitor.result_init(group_list)
    all_num = q.qsize()

    # 设置线程数
    for i in list(range(10)):
        t = bdpcMonitor()
        t.setDaemon(True)
        t.start()
    q.join()

    bdpcMonitor.save()
    end = time.time()
    print('\n关键词共{0}个,查询成功{1}个,耗时{2}min'.format(all_num,success_num,(end-start)/60) )
    print('结果为\n', result)