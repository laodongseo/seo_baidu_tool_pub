# ‐*‐ coding: utf‐8 ‐*‐
"""
提取的是自然排名url
不含百家号 百度知道 百度贴吧 不含xxx-视频(https://www.baidu.com/sf/vsearch?xxx) 但是含有百科
百家号 百度知道 百度贴吧 类名是c-container  xxx-视频是百度自己的页面
事先准备excel文件，每个sheet存储一类关键词，sheet名字即关键词分类
"""

from openpyxl import load_workbook
import requests
from pyquery import PyQuery as pq
import threading
import queue
import time
import json
import gc


class bdmoMonitor(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    # 读取excel文件 做好关键词分类
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
                 q.put({kwd:sheet_name})
        return q,group_list

    # 初始化结果字典
    @staticmethod
    def result_init(group_list):
        for domain in target_domain:
            result[domain] = {}
            for group in group_list:
                result[domain][group] = 0
        print("初始化结果字典成功")

    # 获取某词serp源码
    def get_html(self,url,retry=2):
        try:
            r = requests.get(url=url,headers=user_agent,timeout=5)
        except Exception as e:
            print('获取源码失败',url,e)
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

    # 提取真实url
    def get_real_urls(self, data_logs=[]):
        real_urls = []
        for data_log in data_logs:
            # json字符串要以双引号表示
            data_log = json.loads(data_log.replace("'", '"'))
            url = data_log['mu']
            real_urls.append(url)
        return real_urls

    # 统计每个域名排名的词数
    def run(self):
        global success_num
        while 1:
            kwd_dict = q.get()
            for kwd,group in kwd_dict.items():
                url = "https://m.baidu.com/s?ie=utf-8&word={0}".format(kwd)
                html = self.get_html(url)
                data_logs = self.get_data_logs(html)
                real_urls = self.get_real_urls(data_logs)
                print(real_urls)
                if real_urls:
                    # 将某词的serp上10条真实url合并为一个字符串
                    domain_str = ''.join(real_urls)
                    try:
                        threadLock.acquire()
                        success_num += 1
                        for domain in target_domain:
                            if domain in domain_str:
                                result[domain][group] += 1
                        print('查询成功{0}个'.format(success_num))
                    except Exception as e:
                        print(e)
                    finally:
                        threadLock.release()
                del kwd
                del group
                gc.collect()
            q.task_done()

    # 保存数据
    @staticmethod
    def save():
        print(result)
        print ('开始save.....')
        with open('bdmo_result.txt','w',encoding="utf-8") as f:
            for domain,data_dict in result.items():
                for key,value in data_dict.items():
                    f.write(date+'\t'+domain+ '\t'+key+'\t'+str(value)+'\n')


if __name__ == "__main__":
    start = time.time()

    # 全局变量 待监控域名列表
    target_domain = ['m.renrenche.com','www.renrenche.com','m.guazi.com','www.guazi.com',
                     'm.che168.com','www.che168.com','m.iautos.cn','so.iautos.cn','www.iautos.cn',
                     'm.hx2car.com','www.hx2car.com','58.com','m.taoche.com','www.taoche.com',
                     'm.51auto.com','www.51auto.com','m.xin.com','www.xin.com']
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; ALP-AL00 Build/HUAWEIALP-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/63.0.3239.83 Mobile Safari/537.36 T7/10.13 baiduboxapp/10.13.0.11 (Baidu; P1 8.1.0)'}
    threadLock = threading.Lock()  # 锁
    result = {}   # 结果保存字典
    success_num = 0  # 查询成功个数
    date = time.strftime("%Y-%m-%d", time.localtime()) # 询日期

    q,group_list = bdmoMonitor.read_excel('kwd.xlsx')
    bdmoMonitor.result_init(group_list)
    all_num = q.qsize()

    # 设置线程数
    for i in list(range(5)):
        t = bdmoMonitor()
        t.setDaemon(True)
        t.start()
    q.join()

    bdmoMonitor.save()
    end = time.time()
    print('\n关键词共{0}个,查询成功{1}个,耗时{2}min'.format(all_num,success_num,(end-start)/60) )
