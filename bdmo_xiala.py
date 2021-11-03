# ‐*‐ coding: utf‐8 ‐*‐
"""
百度移动下拉词
目前返回json数据,后期可能会变化
默认线程1
"""
import requests
import threading
import queue
import time
import json
import random
import traceback



def get_cookie():
    seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lis = []
    [lis.append(random.choice(seed)) for _ in seed]
    StringS = ''.join(lis)
    return StringS

# header
def get_header():
    StringS = get_cookie()
    my_header = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding':'deflate',
'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,pt;q=0.5',
'Cache-Control':'no-cache',
'Host':'m.baidu.com',
'Pragma':'no-cache',
'Sec-Fetch-Dest':'document',
'Sec-Fetch-Mode':'navigate',
'Sec-Fetch-Site':'none',
'Sec-Fetch-User':'?1',
'Upgrade-Insecure-Requests':'1',
'User-Agent':random.choice(ua_list).strip(),
'Cookie':f'BIDUPSID=95E739A8EE050812705C1FDE2584A61E; PSTM=1563865961; BDUSS=Dk4ZVBCcWN3aVA1LUF-TlRrYTYxczR1TnFwSWtncVZzdzBUMkRpM2p-QTd2dlZlRVFBQUFBJCQAAAAAAAAAAAEAAADag5oxzI2IkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADsxzl47Mc5ed; BDUSS_BFESS=Dk4ZVBCcWN3aVA1LUF-TlRrYTYxczR1TnFwSWtncVZzdzBUMkRpM2p-QTd2dlZlRVFBQUFBJCQAAAAAAAAAAAEAAADag5oxzI2IkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADsxzl47Mc5ed; BAIDUID={StringS}:SL=0:NR=10:FG=1; __yjs_duid=1_5ae4d8f5d697df213487ed86b671c45d1619745523512; MSA_WH=375_812; COOKIE_SESSION=0_0_0_0_0_w3_2_1_0_0_0_1_13_1623379671%7C1%230_0_0_0_0_0_0_0_1623379671%7C1; FC_MODEL=0.02_3_13_0_8.91_0_1_0_0_0_11.88_0.02_8_17_2_23_0_1623382183_1623379671%7C9%238.91_0.02_0.02_8_2_1623382183_1623379671%7C9%230_vaghghghx_0_3_3_0_249_1623379671; BAIDUID_BFESS=DDEF0EB0EF9FAD4B541EA25191702D42:FG=1; uc_login_unique=519da14a47c0774e41050ecb2530d1e7; uc_recom_mark=cmVjb21tYXJrXzExMjgyMTQ5; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; ab_sr=1.0.1_ZTE1NzJjNjdkYjVhYzBmYmUwZDQ4ZGNkYjZmNjEyMzc1OWY5ZTBjZmEzOTE1NjE0NmMyNDE5MTQxZWU1YjMyYmVlOGRhMjg0N2NiODA0Y2ZjZTk3NWMyMWJlNDc0ZmU5ZTg4Mjg5MTJkNzk0NWUyNzZkNGFlNDE5NmJiOTE0YmYyYWE2NDkyYWU5MzhhNDM3N2ZmOGY3OTYyOGU2NWQwMjJiMzQwYmJlYTM5M2QzMTEyMTM4MjYwNWI1YTVmZjMw; H_WISE_SIDS=110085_114550_127969_175668_176398_177371_178384_178601_179346_179364_179451_179620_180276_181133_181135_181489_181588_181712_181825_182291_182529_183031_183330_183346_183536_183584_183611_183712_183975_184042_184246_184267_184319_184440_184657_184734_184793_184811_184826_184894_185029_185268_185305_185517_185879_185892_185903_186038_186315_186318_186411_186446_186559_186597_186635_186898_187022_187042_187088_187121_187187_187202_187292_187325_187385_187392_187433_187448_187533_187671_187726_187929_187963_188041_188220_188333_188425_188468_8000060_8000117_8000120_8000138_8000149_8000163_8000172_8000177_8000179; rsv_i=2febgwQOusHlfUnYxXctnFALuxzTG60eLZ7X1VyS7pNxz5ruNMwxCPnl755%2BII4GPCXJFcsbsKmv87b5v2ft%2BmrS7Z1E7%2FY; BDSVRBFE=Go; BA_HECTOR=8g2k8485su2h0k2l071gl2skp13; ZFY=IkFKxndW7afw0FeE5e80rTfa:ANDVW2UmXbl0YlNNPbQ:C; BDSVRTM=39; plus_lsv=e9e1d7eaf5c62da9; plus_cv=1::m:7.94e+147; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1632727705; Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1632727705; SE_LAUNCH=5%3A27212128; __bsi=7932260733211936424_00_38_R_R_57_0303_c02f_Y; wise_tj_ub=ci%4077_26_77_26_81_123_37%7Ciq%408_2_7_130%7Ccb%40-1_-1_-1_-1_-1_-1_-1%7Cce%401%7Ctse%401; BDICON=10123156'
    }
    return my_header


# 获取源码
def get_html(url,retry=2):
    my_header = get_header()
    try:
        r = requests.get(url=url,headers=my_header, timeout=5)
    except Exception as e:
        print('获取源码失败', url, e)
        time.sleep(5)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.json()
        return html


def get_kwds(html):
    if html:
        xiala_kwds = []
        dicts = html['g'] if 'g' in html else {}
        for dic in dicts:
            kwd = dic['q']
            xiala_kwds.append(kwd)
        return xiala_kwds


# 结果排序
def sort_dict(dicts_kwd):
    res = sorted(dicts_kwd.items(), key=lambda e:e[1], reverse=True)
    for kwd,count in res:
        f_count.write('{0}\t{1}\n'.format(kwd,count))
        f_count.flush()


def main():
    while 1:
        kwd = q.get()
        url = "https://m.baidu.com/sugrec?pre=1&&ie=utf-8&json=1&prod=wise&wd={0}".format(kwd)
        try:
            html = get_html(url)
            if not html:
                print('error',html)
                q.put(kwd)
                time.sleep(30)
                continue
            xiala_kwds = get_kwds(html)
            if xiala_kwds == None:
                print('parse error',html)
                q.put(kwd)
                time.sleep(10)
                continue
            print(xiala_kwds)
            for kwd in xiala_kwds:
                dicts_kwd[kwd] = dicts_kwd[kwd] + 1 if kwd in dicts_kwd else 1
                threadLock.acquire()
                f.write(kwd + '\n') # 防止多线程写入错乱
                threadLock.release()
            f.flush()
        except Exception as e:
            print('main',e)
            traceback.print_exc(file=open('log_mo_xiala.txt', 'a'))
        finally:
            q.task_done()
            time.sleep(2)



if __name__ == "__main__":
    threadLock = threading.Lock()  # 锁
    ua_list = [line.strip() for line in open('ua_mo.txt','r',encoding='utf-8')]
    dicts_kwd = {}
    # 结果保存文件
    f = open('bdmo_xiala.txt','a+',encoding='utf-8')
    # 结果保存文件-排序
    f_count = open('bdmo_xiala_sort.txt','a+',encoding='utf-8')
    
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
    f.close()
    f_count.close()

