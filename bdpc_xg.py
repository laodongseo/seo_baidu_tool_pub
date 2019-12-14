# ‐*‐ coding: utf‐8 ‐*‐
"""
kwd.txt,一行一个关键词
采集相关搜索词
默认线程2
(cookie用自己登陆账号后的cookie否则很容易被反爬)
"""
import requests
import threading
import queue
from pyquery import PyQuery as pq
import time
import gc


# 获取某词serp源码
def get_html(url, retry=2):
    try:
        r = requests.get(url=url, headers=my_header, timeout=5)
    except Exception as e:
        print('获取源码失败', e)
        time.sleep(6)
        if retry > 0:
            get_html(url, retry - 1)
    else:
        html = r.content.decode('utf-8', errors='ignore')  # 用r.text有时候识别错误
        url = r.url  # 反爬会重定向,取定向后的地址
        return html, url


# 提取相关词
def get_kwds(html,url):
    kwds = []
    doc = pq(str(html))  # 偶尔有问题,强制转str
    title = doc('title').text()
    if '_百度搜索' in title and 'https://www.baidu.com/s?tn=48020221' in url:
        # 异常处理,防止有些词没相关搜索报错
        xg_kwds = doc('#rs table tr th a').items()
        for kwd_xg in xg_kwds:
            kwd_xg = kwd_xg.text()
            kwds.append(kwd_xg)
    else:
        print('源码异常,可能反爬')
    return kwds


# 线程函数
def main():
    while 1:
        kwd = q.get()
        url = 'https://www.baidu.com/s?tn=48020221_28_hao_pg&ie=utf-8&wd={}'.format(kwd)
        try:
            html = get_html(url)
            kwds = get_kwds(html,url)
        except Exception as e:
            print(e)
        else:
            for kwd in kwds:
                f.write(kwd + '\n')
                print(kwd)
            f.flush()
        finally:
            del kwd,url
            gc.collect()
            q.task_done()


if __name__ == "__main__":
    # 结果保存文件
    f = open('bdpc_xg.txt','w',encoding='utf-8')
    # 关键词队列
    q = queue.Queue()
    for kwd in open('kwd.txt',encoding='utf-8'):
        kwd = kwd.strip()
        q.put(kwd)
    # UA设置
    my_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'cookie':'wpr=0;rl__test__cookies=1576231586613; BDICON=10123156; BIDUPSID=95E739A8EE050812705C1FDE2584A61E; PSTM=1563865961; BAIDUID=95E739A8EE050812705C1FDE2584A61E:SL=0:NR=10:FG=1; BDUSS=NMRzZPVUFqR0JtbzJJc1ZDdkx2MGtiQUpvWVNUSjhnSUFmRFRmTnpDdmpGcXhkRVFBQUFBJCQAAAAAAAAAAAEAAADag5oxzI2IkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOOJhF3jiYRdOU; MSA_PBT=146; plus_lsv=f197ee21ffd230fd; plus_cv=1::m:49a3f4a6; MSA_ZOOM=1000; MSA_WH=394_670; lsv=searchboxcss_591d86b-globalBcss_565c244-wwwBcss_777000e-globalT_androidcss_e2c894e-wwwT_androidcss_90adf93; ysm=10313|10313; delPer=0; BDRCVFR[xoix5KwSHTc]=9xWipS8B-FspA7EnHc1QhPEUf; ___rl__test__cookies=1576220661807; SE_LAUNCH=5%3A26270344_0%3A26270344; BDICON=10123156; BDPASSGATE=IlPT2AEptyoA_yiU4V_43kIN8enzTri4H4PISkpT36ePdCyWmhHWBAREUjD6YnSgBC3gzDDPdstPoifKXlVXa_EqnBsZolpMany5xNSCgsTtPsx17QovIab2KUE2sA8PbRhL-3MJJ3NUMWosyBDxhAY1fe768Qx5huvRrzHgmMjsAkeR3oj6r7aTY767O-0APNuc-R0QbSh-OkOWVOGxRILYhFchOJ1L70aOatY6C3D5q6oY0RuiZMExGI8mFppi_x3nBQOLkKaoEV55qysc; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; FEED_SIDS=345657_1213_18; rsv_i=c8e0s9Kbgfe3IYpd4YQd9DWYvBco3sBW3mXRj6IEo6%2FgSyu%2Frc00sEfOpcIfTeIYx8TsGI5lR4gwD25GaSdnvPjVCMWNixE; BAIDULOC=11562630.22873027_149874.6866054242_16432_20001_1576231577543; wise_tj_ub=ci%40-1_-1_-1_-1_-1_-1_-1%7Ciq%408_1_7_275%7Ccb%40-1_-1_-1_-1_-1_-1_-1%7Cce%401%7Ctse%401; H_WISE_SIDS=136722_139419_139405_137831_114177_139251_120169_138490_133995_138878_137979_137690_131247_132552_137750_136680_118880_118865_118839_118832_118793_138165_107313_138882_136431_138845_138691_136863_138147_138114_139174_136195_131861_137105_139274_139400_133847_138476_137734_138343_137467_138564_138648_131423_138663_136537_138178_110085_137441_127969_138302_137252_139507_139408_127417_138312_137187_136635_138425_138562_138943_135718_139221_138239; BDSVRTM=55; BDORZ=SFH; COOKIE_SESSION=10914_1_1_8_1_t1_32_5_5_1_0_5_42_1576231572%7C9%230_0_0_0_0_0_0_0_1576144558%7C1; FC_MODEL=0_1_17_0_0_0_1_0_0_0_0_0_5_32_1_18_0_0_1576231572663%7C9%2310.3_-1_-1_5_1_1576231567476_1576220658164%7C9; ASUV=1.2.114; __bsi=8269619105128910962_00_24_N_R_1_0303_c02f_Y; BDSVRBFE=Go; OUTFOX_SEARCH_USER_ID_NCOO=78699081.532675; wise_tj_ub=ci%40-1_-1_-1_-1_-1_-1_-1%7Ciq%40-1_-1_-1_-1%7Ccb%4056_10_56_10_82_350_73%7Cce%40-1%7Ctse%401'
        }
    # 设置线程数
    for i in list(range(2)):
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()
    q.join()
    f.flush()
    f.close()
