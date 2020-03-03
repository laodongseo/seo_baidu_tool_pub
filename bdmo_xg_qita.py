# ‐*‐ coding: utf‐8 ‐*‐
"""
百度移动端相关词和其他人还在搜采集
将结果去重并统计重复次数排序
bdmo_xgqita.txt为采集到的词
bdmo_xgqita_sort.txt为排序后的词
"""
# python3.6版本
import requests
import threading
import queue
from pyquery import PyQuery as pq
import time

# 获取某词serp源码
def get_html(url,my_header,retry=1):
    try:
        r = requests.get(url=url,headers=my_header,timeout=5)
    except Exception as e:
        print('获取源码失败',e)
        time.sleep(6)
        if retry > 0:
            get_html(url,my_header,retry-1)
    else:
        html = r.content.decode('utf-8',errors='ignore')  # 用r.text有时候识别错误
        url = r.url  # 反爬会重定向,取定向后的地址
        return html,url



# 提取相关词+其他人还在搜
def get_kwds(html,url):
    xg_kwds = []
    qita_kwds = []
    doc = pq(html)
    title = doc('title').text()
    if '- 百度' in title and 'https://m.baidu.com/s?ie=utf-8' in url:
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
                break # 找到目标div后就停止
    else:
        print('源码error',url)
        time.sleep(100)
    xg_kwds.extend(qita_kwds)
    return xg_kwds

# 结果排序
def sort_dict(dicts_kwd):
    res = sorted(dicts_kwd.items(), key=lambda e:e[1], reverse=True)
    for kwd,count in res:
        f_count.write('{0}\t{1}\n'.format(kwd,count))
        f_count.flush()



def main():
    while 1:
        kwd = q.get()
        url = "https://m.baidu.com/s?ie=utf-8&word={0}".format(kwd)
        try:
            print(url)
            html,now_url = get_html(url,my_header)
            kwds = get_kwds(html,now_url)
            print(kwd,len(kwds))
            for kwd in kwds:
                dicts_kwd[kwd] = dicts_kwd[kwd] + 1 if kwd in dicts_kwd else 1
                f.write(kwd + '\n')
            f.flush()
        except Exception as e:
            print(e)
        finally:
            q.task_done()



if __name__ == "__main__":
    dicts_kwd = {}
    # 结果保存文件
    f = open('bdmo_xgqita.txt','w',encoding='utf-8')
    # 结果保存文件-排序
    f_count = open('bdmo_xgqita_sort.txt','w',encoding='utf-8')
    # head设置
    my_header = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding':'deflate',
'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Cookie':'cuid=9D9A0DBD27C85A299930263FF6BE52CB;BAIDU_WISE_UID=wpass_1557773074883_645;HISTORY=7538961407b87ee55f98de183cdc4bf7e4a758d55c6bb28493;BAIDUID=AC1D01EB26A43281B80C01932C3B1B04:FG=1;STOKEN=18f5c4868f05de8b634e97c53240b53075a1259fd6c10d0ed69fdeb1898385e8;SAVEUSERID=81db925c8ee9433ed26e5949342dda8b732ee6b86d;PTOKEN=a706047f3786779f85f752cc0b76b51b;BDUSS=29GYXlkb2tORTd3MkJCVG02ejlUUHJPMVRnSGZ6ekN6VVF-UjcyZVFZQXpTQUZkSVFBQUFBJCQAAAAAAAAAAAEAAAADZvwsv76w~NfT1tfDtMHLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADO72Vwzu9lcd;PASSID=FuYK;UBI=fi_PncwhpxZ%7ETaJc0sNwb%7ENx8KDCUsDofWK6%7Ezu9rupW0C6n2vvtflUqpArFgdr87G2TYzPXaQXGWs2WXC2',
'Host':'m.baidu.com',
'Pragma':'no-cache',
'Referer':'https://m.baidu.com/',
'Sec-Fetch-Mode':'navigate',
'Sec-Fetch-Site':'same-origin',
'Sec-Fetch-User':'?1',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36',}
    # 关键词队列
    q = queue.Queue()
    for kwd in open('kwd.txt','r',encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)
    # 设置线程数
    for i in list(range(1)):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
    q.join()
    sort_dict(dicts_kwd)
    f.flush()
    f.close()
    f_count.close()
