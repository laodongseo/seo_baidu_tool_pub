# ‐*‐ coding: utf‐8 ‐*‐
"""
准备kwd.txt,一行一个
包含xxx相关网站  其他人还在搜 不含百家号和智能搜索推荐
自行修改线程数
python3.7
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue


class BdmoIntitle(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取kwd.txt文件
    @staticmethod
    def read_txt(filepath):
        q = queue.Queue()
        for kwd in open(filepath, encoding='utf-8'):
            kwd = kwd.strip()
            q.put(kwd)
        return q

    # 获取某词的serp源码
    def get_html(self, url, user_agent, retry=2):
        try:
            r = requests.get(url=url, headers=user_agent, timeout=5)
        except Exception as e:
            print('获取源码失败', url, e)
            if retry > 0:
                self.get_html(url, user_agent, retry - 1)
        else:
            html = r.text
            return html

    # 获取serp源码上所有的title(包含 其他人还搜)
    def get_titles(self,html):
        title_list = []
        if html:
            doc = pq(html)
            title_items = doc('#results .c-result-content h3').items()
            for title in title_items:
                title_list.append(title.text())
        return title_list

    # 线程函数
    def run(self):
        while 1:
            kwd = q.get()
            url = "https://m.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
            html = self.get_html(url,user_agent)
            title_list = self.get_titles(html)
            try:
                threadLock.acquire()
                num = 0
                for title in title_list:
                    if kwd in title:
                        num += 1
                print(kwd,num)
                f.write(kwd + '\t' + str(num) + '\n')
            except Exception as e:
                print(e)
            finally:
                threadLock.release()
            q.task_done()


if __name__ == "__main__":

    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; ALP-AL00 Build/HUAWEIALP-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.11 (Baidu; P1 8.1.0)'}
    threadLock = threading.Lock()  # 锁
    q = BdmoIntitle.read_txt('kwd.txt')
    f = open('bdmo_kwd_intitle.txt','w',encoding='utf-8')
    # 设置线程数
    for i in list(range(10)):
        t = BdmoIntitle()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()

