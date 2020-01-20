# ‐*‐ coding: utf‐8 ‐*‐
"""
采集百度pc首页排名的真实url
准备kwd.txt,一行一个词
线程数自己设,默认2
要加自己账号登陆后的cookie
"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import gc


class BdpcRealUrl(threading.Thread):

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

    # 获取某待查询url的serp源码所有排名url
    def get_encrpt_urls(self,html,url):
        encrypt_url_list = []
        real_urls = []
        doc = pq(html)
        title = doc('title').text()
        if '_百度搜索' in title and 'https://www.baidu.com/s?ie=utf-8' in url:
            div_list = doc('.result').items() # 自然排名
            div_op_list = doc('.result-op').items() # 非自然排名
            for div in div_list:
                rank = div.attr('id')
                if rank:
                    try:
                        a = div('h3 a')
                    except Exception as e:
                        print('未提取自然排名加密链接')
                    else:
                        encrypt_url = a.attr('href')
                        encrypt_url_list.append(encrypt_url)
            for div in div_op_list:
                rank = div.attr('id')
                if rank:
                    link = div.attr('mu') # 真实url,有些op样式没有mu属性
                    if link: 
                        real_urls.append(link)
                    else:
                        encrypt_url = div('article a').attr('href')
                        encrypt_url_list.append(encrypt_url)

        else:
            print('源码异常,可能反爬')
            time.sleep(60)
        return encrypt_url_list,real_urls

    # 解密某条加密url
    def decrypt_url(self,encrypt_url,retry=1):
        real_url = None # 默认None
        try:
            encrypt_url = encrypt_url.replace('http://','https://')
            # print(encrypt_url)
            r = requests.head(encrypt_url,headers=my_header)
        except Exception as e:
            print(encrypt_url,'解密失败',e)
            time.sleep(6)
            if retry > 0:
                self.decrypt_url(encrypt_url,retry-1)
        else:
            real_url = r.headers['Location']
        return real_url

    # 获取结果页真实url
    def get_real_urls(self, encrypt_url_list):
        if encrypt_url_list:
            real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
            return real_url_list
        else:
            return []

    # 线程函数
    def run(self):
        while 1:
            kwd = q.get()
            # url带上tn等参数 否则会被反爬
            url = "https://www.baidu.com/s?ie=utf-8&rsv_bp=1&tn=87048150_dg&wd={0}".format(kwd)
            try:
                html,now_url = self.get_html(url)
                encrypt_url_list,real_urls = self.get_encrpt_urls(html,now_url)
                real_urls_qita = self.get_real_urls(encrypt_url_list)
                real_urls.extend(real_urls_qita)
            except Exception as e:
                print(e)
            else:
                for real_url in real_urls:
                    f.write(real_url + '\n')
                    print(real_url)
                f.flush()
            finally:
                del kwd
                gc.collect()
                q.task_done()
                exit()


if __name__ == "__main__":

    start = time.time()
    my_header = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Cookie':'BIDUPSID=95E739A8EE050812705C1FDE2584A61E; PSTM=1563865961; BAIDUID=95E739A8EE050812705C1FDE2584A61E:SL=0:NR=10:FG=1; BDUSS=NMRzZPVUFqR0JtbzJJc1ZDdkx2MGtiQUpvWVNUSjhnSUFmRFRmTnpDdmpGcXhkRVFBQUFBJCQAAAAAAAAAAAEAAADag5oxzI2IkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOOJhF3jiYRdOU; NOJS=1; BD_UPN=12314353; MSA_WH=414_736; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; H_WISE_SIDS=141144_139203_139419_139403_137831_114177_135846_141000_139148_120169_139864_140833_133995_138878_137979_140173_131247_132552_141261_118880_118865_118839_118832_118793_138165_107317_138883_140260_141367_141410_139046_140202_140592_138585_139174_139624_140114_136196_131861_140591_133847_140792_140065_140545_131423_140823_138663_136537_141103_110085_140325_127969_140622_140595_140864_139802_137252_139408_127417_138312_138425_141193_138944_140685_141190_140596_140964; SE_LAUNCH=5%3A26323611_0%3A26323611; uc_login_unique=6bf49fd83dac5615e84a46c7a074358a; uc_recom_mark=cmVjb21tYXJrXzExMjgyMTQ5; delPer=0; BD_CK_SAM=1; H_PS_PSSID=; sug=0; sugstore=0; ORIGIN=0; bdime=20100; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03295031977; PSINO=3; BDRCVFR[xoix5KwSHTc]=mk3SLVN4HKm; H_PS_645EC=4ab6F6VIt%2BYkr06wgh3RIrIwQ%2Fal4E2RHKvDXYvs9ojMQEhw8q4h1OJUVxdAvNcvWuSdmLAiss89; BDSVRTM=184; COOKIE_SESSION=6_0_4_8_3_15_0_1_3_5_0_2_6777_1579491493_0_0_1579422695_0_1579491512%7C9%23349315_47_1579491172%7C9',
        'Host':'www.baidu.com',
        'Referer':'https://www.hao123.com/?tn=48020221_28_hao_pg',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'same-origin',
        'Sec-Fetch-User':'?1',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
    q = BdpcRealUrl.read_txt('kwd.txt') 
    f = open('bdpc_real_url.txt','w+',encoding='utf-8')
    # 设置线程数
    for i in list(range(1)):
        t = BdpcRealUrl()
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
    end = time.time()
    print('耗时{0}min'.format((end - start) / 60))
