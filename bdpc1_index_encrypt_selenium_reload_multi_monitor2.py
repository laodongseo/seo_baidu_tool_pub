# ‐*‐ coding: utf‐8 ‐*‐
"""
执行脚本,由reload_control_pc.py控制执行
必须单线程,1是因为百度反爬,2是写入文件未加锁可能错乱
selenium驱动浏览器的方式 默认为无头模式,
selenium操作浏览器浏览器会崩溃,reload_control_pc.py负责每30分钟杀死并重启一次本脚本
功能:
   1)指定几个域名,分关键词种类监控首页词数
   2)抓取serp所有url,提取域名并统计各域名首页覆盖率
   3)通过tpl属性记录serp排名url的特征
   4)支持顶级域名或者其他域名
提示:
  1)含自然排名和百度开放平台的排名
  2)百度开放平台的样式mu属性值为排名url,mu不存在提取article里的url
  3)2020xiaoqu_kwd_city_new.xlsx:sheet名为关键词种类,sheet第一列放关键词
结果:
    bdpc1_index_encrypt_all.txt:serp所有加密url(含一些真实url)及样式特征
    bdpc1_script_ids.txt 当前抓取脚本产生的谷歌浏览器及webdriver进程id
"""

from pyquery import PyQuery as pq
import threading
import queue
import time
from urllib.parse import urlparse
from openpyxl import load_workbook
from openpyxl import Workbook
import time
import gc
import random
import urllib3
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import random
import traceback
import tld
import psutil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 获取selenium启动的浏览器pid(含浏览器子进程)
def get_webdriver_chrome_ids(driver):
    all_ids = []
    main_id = driver.service.process.pid
    all_ids.append(main_id)
    p = psutil.Process(main_id)
    child_ids = p.children(recursive=True)
    for id_obj in child_ids:
        all_ids.append(id_obj.pid)
    return all_ids


# 根据pid杀死进程
def kill_process(p_ids):
    try:
        for p_id in p_ids:
            os.system(f'taskkill  /f /pid {p_id}')
    except Exception as e:
        pass
    time.sleep(1)


# 根据进程名获取pid,传参chromedriver
def get_pid_from_name(name):
    chromedriver_pids = []
    pids = psutil.process_iter()
    for pid in pids:
        if(pid.name() == name):
            chromedriver_pids.append(pid.pid)
    return chromedriver_pids



def get_driver(chrome_path,chromedriver_path,ua):
    ua = ua
    option = Options()
    option.binary_location = chrome_path
    # option.add_argument('disable-infobars')
    option.add_argument("user-agent=" + ua)
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--disable-gpu")
    option.add_argument("--disable-features=NetworkService")
    # option.add_argument("--window-size=1920x1080")
    option.add_argument("--disable-features=VizDisplayCompositor")
    option.add_argument('headless')
    option.add_argument('log-level=3') #屏蔽日志
    option.add_argument('--ignore-certificate-errors-spki-list') #屏蔽ssl error
    option.add_argument('-ignore -ssl-errors') #屏蔽ssl error
    option.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    option.add_experimental_option('useAutomationExtension', False)
    No_Image_loading = {"profile.managed_default_content_settings.images": 2}
    option.add_experimental_option("prefs", No_Image_loading)
    # 屏蔽webdriver特征
    option.add_argument("--disable-blink-features")
    option.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=option,executable_path=chromedriver_path )
    # 屏蔽true特征
  #   driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  #       "source": """
  #   Object.defineProperty(navigator, 'webdriver', {
  #     get: () => undefined
  #   })
  # """
  #   })
    return driver


# 只解密加密url用
def get_header():
    my_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': random.choice(list_cookies),
        'Host': 'www.baidu.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': random.choice(list_ua),
        }
    return my_header


class bdpcIndexMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    @staticmethod
    def read_excel(filepath):
        q = queue.Queue()
        group_list = []
        kwd_dict = {}
        wb_kwd = load_workbook(filepath)
        for sheet_obj in wb_kwd:
            sheet_name = sheet_obj.title
            group_list.append(sheet_name)
            kwd_dict[sheet_name] = []
            col_a = sheet_obj['A']
            for cell in col_a:
                kwd = (cell.value)
                # 加个判断吧
                if kwd:
                    q.put([sheet_name, kwd])
        return q, group_list

    # 初始化结果字典
    @staticmethod
    def result_init(group_list):
        result = {}
        for domain in domains:
            result[domain] = {}
            for group in group_list:
                result[domain][group] = {'首页': 0, '总词数': 0}
        print("结果字典init...")
        return result


    # 获取源码,异常由run函数try捕获
    def get_html(self,kwd):
        global driver
        html = now_url = ''
        driver.get('https://www.baidu.com/')
        # exit()
        input = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "kw"))
        )
        input_click_js = 'document.getElementById("kw").click()'
        driver.execute_script(input_click_js)  # 点击输入框

        input_js = 'document.getElementById("kw").value="{0}"'.format(kwd)
        driver.execute_script(input_js)  # 输入搜索词

        baidu = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "su"))
        )
        click_js = 'document.getElementById("su").click()'
        driver.execute_script(click_js)  # 点击搜索

        # 等待首页元素加载完毕
        # 此处异常由run函数的try捕获
        bottom = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "help"))
        )
        # 页面下拉
        js_xiala = 'window.scrollBy(0,{0} * {1})'.format('document.body.scrollHeight', random.random() / 5)
        driver.execute_script(js_xiala)
        html = driver.page_source
        now_url = driver.current_url
        return html,now_url

    # 获取某词serp源码所有url
    def get_encrpt_urls(self, html, url):
        encrypt_url_list = []
        real_urls = []
        doc = pq(html)
        title = doc('title').text()
        if '_百度搜索' in title and 'https://www.baidu.com/' in url:
            div_list = doc('#content_left .result').items()  # 自然排名
            div_op_list = doc('#content_left .result-op').items()  # 非自然排名
            for div in div_list:
                rank = div.attr('id') if div.attr('id') else 'id_xxx'
                tpl = div.attr('tpl') if div.attr('tpl') else 'tpl_xxx'
                if rank:
                    try:
                        a = div('h3 a')
                    except Exception as e:
                        print('未提取自然排名加密链接')
                    else:
                        encrypt_url = a.attr('href')
                        encrypt_url_list.append((encrypt_url, rank, tpl))
            for div in div_op_list:
                rank_op = div.attr('id') if div.attr('id') else 'id_xxx'
                tpl = div.attr('tpl') if div.attr('tpl') else 'tpl_xxx'
                if rank_op:
                    link = div.attr('mu')  # 真实url,有些op样式没有mu属性
                    # print(link,rank_op)
                    if link:
                        real_urls.append((link, rank_op, tpl))
                    else:
                        encrypt_url = div('article a').attr('href')
                        encrypt_url_list.append((encrypt_url, rank_op, tpl))

        else:
            print('源码异常,可能反爬', title)
            time.sleep(60)

        return encrypt_url_list, real_urls


    # 线程函数
    def run(self):
        global driver,webdriver_chrome_ids
        while 1:
            group_kwd = q.get()
            group, kwd = group_kwd
            print(group,kwd)
            try:
                html,now_url = self.get_html(kwd)
                encrypt_url_list_rank, real_urls_rank = self.get_encrpt_urls(html, now_url)
            except Exception as e:
                traceback.print_exc(file=open(f'{today}_serp_log.txt', 'a'))
                print(e, '杀死残留进程,重启selenium')
                q.put(group_kwd)
                driver.quit()
                kill_process(webdriver_chrome_ids)
            else:
                for my_serp_url, my_order, tpl in encrypt_url_list_rank:
                    f_all.write('{0}\t{1}\t{2}\t{3}\t{4}\t加密\n'.format(kwd, str(my_serp_url), my_order, tpl, group))
                for my_real_url, my_order, tpl in real_urls_rank:
                    f_all.write('{0}\t{1}\t{2}\t{3}\t{4}\t非加密\n'.format(kwd, str(my_real_url), my_order, tpl, group))
                f_all.flush()
            finally:
                del group_kwd, kwd, group
                gc.collect()
                q.task_done()
                time.sleep(2)


if __name__ == "__main__":
    start = time.time()
    local_time = time.localtime()
    # today = time.strftime('%Y%m%d', local_time)
    today = '20210419'
    f_all = open(f'{today}bdpc1_index_encrypt_all.txt', 'a+', encoding="utf-8") # 结果文件

    list_ua = [i.strip() for i in open('headers.txt', 'r', encoding='utf-8')]
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
    chromedriver_path = 'D:/install/pyhon36/chromedriver.exe'
    ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
    driver = get_driver(chrome_path,chromedriver_path,ua)
    webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
    print(f'chrome的pid及子进程:{webdriver_chrome_ids}')
    with open('bdpc1_script_ids.txt','w',encoding='utf-8') as f_pid:
        f_pid.write('\n'.join([str(id) for id in webdriver_chrome_ids]))

    domains = ['5i5j.com', 'lianjia.com', 'anjuke.com', 'fang.com','ke.com']  # 目标域名
    q, group_list = bdpcIndexMonitor.read_excel('2021xiaoqu_kwd_city.xlsx')  # 关键词队列及分类
    result = bdpcIndexMonitor.result_init(group_list)  # 结果字典
    # print(result)
    all_num = q.qsize()  # 总词数
    # 设置线程数
    for i in list(range(1)):
        t = bdpcIndexMonitor()
        t.setDaemon(True)
        t.start()
    q.join()
    f_all.close()
    print('done')
