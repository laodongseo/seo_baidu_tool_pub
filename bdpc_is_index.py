# ‐*‐ coding: utf‐8 ‐*‐
"""
准备url.txt,一行一个url,要加上https或者http
查询某个url是否收录，有收录再访问该url获取title，查询通过搜索title该url是否有排名
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue


class BdpcIndex(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取txt文件 获取待查询url
    @staticmethod
    def read_txt(filepath):
        q = queue.Queue()
        for url in open(filepath, encoding='utf-8'):
            url = url.strip()
            q.put(url)
        return q

    # 获取某待查询url的title
    def get_title(self, url):
        html = self.get_html(url)
        if html:
            doc = pq(html)
            title = doc('title').text()
            return title

    # 获取某待查询url或某词的serp源码
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

    # 获取某待查询url或某词的serp源码上10条加密url
    def get_encrpt_urls(self, html):
        encrypt_url_list = []
        if html and '_百度搜索' in html:
            doc = pq(html)
            try:
                a_list = doc('.t a').items()
            except Exception as e:
                print('未找到加密url,链接未收录', e)
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

    # 获取某待查询url或某词的serp源码首页真实url
    def get_real_urls(self, encrypt_url_list):
        if encrypt_url_list:
            real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
            return real_url_list
        else:
            return []

    # 检查链接是否有收录
    def check_include(self, url, real_urls):
        if url in real_urls:
            return 1
        else:
            return 0

    # 线程函数
    def run(self):
        while 1:
            target_url = q.get()
            print('查询', target_url)
            # 查询该target_url是否收录
            url = "https://www.baidu.com/s?ie=utf-8&wd={0}".format(target_url)
            html = self.get_html(url)
            encrypt_url_list = self.get_encrpt_urls(html)
            real_urls = self.get_real_urls(encrypt_url_list)
            num_target_url = self.check_include(target_url, real_urls)
            # 有收录则判断是否索引
            if num_target_url == 1:
                # 查询该target_url的title 检查是否有索引
                title = self.get_title(target_url)
                url = "https://www.baidu.com/s?ie=utf-8&wd={0}".format(title)
                html = self.get_html(url)
                encrypt_url_list = self.get_encrpt_urls(html)
                real_urls = self.get_real_urls(encrypt_url_list)
                num_title = self.check_include(target_url, real_urls)
                if num_title == 1:
                    print("收录且索引")
                    f.write(target_url+'\t'+'收录且索引\n')
                elif num_title == 0:
                    print("收录无索引")
                    f.write(target_url + '\t' + '收录无索引\n')
            elif num_target_url == 0:
                print("无收录")
                f.write(target_url + '\t' + '无收录\n')
            q.task_done()


if __name__ == "__main__":

    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    q = BdpcIndex.read_txt('url.txt')
    f = open('bdpc_index.txt','w',encoding='utf-8')
    # 设置线程数
    for i in list(range(6)):
        t = BdpcIndex()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()

