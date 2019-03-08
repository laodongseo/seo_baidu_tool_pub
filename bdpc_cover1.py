# ‐*‐ coding: utf‐8 ‐*‐
"""
一个关键词 serp上同一个域名出现N个url排名 则计算N次
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
from urllib.parse import urlparse

class bdpcCover(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取txt文件 关键词进入队列
    @staticmethod
    def read_file(filepath):
        q = queue.Queue()
        for kwd in open(filepath,encoding='utf-8'):
            kwd = kwd.strip()
            q.put(kwd)
        return q

    # 获取某词serp源码
    def get_html(self,url,retry=2):
        try:
            r = requests.get(url=url,headers=user_agent,timeout=5)
        except Exception as e:
            print('获取源码失败',e)
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

    # 解密某条加密url
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

    # 统计函数
    def get_domains(self,url):
        res_url = self.get_real_urls(url)
        if res_url:
            for url in res_url:
                try:
                  res = urlparse(url)
                except Exception as e:
                  print (e,url)
                else:
                  domain = res.netloc
                if domain in result:
                    result[domain]+=1
                else:
                    result[domain]=1

    # 线程函数
    def run(self):
        global success_num
        while 1:
            kwd = q.get()
            url = "https://www.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
            try:
                threadLock.acquire()
                self.get_domains(url)
                success_num += 1
                print('查询成功{0}个'.format(success_num))
            except Exception as e:
                print(e)
            finally:
                print (kwd,'查询结束')
                threadLock.release()
            q.task_done()

    # 保存数据
    @staticmethod
    def save():
        print ('开始save.....')
        res_sort = sorted(result.items(), key=lambda s: s[1], reverse=True)
        with open('result1.txt','w',encoding="utf-8") as f:
            for domain,value in res_sort:
                    f.write(domain+'\t'+str(value)+'\n')


if __name__ == "__main__":
    start = time.time()

    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'}
    threadLock = threading.Lock()  # 锁
    result = {}   # 初始结果保存字典
    success_num = 0  # 查询成功个数
    q = bdpcCover.read_file('kwd.txt')
    all_num = q.qsize() #总词数

    # 设置线程数
    for i in list(range(5)):
        t = bdpcCover()
        t.setDaemon(True)
        t.start()
    q.join()

    # 结果保存文件
    bdpcCover.save()
    end = time.time()
    print('\n关键词共{0}个,查询成功{1}个,耗时{2}min'.format(all_num,success_num,(end-start)/60) )
    print('结果为\n', result)