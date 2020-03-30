# ‐*‐ coding: utf‐8 ‐*‐
"""
kwd.txt,一行一个关键词
采集相关搜索词
默认线程2
(cookie用自己登陆账号后的cookie否则很容易被反爬)
"""
import requests
import threading
import queue
from pyquery import PyQuery as pq
import time
import gc


# 获取某词serp源码
def get_html(url, retry=2):
    try:
        r = requests.get(url=url, headers=my_header, timeout=5)
    except Exception as e:
        print('获取源码失败', e)
        time.sleep(6)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.content.decode('utf-8', errors='ignore')  # 用r.text有时候识别错误
        url = r.url  # 反爬会重定向,取定向后的地址
        return html, url


# 提取相关词
def get_kwds(html,url):
    kwds = []
    doc = pq(html)  # 偶尔有问题,强制转str
    title = doc('title').text()
    if '_百度搜索' in title and 'https://www.baidu.com/s?tn=48020221' in url:
        # 无相关搜索,不会报错
        xg_kwds = doc('#rs table tr th a').items()
        for kwd_xg in xg_kwds:
            kwd_xg = kwd_xg.text()
            kwds.append(kwd_xg)
    else:
        print('源码异常,可能反爬')
    return kwds


# 线程函数
def main():
    while 1:
        kwd = q.get()
        url = 'https://www.baidu.com/s?tn=48020221_28_hao_pg&ie=utf-8&wd={}'.format(kwd)
        try:
            html,now_url = get_html(url)
            kwds = get_kwds(html,now_url)
        except Exception as e:
            print(e)
        else:
            for kwd in kwds:
                f.write(kwd + '\n')
                print(kwd)
            f.flush()
        finally:
            del kwd,url
            gc.collect()
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
    my_header = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding':'deflate',
'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'BIDUPSID=34AD203382E590D3153BF7821B242D36; PSTM=1585537234; BAIDUID=34AD203382E590D391F5ADBFBDC790BD:FG=1; BD_HOME=1; BD_UPN=12314353; delPer=0; BD_CK_SAM=1; PSINO=7; H_PS_PSSID=30963_1430_31118_21081_31186_30823_31195; H_PS_645EC=e5c8J2vTZkZ7EhteM%2BYya8xRZ2c6EDA2g0XET1wKfuu9eEQcRmsx6WxjTeQ; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSVRTM=241; COOKIE_SESSION=0_0_1_0_0_3_0_0_0_1_2_0_0_0_0_0_0_0_1585537243%7C1%230_0_1585537243%7C1',
'Host':'www.baidu.com',
'Sec-Fetch-Dest':'document',
'Sec-Fetch-Mode':'navigate',
'Sec-Fetch-Site':'same-origin',
'Sec-Fetch-User':'?1',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        }
    # 设置线程数
    for i in list(range(2)):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
