# ‐*‐ coding: utf‐8 ‐*‐
"""
获取快照地址
查询一个url，直接取的搜索结果第1位排名的快照，所以可能有误差
"""

import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import gc


class BdpcKuaiZhao(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取txt文件 获取待查询url
    @staticmethod
    def read_txt(filepath):
        q = queue.Queue()
        for url in open(filepath, encoding='utf-8'):
            url = url.strip()
            q.put(url)
        return q

    # 获取某待查询url的serp源码
    def get_html(self,url,retry=2):
        try:
            r = requests.get(url=url,headers=my_header,timeout=5)
        except Exception as e:
            print('获取源码失败',e)
            time.sleep(6)
            if retry > 0:
                self.get_html(url,retry-1)
        else:
            html = r.content.decode('utf-8',errors='ignore')  # 用r.text有时候识别错误
            url = r.url  # 反爬会重定向,取定向后的地址
            return html,url


    # 获取某待查询url的serp源码上自然排名的所有url
    def get_encrpt_urls(self,html,url):
        encrypt_url = ''
        doc = pq(html)
        title = doc('title').text()
        if '_百度搜索' in title and 'https://www.baidu.com/s?ie=utf-8' in url:
            div_list = doc('.result').items() # 自然排名
            for div in div_list:
                try:
                    a = div('.f13 .m ')
                except Exception as e:
                    print('未提取自然排名加密链接')
                else:
                    kuaizhao_url = a.attr('href')
                    encrypt_url = kuaizhao_url
                    break

        else:
            print('源码异常,可能反爬')
            print(title)
            time.sleep(60)
                    
        return encrypt_url



    # 线程函数
    def run(self):
        global shoulu_num
        while 1:
            target_url = q.get()
            # url带上tn等参数 否则更易被反爬
            url = "https://www.baidu.com/s?ie=utf-8&rsv_bp=1&tn=87048150_dg&wd={0}".format(target_url)
            try:
                html,now_url = self.get_html(url)
                encrypt_url = self.get_encrpt_urls(html,now_url)
            except Exception as e:
                print(e)
            else:
                if encrypt_url:
                    print(encrypt_url)
                    f.write('{0}\t{1}\n'.format(target_url,encrypt_url))
            finally:
                f.flush()
                del target_url
                gc.collect()
                q.task_done()


if __name__ == "__main__":

    start = time.time()
    shoulu_num = 0
    lock = threading.Lock() #创建锁
    my_header = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding':'deflate',
'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'BIDUPSID=9456F2638642EC81ACD54009E96C4D2F; PSTM=1595843656; BAIDUID=9456F2638642EC81CCFDBD5A55221FC6:FG=1; BD_HOME=1; BD_UPN=12314353; delPer=0; BD_CK_SAM=1; PSINO=7; H_PS_PSSID=32294_1439_31669_32355_31660_32046_31321_32299_26350_22157; H_PS_645EC=a5daRiayjQw4sxjCEX%2Fen4mS19TWlN35bUDurNkiGkDmM26iyOHaPmHEfSY; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSVRTM=303; COOKIE_SESSION=0_0_1_0_0_2_0_0_0_1_2_0_0_0_0_0_0_0_1595843672%7C1%230_0_1595843672%7C1',
'Host':'www.baidu.com',
'Sec-Fetch-Dest':'document',
'Sec-Fetch-Mode':'navigate',
'Sec-Fetch-Site':'same-origin',
'Sec-Fetch-User':'?1',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',}
    q = BdpcKuaiZhao.read_txt('pc_url.txt') # url队列
    f = open('bdpc_kuaizhao.txt','w+',encoding='utf-8')
    # 设置线程数
    for i in list(range(1)):
        t = BdpcKuaiZhao()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
    end = time.time()
    print('耗时{0}min,收录{1}个'.format((end - start) / 60,shoulu_num))
