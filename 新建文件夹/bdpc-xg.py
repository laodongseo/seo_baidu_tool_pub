# ‐*‐ coding: utf‐8 ‐*‐
# python3.7版本
import requests
import threading
import queue
from pyquery import PyQuery as pq

# 获取某词下拉地址源码
def get_html(url,retry=2):
    try:
        r = requests.get(url=url,headers=user_agent, timeout=5)
    except Exception as e:
        print('获取源码失败', url, e)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.text
        return html


# 提取相关词
def get_xgkwds():
    while 1:
        kwd = q.get()
        url = 'https://www.baidu.com/s?ie=utf-8&wd={}'.format(kwd)
        html = get_html(url)
        if html and '_百度搜索' in html:
            doc = pq(html)
            try:
                xg_kwds = doc('#rs table tr th a').items()
                # print(xg_kwds)
            except Exception as e:
                print(e)
            else:
                for kwd_xg in xg_kwds:
                    kwd_xg = kwd_xg.text()
                    print(kwd_xg)
                    f.write(kwd_xg+'\n')
        q.task_done()


if __name__ == "__main__":
    # 结果保存文件
    f = open('bdpc_xg.txt','w',encoding='utf-8')
    # 关键词队列
    q = queue.Queue()
    for kwd in open('kwd.txt',encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)
    # UA设置
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    # 设置线程数
    for i in list(range(5)):
        t = threading.Thread(target=get_xgkwds)
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
