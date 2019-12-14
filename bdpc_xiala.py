# ‐*‐ coding: utf‐8 ‐*‐
"""
提取百度pc下拉词
准备kwd.txt,一行一个
下拉接口抓包获取
默认线程数2,请求头的cookie用你自己登陆账号后的cookie
"""
import requests
import threading
import queue
import gc


# 获取某词下拉地址源码
def get_html(url,retry=2):
    try:
        r = requests.get(url=url,headers=my_header, timeout=5)
    except Exception as e:
        print('获取源码失败', url, e)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.json()
        return html


# 提取下拉词
def get_kwds(html):
    kwds = []
    if html:
        try:
            kwd_list = html['g']
        except Exception as e:
            pass
        else:
            for data_dict in kwd_list:
                kwd = data_dict['q']
                kwds.append(kwd)
    return kwds


# 线程函数
def main():
    while 1:
        kwd = q.get()
        url = 'https://www.baidu.com/sugrec?ie=utf-8&prod=pc&wd={}'.format(kwd)
        try:
            html = get_html(url)
            kwds = get_kwds(html)
        except Exception as e:
            print(e)
        else:
            for wd in kwds:
                f.write(wd + '\n')
                print(wd)
            f.flush()
        finally:
            del kwd,url
            gc.collect()
            q.task_done()


if __name__ == "__main__":
    # 结果保存文件
    f = open('bdpc_xiala.txt','w',encoding='utf-8')
    # 关键词队列
    q = queue.Queue()
    for kwd in open('kwd.txt',encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)
    # 请求头设置
    my_header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Cookie':'BIDUPSID=EB1F44AB7896D7EFA4F0FD243C29FF17; PSTM=1567562976; BAIDUID=EB1F44AB7896D7EFA4F0FD243C29FF17:SL=0:NR=10:FG=1; BDUSS=BZWlZuSXpNWmNjM3BTSktnM2xhbGhIdUlqeW1ITEdvclpzSHpIS3p2WUMwc2hkRVFBQUFBJCQAAAAAAAAAAAEAAAAGtiZkNzcyNDgzMjAwZG9uZwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJFoV0CRaFdeF; plus_cv=1::m:49a3f4a6; MSA_WH=400_655; lsv=globalTjs_3a11c3d-globalT_androidcss_4630b37-wwwT_androidcss_c5f9a54-searchboxcss_591d86b-globalBcss_aad48cc-wwwBcss_777000e-framejs_c9ac861-atomentryjs_5cd4b30-globalBjs_99ad350-wwwjs_b674808; BD_UPN=19314353; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BDICON=10294984.98; delPer=0; BD_CK_SAM=1; rsv_i=c2b6G%2F3avQC%2FfgLjK6Tg5dByzXJGjTHszykjx0XgYlZZgizi3%2F9wOVrzCucTWKLxPYYUs%2BqPpygizpeQMUWhVScLKRxzaaw; FEED_SIDS=732051_1030_14; plus_lsv=f197ee21ffd230fd; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1572225355,1572415847,1572418912; Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1572418912; BAIDULOC=12966109.384666294_4841881.341700486_100_131_1572418911981; SE_LAUNCH=5%3A26206981_0%3A26206981; BDPASSGATE=IlPT2AEptyoA_yiU4VKH3kIN8efjWvW4AfvESkplQFStfCaWmhH3BrUzWz0HSieXBDP6wZTXdMsDxXTqXlVXa_EqnBsZolpOaSaXzKGoucHtVM69-t5yILXoHUE2sA8PbRhL-3MEF2ZELlQvcgjchQZrchW8z3JTpxz1z5Xocc0T1UKR2VLJxJyTS7xvRHvcPNuz94rXnEpKKSmBUADHRVjYcSQyWXkD5NOtjsAm1Q0WrkoXGurSRvAa1G8vJpFeXAio1fWU60ul269v5HViViwh9UOI7u46MnJZ; H_WISE_SIDS=137151_137734_137755_136649_137663_137071_128070_134982_136665_120196_136768_137002_137788_136366_132909_136456_137690_135847_131246_137746_132378_136681_118893_118876_118846_118827_118802_132782_136800_136431_136093_133352_136862_137089_129652_136194_124637_137105_137572_133847_132551_137468_134046_129646_131423_137212_137466_136034_110085_127969_137613_131951_136611_137252_128196_137696_136636_137767_137207_134347_134231_137618_137449; kleck=638cabc3ad33a7a082343c4553a47c42; BDRCVFR[x4e6higC8W6]=mk3SLVN4HKm; PSINO=7; H_PS_PSSID=1440_21084_20697_29567_29220; sug=3; sugstore=0; ORIGIN=0; bdime=0; H_PS_645EC=db34IWhem1lYO7OwXVBPbsx2yQuIu3jmqGT9FUp09TItjsTj8omDTLnov6%2BIZQe6dqc',
        }
    # 设置线程数
    for i in list(range(1)):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
