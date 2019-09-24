# ‐*‐ coding: utf‐8 ‐*‐
"""
bdmo1_page5_info.txt记录每个kwd在第几页有排名
bdmo1_page5_rankurl.txt记录每个kwd前五页排名的url，当前页面出现多个就记录多个
生成的excel和txt是首页 前二/三/四/五/五页后的数量
bdmo1_page5_info.txt的行数就是真正查询成功的词数

"""
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
from urllib.parse import urlparse
from openpyxl import load_workbook
from openpyxl import Workbook
import json
import time
import gc
import zlib



class bdmoCoverPage5(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    @staticmethod
    def read_excel(filepath):
        q = queue.Queue()
        group_list = []
        wb_kwd = load_workbook(filepath)
        for sheet_obj in wb_kwd:
            sheet_name = sheet_obj.title
            group_list.append(sheet_name)
            col_a = sheet_obj['A']
            for cell in col_a:
                kwd = (cell.value)
                # 加个判断,防止一些不可见字符
                if kwd:
                    q.put([kwd,sheet_name])
        return q, group_list

    # 初始化结果字典
    @staticmethod
    def result_init(group_list):
        result = {}
        for group in group_list:
            result[group] = {}
        for group in group_list:
            for page in page_list:
                result[group][page] = 0
        print("结果字典init...")
        return result

    # 获取某词serp源码
    def get_html(self,url,retry=2):
        try:
            r = requests.get(url=url,headers=user_agent,timeout=5)
        except Exception as e:
            print('获取源码失败',e)
            time.sleep(1)
            if retry > 0:
                self.get_html(url,retry-1)
        else:
            html = r.text
            return html

    # 获取某词的serp源码上包含排名url的div块
    def get_data_logs(self, html):
        data_logs = []
        if html and '百度' in html:
            doc = pq(html)
            try:
                div_list = doc('.c-result').items()
            except Exception as e:
                print('提取div块失败', e)
            else:
                for div in div_list:
                    data_log = div.attr('data-log')
                    data_logs.append(data_log) if data_log is not None else data_logs
        else:
            print('结果页源码有问题,可能被反爬')
        return data_logs

    # 提取排名的真实url
    def get_real_urls(self, data_logs=[]):
        real_urls = []
        for data_log in data_logs:
            # json字符串要以双引号表示
            data_log = json.loads(data_log.replace("'", '"'))
            url = data_log['mu']
            real_urls.append(url)
        return real_urls

    # 提取某条url域名部分
    def get_domain(self,real_url):

        # 通过mu提取url有些非自然排名url是空
        try:
           res = urlparse(real_url)  # real_url为空不会报错
        except Exception as e:
           print (e,real_url)
           domain = "xxx"
        else:
           domain = res.netloc
        return domain

    # 获取某词serp源码首页排名真实url的域名部分
    def get_domains(self,real_urls):
            domain_list = [self.get_domain(real_url) for real_url in real_urls]
            domain_set = set(domain_list)
            domain_set = domain_set.remove(None) if None in domain_set else domain_set
            domain_str = ','.join(domain_set)
            # 搜一个词 同一个域名多个url出现排名 只计算一次
            return domain_str

    # 线程函数
    def run(self):
        global success_num
        while 1:
            kwd_group = q.get()
            kwd,group = kwd_group
            try:
                # 循环1-5页数依次查询
                for page in page_dict.keys():
                    if page == '':
                        url = "https://m.baidu.com/s?ie=utf-8&word={0}".format(kwd)
                    else:
                        url = "https://m.baidu.com/s?ie=utf-8&word={0}&pn={1}".format(kwd,page) # 根据page构造2到5页url
                    html = self.get_html(url)
                    data_logs = self.get_data_logs(html)
                    real_url_list = self.get_real_urls(data_logs)
                    # 将10条排名url合并成字符串domain_str
                    domain_str = self.get_domains(real_url_list)
                    # 直接判断目标站是否在domain_str内
                    if domain_str and domain in domain_str:
                        page = '首页' if page == '' else page_dict[page]
                        # 将关键词 排名页数 关键词属性写入文件 
                        f.write('{0}\t{1}\t{2}\n'.format(kwd,page,group))

                        # 详细记录10条排名url中有几条是目标站点的链接
                        for real_url in real_url_list:
                            if domain in real_url:
                                f_url.write('{0}\t{1}\t{2}\t{3}\n'.format(kwd,page,group,real_url))

                        # 避免每个词都把前五页查询一遍，一旦找到排名本次循环结束
                        break
                    if page == 40 and domain not in domain_str:
                        f.write('{0}\t{1}\t{2}\n'.format(kwd,'五页后',group))
                f.flush()
                f_url.flush()
                threadLock.acquire()
                success_num += 1
                threadLock.release()
                print(success_num)
            except Exception as e:
                print(e)
            finally:
                del kwd
                del group
                gc.collect()
                q.task_done()


if __name__ == "__main__":
    start = time.time() 
    local_time = time.localtime()
    today = time.strftime('%Y%m%d',local_time)
    domain = '5i5j.com'
    user_agent = {
        'User-Agent':'Mozilla/5.0 (Linux; Android 8.1.0; ALP-AL00 Build/HUAWEIALP-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.11 (Baidu; P1 8.1.0)',
        'Referer': 'https://m.baidu.com/',
        'Cookie':'wpr=6; ___rl__test__cookies=1567566913148; BIDUPSID=95E739A8EE050812705C1FDE2584A61E; PSTM=1563865961; BAIDUID=95E739A8EE050812705C1FDE2584A61E:SL=0:NR=10:FG=1; BDUSS=FsYjdHZC05cmxocWFKR1U3a2ZZdTRqYlRSdHYzNTJzaVJtUFpLck4zT0xnRjlkSVFBQUFBJCQAAAAAAAAAAAEAAADag5oxzI2IkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIvzN12L8zddNE; MSA_PBT=146; plus_lsv=3244eb2ce4167e29; plus_cv=1::m:49a3f4a6; usr_his=e34a; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; SE_LAUNCH=5%3A26126113_0%3A26126113; BDICON=10123156; BDPASSGATE=IlPT2AEptyoA_yiU4V_43kIN8enzTri4H4PISkpT36ePdCyWmhHWBAREUjD6YnSgBC3gzDDPdstPoifKXlVXa_EqnBsZolpMany5xNSCgsTtPsx17QovIab2KUE2sA8PbRhL-3MJJ3NUMWosyBDxhAY1fe768Qx5huvRrzHgmMjsAkeR3oj6r7aTY767O-0APNuc-R0QbSh-OkOWVOGxRILYhFchOJ1L70aOatY6C3D5q6oY0RuiZMExGI8mFppi_x3nBQOLkKaoEV55qysc; delPer=0; ysm=10309; lsv=globalTjs_3aec804-searchboxless_366db37-sugcss_465b32a-wwwBcss_f90e83d-framejs_63d8bca-atomentryjs_0b0c978-searchboxjs_ede4863-esl_and_confjs_f9f1566-wwwTcss_9c5a46e-globalBjs_54486bd-sugjs_4826844-wwwjs_ab662ab; MSA_WH=346_299; MSA_ZOOM=1000; COOKIE_SESSION=179063_0_0_4_1_w6_1_4_2_0_0_2_28_1567566894%7C4%230_0_0_0_0_0_0_0_1567386507%7C1; OUTFOX_SEARCH_USER_ID_NCOO=1669951631.280445; FC_MODEL=-1_1_2_0_8.27_3_1_19.15_3_0_15.44_-1_5_1_1_16_0_1567566913295_1567566894080%7C5%238.27_-1_-1_5_1_1567566913295_1567566894080%7C5; PSINO=7; H_PS_PSSID=; BDRCVFR[buve_JmS-26]=9xWipS8B-FspA7EnHc1QhPEUf; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03175834511; uc_login_unique=fafa25412d8732231a77c76d0f04485e; uc_recom_mark=cmVjb21tYXJrXzExMjgyMTQ5; H_WISE_SIDS=127760_135173_134862_114177_120169_133971_132909_131246_122155_130762_132378_131517_118880_118865_118839_118832_118793_107313_132781_133352_132553_129651_132250_131861_134855_128968_135307_133838_133847_132552_135873_134256_129646_131423_135552_135592_110085_134154_127969_128918_131951_135672_135459_127417_135044_135041_135836_132467_135504_134724_135718; rsv_i=8306IP87UaKGrZa008N2QWuoffdEg77S53FjuGVZHMxXh%2Be4jiDluDFCzf4FlSh4ZM%2FZBcd0RH5V%2FevD590xYefpAH1tPmc; FEED_SIDS=345657_0904_12; BDSVRTM=374; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1567387069,1567387568,1567566843,1567571951; Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1567571951; ___rl__test__cookies=1567571953947; BDSVRBFE=Go; wise_tj_ub=ci%40137_32_-1_-1_-1_-1_-1%7Ciq%4024_1_23_308%7Ccb%40-1_-1_-1_-1_-1_-1_-1%7Cce%401%7Ctse%401; __bsi=9711260377085762445_00_19_R_R_7_0303_c02f_Y'}
    threadLock = threading.Lock()  # 锁
    success_num = 0  # 查询成功个数
    page_list = ['首页','二页','三页','四页','五页','五页后']  #查询页码 全局变量
    q,group_list = bdmoCoverPage5.read_excel('./kwd_core_city.xlsx')  #关键词队列及属性
    result = bdmoCoverPage5.result_init(group_list)  #结果字典
    all_num = q.qsize() # 总词数
    page_dict = {'':'首页',10:'二页',20:'三页',30:'四页',40:'五页'}  #页码页数关系
    f = open('{0}bdmo1_page5_info.txt'.format(today),'w',encoding="utf-8")
    f_url = open('{0}bdmo1_page5_rankurl.txt'.format(today),'w',encoding="utf-8")
    # 设置线程数
    for i in list(range(4)):
        t = bdmoCoverPage5()
        t.setDaemon(True)
        t.start()
    q.join()
    f.close()
    f_url.close()

    # 读取文件 计算首页到五页每页的词数
    for line in open('{0}bdmo1_page5_info.txt'.format(today),'r',encoding='utf-8'):
        line = line.strip().split('\t')
        page = line[1]
        group = line[2]
        result[group][page] += 1

    # 计算首页、前二页、前三页、前四页、前五页词数
    for group,page_num in result.items():
        for page,num in page_num.items():
            if page in ['五页后']:
                result[group]['五页后'] = num
        for page,num in page_num.items():
            if page in ['首页','二页','三页','四页']:
                result[group]['五页'] += num
        for page, num in page_num.items():
            if page in ['首页','二页','三页']:
                result[group]['四页'] += num
        for page, num in page_num.items():
            if page in ['首页','二页',]:
                result[group]['三页'] += num
        for page, num in page_num.items():
            if page in ['首页',]:
                result[group]['二页'] += num

    # 写入txt文件
    with open('{0}bdmo1_page5.txt'.format(today), 'w', encoding="utf-8") as f:
        for group,data_dict in result.items():
            for page,value in data_dict.items():
                f.write(group + '\t' + page + '\t' + str(value) + '\n')

    #写入excel文件
    wb = Workbook()
    # 创建sheet
    for group in group_list:
        sheet_num = 0
        wb.create_sheet(u'{0}'.format(group),index=sheet_num)
        sheet_num += 1
    # 写内容
    page_list.insert(0,'日期')
    for group,data_dict in result.items():
            # 写第一行日期+首页到五页后
            wb[group].append(page_list)
            row_value = [today]
            for page,value in data_dict.items():
                row_value.append(value)
            # 写第二行日期+值
            wb[u'{0}'.format(group)].append(row_value)
            # 干掉日期单元格的数据
            wb[u'{0}'.format(group)].cell(row=1,column=1,value="")
    wb.save('{0}bdmo1_page5.xlsx'.format(today))
    end = time.time()
    print('\n关键词共{0}个,查询任务{1}个,耗时{2}min'.format(all_num, success_num, (end - start) / 60))
