# ‐*‐ coding: utf‐8 ‐*‐
"""
百度移动端相关词和其他人还在搜
"""
# python3.6版本
import requests
import threading
import queue
from pyquery import PyQuery as pq
import time

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
    xg_kwds = []
    qita_kwds = []
    if html and '百度' in html:
        doc = pq(html)
        # 获取相关搜索
        xg_list = doc('.rw-list a').items()
        for a in xg_list:
            text = a.text()
            xg_kwds.append(text)

         # 获取其他人还在搜
        div_list =doc('.c-result').items()
        for div in div_list:
            if div.attr('tpl') == 'recommend_list':
                a_list = div('section .c-row a').items()
                for a in a_list:
                    text = a.text()
                    qita_kwds.append(text)
                break
    xg_kwds.extend(qita_kwds)
    return xg_kwds


def main():
    while 1:
        kwd = q.get()
        # kwd = '怎么定义共有产权房'
        url = "https://m.baidu.com/s?ie=utf-8&word={0}".format(kwd)
        try:
            html = get_html(url)
            kwds = get_kwds(html)
            print(kwd,len(kwds))
            for kwd in kwds:
                f.write(kwd + '\n')
            f.flush()
        except Exception as e:
            print(e)
        finally:
            q.task_done()



if __name__ == "__main__":
    # 结果保存文件
    f = open('bdmo_xgqita.txt','w',encoding='utf-8')
    # 关键词队列
    q = queue.Queue()
    for kwd in open('kwd.txt','r',encoding='utf-8'):
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
