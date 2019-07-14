# ‐*‐ coding: utf‐8 ‐*‐
"""
 准备关键词文件kwd.txt 一行一个词
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import gc
import json


class BdmoReal(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取txt文件 获取待查询url
    @staticmethod
    def read_txt(filepath):
        q = queue.Queue()
        for line in open(filepath, encoding='utf-8'):
            kwd = line.strip()
            q.put(kwd)
        return q

    # 获取某词的serp源码
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

    # 获取排名真实url
    def get_real_urls(self,data_logs=[]):
        real_urls = []
        for data_log in data_logs:
            # json字符串要以双引号表示
            data_log = json.loads(data_log.replace("'", '"'))
            rank_url = data_log['mu']
            real_urls.append(rank_url)
        return real_urls


    # 线程函数
    def run(self):
        while 1:
            kwd = q.get()
            try:
                url = "https://m.baidu.com/s?ie=utf-8&word={0}".format(kwd)
                html = self.get_html(url)
                data_logs = self.get_data_logs(html)
                rank_urls = self.get_real_urls(data_logs)
                for url in rank_urls:
                    print(url)
                    f.write(url + '\t'+ '\n')
                del kwd
                gc.collect()
            except Exception as e:
                print(e)
            finally:
                q.task_done()

if __name__ == "__main__":
    # 结果保存文件
    f = open('bdmo_real_urls.txt','w',encoding='utf-8')
    # UA设置
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; ALP-AL00 Build/HUAWEIALP-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.11 (Baidu; P1 8.1.0)'}
    # 关键词队列
    q = BdmoReal.read_txt('kwd.txt')
    # 设置线程数
    for i in list(range(6)):
        t = BdmoReal()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()

