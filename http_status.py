#‐*‐coding:utf‐8‐*‐
import requests
import threading
import queue
import random
import re
import time
import pandas as pd

def read_excel(excelpath):
    q = queue.Queue()
    series_kwd = pd.read_excel(excelpath,usecols=['小区url'])['小区url']
    for name,kwd in series_kwd.items():
        q.put(kwd.strip())
    return q


# 获取某词serp源码
def get_status(url,retry=0):
    try:
        r = requests.head(url=url,headers=pc_header, timeout=10)
    except Exception as e:
        print('获取源码失败', 1-retry,url, e)
        q.put(url)
        time.sleep(20)
        if retry > 0:
            get_status(url, retry - 1)
    else:
        status = r.status_code 
        return status


def main():
    while 1:
        url = q.get()
        status = get_status(url)
        if not status:
            q.task_done()
            q.put(url)
            continue
        f.write(f'{url}\t{status}\n')
        f.flush()
        print(status)
        q.task_done()
        # time.sleep(1)


if __name__ == "__main__":
    # 结果保存文件
    f = open('http_status.txt', 'w', encoding='utf-8')
    pc_header = {
            'User-Agent':'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'

        }
    mo_header = {'User-Agent':'Mozilla/5.0 (Linux;u;Android 4.2.2;zh-cn;) AppleWebKit/534.46 (KHTML,like Gecko) Version/5.1 Mobile Safari/10600.6.3 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)'}
    # url队列
    q = read_excel(r'E:\py3script-工作\5i5j\x小区词导出\xiaoqu词手工.xlsx')
    # 线程数
    for i in list(range(1)):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
    q.join()
    f.close()
