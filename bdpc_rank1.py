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


class BdpcRank(threading.Thread):

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

    # 获取某词的serp源码上自然排名的所有url
    def get_encrpt_urls(self, html):
        encrypt_url_list = []
        if html and '_百度搜索' in html:
            doc = pq(html)
            try:
                a_list = doc('.t a').items()
            except Exception as e:
                print('未找到加密url,源码获取失败', e)
            else:
                for a in a_list:
                    encrypt_url = a.attr('href')
                    if encrypt_url.find('http://www.baidu.com/link?url=') == 0:
                        encrypt_url_list.append(encrypt_url)
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
            return r.headers['Location']

    # 获取某词的serp源码首页真实url
    def get_real_urls(self, encrypt_url_list):
        if encrypt_url_list:
            real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
            return real_url_list
        else:
            return []

    # 检查链接是否首页有排名
    def check_include(self, url, real_urls):
        rank = 0
        if url not in  real_urls:
            return '无'
        else:
            for target_url in real_urls:
                rank += 1
                if url == target_url:
                    return rank

    # 线程函数
    def run(self):
        while 1:
            kwd_url = q.get()
            kwd = kwd_url[0]
            url_check = kwd_url[1]
            url = "https://www.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
            html = self.get_html(url)
            encrypt_url_list = self.get_encrpt_urls(html)
            real_urls = self.get_real_urls(encrypt_url_list)
            rank = self.check_include(url_check, real_urls)
            print(kwd,url_check,rank)
            f.write(kwd+'\t'+url_check+'\t'+str(rank)+'\n')

            q.task_done()


if __name__ == "__main__":

    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    q = BdpcRank.read_txt('kwd_url.txt')
    f = open('bdpc_rank1.txt','w',encoding='utf-8')
    # 设置线程数
    for i in list(range(6)):
        t = BdpcRank()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()

