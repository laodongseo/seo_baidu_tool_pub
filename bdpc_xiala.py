# ‐*‐ coding: utf‐8 ‐*‐
# python3.7版本
import requests
import re
import threading
import queue


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


# 提取下拉词
def get_kwd(html):
    while 1:
        if html:
            try:
                html_new = html.split('[')
                kwd_list = re.findall(r'"q":"(.*?)"}', html_new[1], re.S|re.I)
            except Exception as e:
                print(e)
            else:
                for kwd_xiala in kwd_list:
                    f.write(kwd_xiala+'\n')
        q.task_done()



if __name__ == "__main__":
    # 结果保存文件
    f = open('bdpc_xiala.txt','w',encoding='utf-8')
    # 关键词队列
    q = queue.Queue()
    for kwd in open('kwd.txt',encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)
    # UA设置
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    # 设置线程数
    for i in list(range(1)):
        kwd = q.get()
        url = 'https://www.baidu.com/sugrec?ie=utf-8&prod=pc&wd={}'.format(kwd)
        html = get_html(url)
        t = threading.Thread(target=get_kwd,args=(html,))
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
