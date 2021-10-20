#‐*‐coding:utf‐8‐*‐
"""
某个地址获取经纬度信息
"""
import requests
import threading
import queue
import random
import time


# 获取某词serp源码
def get_html(url,retry=2):
    # time.sleep(random.random())
    try:
        time.sleep(0.5)
        user_agent = random.choice(UA)
        r = requests.get(url=url,headers=user_agent, timeout=5)
    except Exception as e:
        print('获取源码失败', url, e)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.json()
        # print(html)
        return html


def get_info(html):
    if html and html['status'] == 0:
        try:
            lng = html['result']['location']['lng']
            lat = html['result']['location']['lat']
        except Exception as e:
            print('未提取到信息', e)
        else:
            return lng,lat
    else:
        if html:
            status = html['status']
            msg = html['msg']
            return status,msg
        else:
            return 'None','None'


def main():
    while 1:
        kwd,city = q.get()
        print(kwd,city)
        # url = 'http://api.map.baidu.com/geocoder?output=json&key=f247cdb592eb43ebac6ccd27f796e2d2&address={0}'.format(kwd) #以前的版本
        # url = 'http://api.map.baidu.com/geocoding/v3/?output=json&ak=F4ayMlhooBg2sLkh7d2NK0jARxqqjIaf&address={0}&city={1}'.format(kwd,city)
        # url = 'http://api.map.baidu.com/geocoding/v3/?output=json&ak=0Mqs9FVP06oA3hIjQGstgOCinOWXG1Ph&address={0}&city={1}'.format(kwd,city)
        url = 'http://api.map.baidu.com/geocoding/v3/?output=json&ak=qGLwUHqoqWCGsl5MARI3x7Uh5xknxhuP&address={0}&city={1}'.format(kwd,city)
        try:
            html = get_html(url)
            lng,lat = get_info(html)
            print(kwd,lng,lat,city)
            if lng:
                f.write("{0}\t{1}\t{2}\t{3}\n".format(kwd,lng, lat,city))
                f.flush()
            else:
                f_fail.write("{0}\t{1}\t{2}\t{3}\n".format(kwd,lng, lat,city))
                f_fail.flush()
        finally:
            del kwd
            q.task_done()


if __name__ == "__main__":
    # 结果保存文件
    f = open('address_.txt', 'a+', encoding='utf-8')
    f_fail = open('address_no.txt', 'a+', encoding='utf-8')
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
    for line in open('kwd.txt', encoding='utf-8'):
        line = line.strip()
        kwd_city = line.split('\t')
        q.put(kwd_city)
    # 线程数
    for i in list(range(2)):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
    f_fail.close()
