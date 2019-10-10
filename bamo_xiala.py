# ‐*‐ coding: utf‐8 ‐*‐
"""
百度移动下拉词
"""
# python3.6版本
import requests
import threading
import queue
import time
import json

# 获取源码
def get_html(url,retry=2):
    try:
        r = requests.get(url=url,headers=user_agent, timeout=5)
    except Exception as e:
        print('获取源码失败', url, e)
        time.sleep(5)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.text
        return html


# 提取相关词+其他人还在搜
def get_kwds(html):
    xiala_kwds = []
    if html and 'jsonp7' in html:
        html = html.replace('jsonp7(','').replace(')','')
        html = json.loads(html)
        dicts = html['g']
        for dic in dicts:
            kwd = dic['q']
            xiala_kwds.append(kwd)
        xiala_kwds.append(kwd)
    return xiala_kwds


def main():
    while 1:
        kwd = q.get()
        url = "https://m.baidu.com/sugrec?pre=1&p=3&ie=utf-8&json=1&prod=wise&from=wise_web&sp=&callback=jsonp7&wd={0}".format(kwd)
        try:
            html = get_html(url)
            xiala_kwds = get_kwds(html)
            print(len(xiala_kwds))
            for kwd in xiala_kwds:
                f.write(kwd + '\n')
            f.flush()
        except Exception as e:
            print(e)
        finally:
            q.task_done()



if __name__ == "__main__":
    # 结果保存文件
    f = open('bdmo_xiala.txt','w',encoding='utf-8')
    # 关键词队列
    q = queue.Queue()
    for kwd in open('head.txt','r',encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)
    # UA设置
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Mobile Safari/537.36'}
    # 设置线程数
    for i in list(range(6)):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
