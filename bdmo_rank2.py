# ‐*‐ coding: utf‐8 ‐*‐
"""
关键词文件kwd.txt(一行一个) 仅查前十名
指定待查询域名domain
domain不要带https或者http
结果保存文件格式：关键词 对应排名的url 及排名值
如果一个词某个域名下有2个url出现排名 取第一个
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue
import gc
import json


class BdmoRank(threading.Thread):

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

    # 检查链接是否首页有排名
    def check_include(self,data_logs=[]):
        rank = None
        for data_log in data_logs:
            # json字符串要以双引号表示
            data_log = json.loads(data_log.replace("'", '"'))
            rank_url = data_log['mu']
            if doamin in rank_url:
                rank = data_log['order']
                print(rank_url,rank)
                return rank_url,rank
        return 'not url found',rank

    # 线程函数
    def run(self):
        while 1:
            kwd = q.get()
            try:
                url = "https://m.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
                html = self.get_html(url)
                data_logs = self.get_data_logs(html)
                rank_url,rank = self.check_include(data_logs)
                print(kwd,rank_url,rank)
                f.write(kwd + '\t' + rank_url+ '\t'+ str(rank) + '\n')
                del kwd
                gc.collect()
            except Exception as e:
                print(e)
            finally:
                q.task_done()


if __name__ == "__main__":

    doamin = 'renrenche.com'
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; ALP-AL00 Build/HUAWEIALP-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.11 (Baidu; P1 8.1.0)'}
    q = BdmoRank.read_txt('kwd.txt')
    f = open('bdmo_rank2.txt','w',encoding='utf-8')
    # 设置线程数
    for i in list(range(6)):
        t = BdmoRank()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()

