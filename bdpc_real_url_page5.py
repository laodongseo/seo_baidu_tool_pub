# ‐*‐ coding: utf‐8 ‐*‐
# python3.6版本
import requests
import threading
import queue
from pyquery import PyQuery as pq
import time

# 获取某词serp源码
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


# 获取某词serp源码上自然排名的所有url
def get_encrpt_urls(html):
    encrypt_url_list = []
    if html and '_百度搜索' in html:
        doc = pq(html)
        try:
            a_list = doc('.t a').items()
        except Exception as e:
            print('未提取到serp上的解密url', e)
        else:
            for a in a_list:
                encrypt_url = a.attr('href')
                if encrypt_url.find('http://www.baidu.com/link?url=') == 0:
                    encrypt_url_list.append(encrypt_url)
    return encrypt_url_list


# 解密某条加密url
def decrypt_url(encrypt_url, retry=1):
    try:
        encrypt_url = encrypt_url.replace('http://', 'https://')
        r = requests.head(encrypt_url, headers=user_agent)
    except Exception as e:
        print(encrypt_url, '解密失败', e)
        if retry > 0:
            decrypt_url(encrypt_url, retry - 1)
    else:
        return r.headers['Location']


# 获取某词serp源码前5页排名真实url
def get_real_urls():
    while 1:
        kwd = q.get()
        try:
            for page_num in page_dict.keys():
                if page_num == '':
                    url = "https://www.baidu.com/s?ie=utf-8&wd={0}".format(kwd)
                else:
                    url = "https://www.baidu.com/s?ie=utf-8&wd={0}&pn={1}".format(kwd,page_num)
                html = get_html(url)
                encrypt_url_list = get_encrpt_urls(html)
                if encrypt_url_list:
                    real_url_list = [decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
                    for url in real_url_list:
                        print(url)
                        f.write(str(url)+'\t'+page_dict[page_num]+'\n')
                else:
                    print('第{0}页未提取到serp上的加密url'.format(page_num))
        except Exception as e:
            print(e)
        finally:
            f.flush()
            q.task_done()

if __name__ == "__main__":
    page_dict = {'':'首页',10:'二页',20:'三页',30:'四页',40:'五页'} #查询页数
    local_time = time.localtime()
    today = time.strftime('%Y%m%d',local_time)
    # 结果保存文件
    f = open('bdpc_real_page5_url{0}.txt'.format(today),'w',encoding='utf-8')
    # UA设置
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    # 关键词队列
    q = queue.Queue()
    for kwd in open('kwd.txt',encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)
    # 线程数
    for i in list(range(1)):
        t = threading.Thread(target=get_real_urls)
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
