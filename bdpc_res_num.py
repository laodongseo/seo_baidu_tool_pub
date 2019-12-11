# -*- coding: utf-8 -*-
"""
记录百度pc搜索词搜索结果数及首页展示的结果数
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import gc,csv,re,random

# 不要在网上复制粘贴ua,用自己浏览器的,有些低版本的ua百度返回非正常页面
ua_pc_list = [
'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
]


# 获取serp源码
def get_html(url, retry=2):
    user_agent = random.choice(ua_pc_list)
    my_header = {
        'cookie': 'BDUSS=RQSWpXeEd5a1lDLXF6OExrVmdzeW9WUnFqRWtTNGRpWEctOU1RSmw0bHB5WU5aSVFBQUFBJCQAAAAAAAAAAAEAAADlnXKtt7CwybK-vbYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGk8XFlpPFxZeG',
        'User-Agent': user_agent}
    try:
        r = requests.get(url=url, headers=my_header, timeout=5)
    except Exception as e:
        print('获取源码失败', url, e)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.content.decode('utf-8',errors='ignore')
        return html


# 分析源码获取结果
def get_res_num(html,url):
    encrypt_url_list = []
    all_num = '---'
    doc = pq(html)
    title = doc('title').text()
    if '_百度搜索' in title and 'https://www.baidu.com/s?tn=48020221' in url:
        try:
            all_num_text = doc('.nums_text').text()
            a_list = doc('.t a').items()
        except Exception as e:
            print('未提取到serp上的解密url', e)
        else:
            all_num = re.search('.*约(.*?)个',all_num_text).group(1)
            for a in a_list:
                encrypt_url = a.attr('href')
                if encrypt_url.find('http://www.baidu.com/link?url=') == 0:
                    encrypt_url_list.append(encrypt_url)
    else:
        print(title,'源码异常,可能反爬')
        time.sleep(6)
    return all_num,len(encrypt_url_list)


# 线程函数
def run():
    while 1:
        kwd = q.get()
        url = "https://www.baidu.com/s?tn=48020221_28_hao_pg&ie=utf-8&wd={0}".format(kwd)
        try:
            html = get_html(url)
            all_num,page1_num = get_res_num(html,url)
            print(kwd,all_num,page1_num)
            f_csv.writerow([kwd,str(all_num),str(page1_num)])
        except Exception as e:
            print(e)
        finally:
            q.task_done()
            csvFile.flush()
            gc.collect()


if __name__ == "__main__":
    print('beginning...')
    q = queue.Queue()  # 关键词队列
    for kwd in open('kwd.txt','r',encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)

    csvFile = open('dai_res_num.csv','w',newline='')  # 结果保存文件
    f_csv = csv.writer(csvFile)
    f_csv.writerow(['关键词','总个数','首页个数'])

    # 线程数
    for i in range(2):
        t = threading.Thread(target=run)
        t.setDaemon(True)
        t.start()
    q.join()
    csvFile.close()
    print('ending...')
