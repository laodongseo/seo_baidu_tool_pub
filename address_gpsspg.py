#‐*‐coding:utf‐8‐*‐
"""
某个地址获取经纬度qq地图
"""
import requests
import threading
import queue
import random
import time
import re
import json


# 获取某词serp源码
def get_html(url,retry=2):
    time.sleep(random.random())
    try:
        user_agent = random.choice(UA)
        r = requests.get(url=url,headers=user_agent, timeout=5)
    except Exception as e:
        print('获取源码失败', url, e)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.text
        return html


def get_info(html):
    if html and html['info']['error'] == 0:
        try:
            lng = html['detail']['pointx']
            lat = html['detail']['pointy']
        except Exception as e:
            print('未提取到信息', e)
        else:
            return lng,lat
    else:
        # if html:
        #     status = html['status']
        #     msg = html['msg']
        #     return status,msg
        # else:
        return None,None


def main():
    while 1:
        kwd = q.get()
        url = 'https://apis.map.qq.com/jsapi?qt=geoc&addr={0}&key=UGMBZ-CINWR-DDRW5-W52AK-D3ENK-ZEBRC&output=jsonp&pf=jsapi&ref=jsapi&cb=qq.maps._svcb3.geocoder0'.format(kwd)
        try:
            html = get_html(url)
            html = re.sub('qq.map.*?\(|\)','',html)
            html = json.loads(html)
            lng,lat = get_info(html)
            print(kwd,lng,lat)
            if lng:
                f.write("{0}\t{1}\t{2}\t\n".format(kwd,lng, lat))
                f.flush()
            else:
                f_fail.write("{0}\t{1}\t{2}\t\n".format(kwd,lng, lat))
                f_fail.flush()
        finally:
            del kwd
            q.task_done()


if __name__ == "__main__":
    # 结果保存文件
    f = open('address_ok.txt', 'w', encoding='utf-8')
    f_fail = open('address_no.txt', 'w', encoding='utf-8')
    # UA设置
    UA = [{'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'},
          {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
          {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
          {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},
          {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
          {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}
          ]
    # url队列
    q = queue.Queue()
    for kwd in open('kwd.txt', encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)
    # 线程数
    for i in list(range(1)):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
    f_fail.close()
