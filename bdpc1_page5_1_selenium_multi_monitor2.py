# ‐*‐ coding: utf‐8 ‐*‐
"""
设为单线程,1是因为百度反爬,2是没加锁多线程写入可能错乱
selenium驱动浏览器的方式 默认为无头模式,
长期操作浏览器浏览器会崩溃,为了解决该问题代码检测抛出异常就重启(验证码页面也会抛出异常重启)
功能:
   1)指定几个域名,分关键词种类监控首页词数
   2)抓取serp所有url,提取域名并统计各域名首页覆盖率
   3)通过tpl属性记录serp排名url的特征
   4)支持顶级域名或者其他域名
提示:
  1)含自然排名和百度开放平台的排名
  2)百度开放平台的样式mu属性值为排名url,mu不存在提取article里的url
  3)kwd.xlsx:sheet名为关键词种类,sheet第一列放关键词
结果:
    bdpc1_page5_info.txt:各监控站点词的排名及url,如有2个url排名,只取第一个
    bdpc1_page5_all.txt:serp所有url及样式特征,依此统计各域名首页覆盖率-单写脚本统计
    bdpc1_page5.xlsx:自己站每类词首页词数
    bdpc1_page5_domains.xlsx:各监控站点每类词的首页词数
    bdpc1_page5_domains.txt:各监控站点每类词的首页词数
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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 杀死进程
def kill_process(*p_names):
    try:
        for p_name in p_names:
            os.system('taskkill /im {0} /F'.format(p_name))
    except Exception as e:
        pass
    time.sleep(2)


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
    # option.add_argument('headless')
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
        'User-Agent': random.choice(list_headers),
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
        for domain in target_domains:
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
    def get_encrpt_urls(self, html, url,page_now):
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
                        encrypt_url_list.append((encrypt_url, rank, tpl, page_now))
            for div in div_op_list:
                rank_op = div.attr('id') if div.attr('id') else 'id_xxx'
                tpl = div.attr('tpl') if div.attr('tpl') else 'tpl_xxx'
                if rank_op:
                    link = div.attr('mu')  # 真实url,有些op样式没有mu属性
                    # print(link,rank_op)
                    if link:
                        real_urls.append((link, rank_op, tpl, page_now))
                    else:
                        encrypt_url = div('article a').attr('href')
                        encrypt_url_list.append((encrypt_url, rank_op, tpl, page_now))

        else:
            print('源码异常,可能反爬', title)
            time.sleep(60)

        return encrypt_url_list, real_urls

    # 解密某条加密url
    def decrypt_url(self, encrypt_url, my_header, retry=1):
        real_url = None  # 默认None
        if encrypt_url:
            try:
                encrypt_url = encrypt_url.replace('http://', 'https://') if 'https://' not in encrypt_url else encrypt_url
                r = requests.head(encrypt_url, headers=my_header,timeout=20)
            except Exception as e:
                print(encrypt_url, '解密失败', e)
                time.sleep(200)
                if retry > 0:
                    my_header = get_header()
                    self.decrypt_url(encrypt_url, my_header, retry - 1)
                else:
                    real_url = encrypt_url
            else:
                real_url = r.headers['Location'] if 'Location' in r.headers else None
        return real_url


    # 获取某词serp源码排名真实url
    def get_real_urls(self, encrypt_url_list):
        real_url_list = [self.decrypt_url(encrypt_url) for encrypt_url in encrypt_url_list]
        real_url_set = set(real_url_list)
        real_url_set.remove(None) if None in real_url_set else real_url_set
        real_url_list = list(real_url_set)
        return real_url_list

    # 提取某url的域名部分
    def get_domain(self, real_url):
        domain = ''
        if real_url:
            try:
                res = urlparse(real_url)
            except Exception as e:
                print(e, 'real_url解析异常', real_url)
            else:
                domain = res.netloc # real_url为None返回字节数据
        return domain

    # 获取某词serp源码排名所有域名
    def get_domains(self, real_url_list):
        domain_url_dicts = {}
        for real_url, my_order, tpl in real_urls_rank:
            if real_url:
                domain = self.get_domain(real_url)
                # 一个词某域名多个url有排名,算一次
                domain_url_dicts[domain] = (real_url,my_order,tpl) if domain not in domain_url_dicts else domain_url_dicts[domain]
        return domain_url_dicts


    # 提取某url的顶级域名
    def get_top_domain(self,real_url):
        top_domain = ''
        if real_url:
            try:
                obj = tld.get_tld(real_url,as_object=True)
                top_domain = obj.fld
            except Exception as e:
                print(e,'top domain:error')
        return top_domain

    # 获取某词所有翻页顶级域名
    def get_top_domains_all_page(self,real_urls_rank):
        domain_url_dict_all = {}
        all_page_domains = set()
        for real_url, my_order, tpl,page_text in real_urls_rank:
            domain_url_dict_all[page_text] = {}

        for real_url, my_order, tpl,page_text in real_urls_rank:
            if real_url:
                top_domain = self.get_top_domain(real_url)
                all_page_domains.add(top_domain)
                serp_element = real_url,my_order,tpl
                # 一个词某域名多个url有排名,算一次
                domain_url_dict_all[page_text][top_domain] = (real_url,my_order,tpl) if top_domain not in domain_url_dict_all[page_text] else domain_url_dict_all[page_text][top_domain]

        return domain_url_dict_all,all_page_domains


    # 获取某词serp源码顶级域名
    def extract_top_domains(self,serp_elements):
        top_domains = []
        for real_url, my_order, tpl in serp_elements:
            if real_url:
                top_domain = self.get_top_domain(real_url)
                top_domains.append(top_domain)
        return top_domains


    # 线程函数
    def run(self):
        global driver
        while 1:
            group_kwd = q.get()
            group, kwd = group_kwd
            print(group,kwd)
            html = ''
            encrypt_url_list_rank_all = [] # 存储前五页url
            real_urls_rank_all = [] # 存储前五页url
            # 外层加异常,五页都成功后再写入
            try:
                for page_num,page_text in page_dict.items():
                    if page_num == 1: 
                        html,now_url = self.get_html(kwd)
                    else:
                        doc = pq(str(html))
                        text_bottom = doc('.page-inner').text()
                        if '下一页' in str(text_bottom):
                            # 点击下一页
                            driver.execute_script(next_page_click_js)
                            # 检测当前url是否为翻页url
                            while True:
                                now_url = driver.current_url
                                if 'pn={0}0'.format(page_num - 1) in driver.current_url:
                                    break
                            # 检测当前源码是否为翻页源码
                            while True:
                                now_page = driver.execute_script(now_page_js)
                                if int(now_page) == page_num:
                                    break
                            # 翻页执行成功后获取源码
                            html, now_url = driver.page_source, driver.current_url
                    encrypt_url_list_rank, real_urls_rank = self.get_encrpt_urls(html, now_url,page_text)
                    encrypt_url_list_rank_all.extend(encrypt_url_list_rank)
                    real_urls_rank_all.extend(real_urls_rank)
            except Exception as e:
                traceback.print_exc(file=open('log.txt', 'a'))
                print(e, '重启selenium')
                q.put(group_kwd)
                driver.quit()
                # kill_process('chromedriver.exe','chrome.exe')
                gc.collect()
                driver = get_driver(chrome_path,chromedriver_path,ua)
            else:
                for my_serp_url, my_order, tpl, page_text in encrypt_url_list_rank_all:
                    my_header = get_header()
                    my_real_url = self.decrypt_url(my_serp_url, my_header)
                    time.sleep(0.25) # 连续解密太快易被反爬
                    real_urls_rank_all.append((my_real_url, my_order, tpl, page_text))
                for my_real_url, my_order, tpl, page_text in real_urls_rank_all:
                    f_all.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(kwd, str(my_real_url), my_order, tpl, page_text,group))

                domain_url_dict_all_page,all_page_domains = self.get_top_domains_all_page(real_urls_rank_all)

                for domain in target_domains:
                    if domain not in all_page_domains:
                        f.write(f'{kwd}\t无\t无\t{group}\t{domain}\t无\t无\n')
                    else:
                        for page_text,domain_url_dicts in domain_url_dict_all_page.items():
                            # print(domain_url_dicts)
                            domains_now_page = domain_url_dicts.keys()
                            if domain in domains_now_page:
                                # my_url可能为None
                                my_url,my_order,tpl = domain_url_dicts[domain]
                                f.write(f'{kwd}\t{str(my_url)}\t{my_order}\t{group}\t{domain}\t{tpl}\t{page_text}\n')
                                break

                f.flush()
                f_all.flush()
            finally:
                del group_kwd, kwd, group
                gc.collect()
                q.task_done()


if __name__ == "__main__":
    start = time.time()
    local_time = time.localtime()
    today = time.strftime('%Y%m%d', local_time)
    page_dict = {1: '首页', 2: '二页', 3: '三页', 4: '四页', 5: '五页'}
    # 点击下一页js
    next_page_click_js = """var pages =document.querySelectorAll('.n');var next_page = pages[pages.length-1];next_page.click()"""
    # 获取当前页码
    now_page_js = """var now_page = document.querySelector("#page > div > strong").innerText;return now_page"""

    list_headers = [i.strip() for i in open('headers.txt', 'r', encoding='utf-8')]
    # list_cookies = [i.strip() for i in open('cookies.txt', 'r', encoding='utf-8')]
    target_domains = ['5i5j.com', 'lianjia.com', 'anjuke.com', 'fang.com','ke.com']  # 目标域名
    my_domain = '5i5j.com'
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
    chromedriver_path = 'D:/install/pyhon36/chromedriver.exe'
    ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
    driver = get_driver(chrome_path,chromedriver_path,ua)
    q, group_list = bdpcIndexMonitor.read_excel('2021xiaoqu_kwd_city_bj.xlsx')  # 关键词队列及分类
    result = bdpcIndexMonitor.result_init(group_list)  # 结果字典
    # print(result)
    all_num = q.qsize()  # 总词数
    f = open('{0}bdpc1_page5_info.txt'.format(today), 'w+', encoding="utf-8")
    f_all = open('{0}bdpc1_page5_all.txt'.format(today), 'w+', encoding="utf-8")
    file_path = f.name
    # 设置线程数
    for i in list(range(1)):
        t = bdpcIndexMonitor()
        t.setDaemon(True)
        t.start()
    q.join()
    f.close()
    f_all.close()
    end = time.time()
    print('关键词任务共{0}个,耗时{2}min'.format(all_num,(end - start) / 60))
