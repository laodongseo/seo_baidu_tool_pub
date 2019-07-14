# ‐*‐ coding: utf‐8 ‐*‐
"""
一个关键词serp上同一个域名出现N个url排名 计算N次
准备kwd.txt
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
from urllib.parse import urlparse
import gc
import json

class bdmoCover(threading.Thread):

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

    # 获取某词的serp源码上包含排名url的div块
    def get_data_logs(self, html):
        data_logs = []
        if html and '百度' in html:
            doc = pq(html)
            try:
                div_list = doc('.c-result').items()
            except Exception as e:
                print('提取div块失败', e)
            else:
                for div in div_list:
                    data_log = div.attr('data-log')
                    data_logs.append(data_log) if data_log is not None else data_logs
        return data_logs

    # 提取排名的真实url
    def get_real_urls(self, data_logs=[]):
        real_urls = []
        for data_log in data_logs:
            # json字符串要以双引号表示
            data_log = json.loads(data_log.replace("'", '"'))
            url = data_log['mu']
            real_urls.append(url)
        return real_urls

    # 提取某条url域名部分
    def get_domain(self,real_url):

        # 通过mu提取url有些非自然排名url是空
        try:
           res = urlparse(real_url)  # real_url为空不会报错
        except Exception as e:
           print (e,real_url)
           domain = "xxx"
        else:
           domain = res.netloc
        return domain

    # 获取某词serp源码首页排名真实url的域名部分
    def get_domains(self,real_urls):
            domain_list = [self.get_domain(real_url) for real_url in real_urls]
            # 搜一个词 同一个域名多个url出现排名 只计算一次
            return domain_list

    # 线程函数
    def run(self):
        global success_num
        while 1:
            kwd = q.get()
            url = "https://m.baidu.com/s?ie=utf-8&word={0}".format(kwd)
            try:
                html = self.get_html(url)
                data_logs = self.get_data_logs(html)
                real_urls = self.get_real_urls(data_logs)
                domain_list = self.get_domains(real_urls)
                if domain_list:
                    try:
                        threadLock.acquire()
                        for domain in domain_list:
                            result[domain] = result[domain]+1 if domain in result else 1
                        success_num += 1
                        print('查询成功{0}个'.format(success_num))
                    finally:
                        threadLock.release()
                del kwd
                gc.collect()
            except Exception as e:
                print(e)
            finally:
                q.task_done()

    # 保存数据
    @staticmethod
    def save():
        print ('开始save.....')
        res_sort = sorted(result.items(), key=lambda s: s[1], reverse=True)
        print(res_sort)
        with open('bdmo_result1.txt','w',encoding="utf-8") as f:
            for domain,value in res_sort:
                    f.write(str(domain)+'\t'+str(value)+'\n')


if __name__ == "__main__":
    start = time.time()

    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; ALP-AL00 Build/HUAWEIALP-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.11 (Baidu; P1 8.1.0)'}
    threadLock = threading.Lock()  # 锁
    result = {}   # 初始结果保存字典
    success_num = 0  # 查询成功个数
    q = bdmoCover.read_file('kwd.txt')
    all_num = q.qsize() #总词数

    # 设置线程数
    for i in list(range(6)):
        t = bdmoCover()
        t.setDaemon(True)
        t.start()
    q.join()

    # 结果保存文件
    bdmoCover.save()
    end = time.time()
    print('\n关键词共{0}个,查询成功{1}个,耗时{2}min'.format(all_num,success_num,(end-start)/60) )
