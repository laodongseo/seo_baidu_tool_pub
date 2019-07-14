# ‐*‐ coding: utf‐8 ‐*‐
"""
kwd和url一对一查询 仅查前十名
kwd_url.txt,每行关键词和url一对,中间用制表符(直接从excel复制)隔开,url必须加http或者https
区分http和https
区分http://aaa/bbb/和http://aaa/bbb
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
            kwd_url = line.strip().split('\t')
            q.put(kwd_url)
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
    def check_include(self, url, data_logs=[]):
        rank = None
        for data_log in data_logs:
            # json字符串要以双引号表示
            data_log = json.loads(data_log.replace("'", '"'))
            if url == data_log['mu']:
                rank = data_log['order']
                return url,rank
        return url,rank

    # 线程函数
    def run(self):
        while 1:
            kwd_url = q.get()
            try:
                kwd = kwd_url[0]
                url_check = kwd_url[1]
                url = "https://m.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
                html = self.get_html(url)
                data_logs = self.get_data_logs(html)
                url,rank = self.check_include(url_check,data_logs)
                print(url,rank)
                f.write(url + '\t' + str(rank) + '\n')
                del kwd
                del url_check
                gc.collect()
            except Exception as e:
                print(e)
            finally:
                q.task_done()


if __name__ == "__main__":

    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36'}
    q = BdmoRank.read_txt('kwd_url.txt')
    f = open('bdmo_rank1.txt','w',encoding='utf-8')
    # 设置线程数
    for i in list(range(6)):
        t = BdmoRank()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()

