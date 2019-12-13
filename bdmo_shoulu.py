# ‐*‐ coding: utf‐8 ‐*‐
"""
查询某个url是否收录
准备mo_url.txt,一行一个url,必须带http或https
区分https或者http
区分https://aaa/bbb和https://aaa/bbb/
(header头信息放你自己登录账号后的cookie,否则很容易被反爬)
线程数灵活调整
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import json
import time
import gc


class BdmoShoulu(threading.Thread):

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
    def get_html(self,url,retry=2):
        try:
            r = requests.get(url=url,headers=my_header,timeout=5)
        except Exception as e:
            print('获取源码失败',e)
            time.sleep(6)
            if retry > 0:
                self.get_html(url,retry-1)
        else:
            html = r.content.decode('utf-8',errors='ignore')  # 用r.text有时候识别错误
            url = r.url  # 反爬会重定向,取定向后的地址
            return html,url

    # 获取某词的serp源码上包含排名url的div块
    def get_data_logs(self, html ,url):
        data_logs = []
        doc = pq(html)
        title = doc('title').text()
        if '- 百度' in title and 'https://m.baidu.com/s?ie=utf-8' in url:
            try:
                div_list = doc('.c-result').items()
            except Exception as e:
                print('提取div块失败', e)
            else:
                for div in div_list:
                    data_log = div.attr('data-log')
                    data_logs.append(data_log) if data_log is not None else data_logs
        else:
            print(title,'源码异常,可能反爬')
        return data_logs

    # 获取serp上排名的真实url
    def get_real_urls(self, data_logs):
        real_urls = []
        for data_log in data_logs:
            # json字符串要以双引号表示
            data_log = json.loads(data_log.replace("'", '"'))
            url = data_log['mu']
            real_urls.append(url)
        return real_urls

    # 线程函数
    def run(self):
        global shoulu_num
        while 1:
            target_url = q.get()
            url = "https://m.baidu.com/s?ie=utf-8&word={0}".format(target_url)
            try:
                html,now_url = self.get_html(url)
                data_logs = self.get_data_logs(html,now_url)
                real_urls = self.get_real_urls(data_logs)
            except Exception as e:
                print(e)
            else:
                if target_url in real_urls:
                    lock.acquire()  # 加锁
                    shoulu_num += 1
                    lock.release()  # 释放
                    print(target_url,'收录')
                    f.write(target_url + '\t收录'+ '\n')
                else:
                    print(target_url, '未收录')
                    f.write(target_url + '\t未收录' + '\n')                
            finally:
                f.flush()
                del target_url
                gc.collect()
                q.task_done()


if __name__ == "__main__":

    start = time.time()
    shoulu_num = 0
    lock = threading.Lock() # 创建锁
    # 结果保存文件
    f = open('bdmo_shoulu.txt','w',encoding='utf-8')
    # head设置
    my_header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; ALP-AL00 Build/HUAWEIALP-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.11 (Baidu; P1 8.1.0)',
        'cookie':'BDUSS=GZpaXJQdn5DU1VhcnV3eXV5WjhpRmozQ2ticVFZRlQ4MlpoZkRLdWlzZzB5WU5aSVFBQUFBJCQAAAAAAAAAAAEAAAD2J3Kt07S8yLnFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQ8XFk0PFxZb'
    }
    # url队列
    q = BdmoShoulu.read_txt('mo_url.txt')
    # 设置线程数
    for i in list(range(3)):
        t = BdmoShoulu()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
    end = time.time()
    print('耗时{0}min,收录{1}个'.format((end - start) / 60,shoulu_num))
