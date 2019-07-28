# ‐*‐ coding: utf‐8 ‐*‐
"""
一个关键词serp上同一个域名出现N个url排名 计算1次
查询前五页的数量,前五页有排名的全部记录,无排名的不记录
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


class bdpcCover(threading.Thread):

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
                for page in page_dict.keys():
                    if page == '':
                        url = "https://m.baidu.com/s?ie=utf-8&word={0}".format(kwd)
                    else:
                        url = "https://m.baidu.com/s?ie=utf-8&word={0}&pn={1}".format(kwd,page)
                    html = self.get_html(url)
                    data_logs = self.get_data_logs(html)
                    real_url_list = self.get_real_urls(data_logs)
                    domain_str = self.get_domains(real_url_list)
                    if domain_str and domain in domain_str:
                        page = '首页' if page == '' else page_dict[page]
                        f.write('{0}\t{1}\t{2}\n'.format(kwd,page,group))
                        break
                    if page == 40 and domain not in domain_str:
                        f.write('{0}\t{1}\t{2}\n'.format(kwd,'五页后',group))
                f.flush()
                threadLock.acquire()
                success_num += 1
                threadLock.release()
                print(success_num)
            except Exception as e:
                print(e)
            finally:
                del kwd
                del group
                q.task_done()


if __name__ == "__main__":
    start = time.time() 
    local_time = time.localtime()
    today = time.strftime('%Y/%m/%d',local_time)
    domain = '5i5j.com'
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Mobile Safari/537.36'}
    threadLock = threading.Lock()  # 锁
    success_num = 0  # 查询成功个数
    page_list = ['首页','二页','三页','四页','五页','五页后']  #查询页码 全局变量
    q,group_list = bdpcCover.read_excel('kwd_core.xlsx')  #关键词队列及属性
    result = bdpcCover.result_init(group_list)  #结果字典
    all_num = q.qsize() # 总词数
    page_dict = {'':'首页',10:'二页',20:'三页',30:'四页',40:'五页'}  #页码页数关系
    f = open('bdmo1_page5_info.txt','w',encoding="utf-8")
    # 设置线程数
    for i in list(range(5)):
        t = bdpcCover()
        t.setDaemon(True)
        t.start()
    q.join()
    f.close()

    # 读取文件 计算首页到五页每页的词数
    for line in open('bdmo1_page5_info.txt','r',encoding='utf-8'):
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
    with open('bdmo1_page5.txt', 'w', encoding="utf-8") as f:
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
    wb.save('bdmo1_page5.xlsx')
    end = time.time()
    print('\n关键词共{0}个,查询成功{1}个,耗时{2}min'.format(all_num, success_num, (end - start) / 60))
