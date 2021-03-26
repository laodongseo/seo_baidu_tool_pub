# ‐*‐ coding: utf‐8 ‐*‐
"""
设为单线程,1是因为百度反爬,连续解密url会被禁止,2是没加锁多线程写入可能错乱
selenium驱动浏览器的方式 默认为无头模式,
长期操作浏览器浏览器会崩溃,为了解决该问题代码检测抛出异常就重启(验证码页面也会抛出异常重启)
因为存在崩溃,所以翻页判断不能用死循环(翻页成功恰好崩溃就会陷入死循环),也得用元素等待
重启前杀死webdriver启动的谷歌进程及webdriver本身

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
    bdmo1_page5_info.txt:前五页各监控站点词的排名及url,如有2个url排名,只取第一个就结束
    bdmo1_page5_all.txt:前五页serp所有url及样式特征,依此统计各域名首页覆盖率-单写脚本统计
"""

from pyquery import PyQuery as pq
import threading
import queue
import time
import json
from urllib.parse import urlparse
from openpyxl import load_workbook
from openpyxl import Workbook
import time
import gc
import random
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import traceback
import tld
import psutil



# 获取selenium启动的浏览器pid
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
    time.sleep(2)


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
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--disable-gpu")
    option.add_argument("--disable-features=NetworkService")
    # option.add_argument("--window-size=1920x1080")
    option.add_argument("--disable-features=VizDisplayCompositor")
    # option.add_argument('headless')
    option.add_argument('log-level=3') #屏蔽日志
    option.add_argument('--ignore-certificate-errors-spki-list') #屏蔽ssl error
    option.add_argument('--ignore-certificate-errors')
    option.add_argument('-ignore -ssl-errors') #屏蔽ssl error
    option.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    option.add_experimental_option('useAutomationExtension', False)
    No_Image_loading = {"profile.managed_default_content_settings.images": 1}
    option.add_experimental_option("prefs", No_Image_loading)
    resolution = {"deviceMetrics": { "width": 375, "height": 667, "pixelRatio": 1 }}
    option.add_experimental_option("mobileEmulation", resolution)
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


class bdmoIndexMonitor(threading.Thread):
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
    def get_html(self,kwd,user_agent):
        global driver
        html = now_url = ''
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent":user_agent}})
        driver.get('https://m.baidu.com/')
        input = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "index-kw"))
        )

        input_click_js = 'document.getElementById("index-kw").click()'
        driver.execute_script(input_click_js) # 点击输入框

        input_js = 'document.getElementById("index-kw").value="{0}"'.format(kwd)
        driver.execute_script(input_js) # 输入搜索词            
        baidu = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "index-bn"))
        )
        click_js = 'document.getElementById("index-bn").click()'
        driver.execute_script(click_js) # 点击搜索
        # 页面下拉
        driver.execute_script(js_xiala)
        # 等待首页搜索后的底部元素加载,验证码页面无此元素
        # 此处异常由run函数的try捕获
        bottom = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "page-copyright")),message='error_bottom')
        html = driver.page_source
        now_url = driver.current_url
        return html,now_url


    # 获取某词的serp源码上包含排名url的div块
    def get_divs(self, html ,url):
        div_list = []
        doc = pq(html)
        title = doc('title').text()
        if '- 百度' in title and 'https://m.baidu.com/s' in url:
            try:
                div_list = doc('.c-result').items()
            except Exception as e:
                print('提取div块失败', e)
            else:
                pass
        else:
            print('源码异常---------------------',title)
            time.sleep(120)
        return div_list

    # 提取serp源码当前页排名的真实url
    def get_real_urls(self, div_list,page_text):
        real_urls_rank = []
        if div_list:
            for div in div_list:
                try:
                    data_log = div.attr('data-log')
                    data_log = json.loads(data_log.replace("'", '"')) # json字符串双引号
                    srcid = data_log['ensrcid'] if 'ensrcid' in data_log  else 'ensrcid' # 样式特征
                    rank_url = data_log['mu']  if 'mu' in data_log else None # mu可能为空或者不存在
                    rank = data_log['order']
                except Exception as e:
                    print('提取rank_url error',e)
                else:
                    if rank_url:
                        real_urls_rank.append((rank_url,rank,srcid,page_text))
                    # 如果mu为空或者不存在
                    else:
                        # 提取资讯聚合,图片聚合
                        article = div('.c-result-content article')
                        link = article.attr('rl-link-href')
                        # 提取热议聚合
                        if not link:
                            a = div('.c-result-content article header a')
                            data_log_ugc = a.attr('data-log')
                            data_log_ugc = json.loads(data_log_ugc.replace("'", '"')) if data_log_ugc else '' # json字符串双引号
                            if data_log_ugc:
                                link = data_log_ugc['mu']  if 'mu' in data_log_ugc else None # mu可能为空或者不存在
                                link = 'https://m.baidu.com{0}'.format(link) if link != None else None
                                # 提取问答聚合
                                if not link:
                                    link = a.attr('href')
                                # 一般为卡片样式,链接太多,不提取了
                                if not link:
                                    pass
                        real_urls_rank.append((link,rank,srcid,page_text))
        return real_urls_rank


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

    # 获取某词serp源码排名所有域名-暂时无用
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


    # 获取某词所有翻页顶级域名及页码和域名排名对应关系
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


    # 线程函数
    def run(self):
        global driver,webdriver_chrome_ids
        while 1:
            group_kwd = q.get()
            group, kwd = group_kwd
            print(group,kwd)
            html = ''
            real_urls_rank_all = [] # 存储前五页url
            # 外层加异常,五页都成功后再写入
            try:
                for page_num,page_text in page_dict.items():
                    user_agent = random.choice(user_agents)
                    if page_num == 1: 
                        # get_html已检测首页是否加载完
                        html,now_url = self.get_html(kwd,user_agent)
                    else:
                        doc = pq(str(html))
                        # page_num=2代表首页处理完,第2轮循环,翻页要点首页下的翻页
                        if page_num == 2:
                            text_bottom_page1 = doc('#page-controller div.new-pagenav a.new-nextpage-only')
                            if not text_bottom_page1:
                                break
                            driver.execute_script(next_page_click_js)
                        else:
                            # 2页及以后的翻页元素和首页的不同
                            text_bottom_other = doc('#page-controller div.new-pagenav div.new-pagenav-right a.new-nextpage')
                            if not text_bottom_other:
                                break
                            else:
                                driver.execute_script(next_page2_click_js)
                        # 等待-检测当前源码是否为翻页源码
                        fanye_obj = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, 'new-nowpage')))
                        if str(page_num) in fanye_obj.text:
                            driver.execute_script(js_xiala)
                    # 解析首页或翻页源码
                    html, now_url = driver.page_source, driver.current_url
                    divs_res = self.get_divs(html,now_url)
                    real_urls_rank = self.get_real_urls(divs_res,page_text)
                    real_urls_rank_all.extend(real_urls_rank)
            except Exception as e:
                traceback.print_exc(file=open(f'{today}mo_log.txt', 'w'))
                print(e, '杀死残留进程,重启selenium')
                q.put(group_kwd)
                driver.quit()
                kill_process(webdriver_chrome_ids)
                # gc.collect()
                driver = get_driver(chrome_path,chromedriver_path,ua)
                chromedriver_pids = get_pid_from_name("chromedriver.exe")
                webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
                print(f'chrome的pid:{webdriver_chrome_ids},\nchromedriver的pid:{chromedriver_pids}')
                webdriver_chrome_ids.extend(chromedriver_pids)
            else:
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
                time.sleep(2.2)


if __name__ == "__main__":
    start = time.time()
    local_time = time.localtime()
    today = time.strftime('%Y%m%d', local_time)
    page_dict = {1: '首页', 2: '二页', 3: '三页', 4: '四页', 5: '五页'}
    # 首页点击下一页
    next_page_click_js = """document.querySelector("#page-controller > div > a").click()"""
    # 第2页到其它页点击下一页
    next_page2_click_js = """document.querySelector("#page-controller > div > div.new-pagenav-right > a").click()"""
    # 获取当前页码
    now_page_js = """var now_page = document.querySelector("#page-controller > div > div.new-pagenav-center > span").innerText
;return now_page"""
    # 页面下拉
    js_xiala = 'window.scrollBy(0,{0} * {1})'.format('document.body.scrollHeight', random.random() / 5)

    user_agents = [i.strip() for i in open('ua_mo.txt', 'r', encoding='utf-8')]
    # list_cookies = [i.strip() for i in open('cookies.txt', 'r', encoding='utf-8')]
    target_domains = ['5i5j.com', 'lianjia.com', 'anjuke.com', 'fang.com','ke.com']  # 目标域名
    my_domain = '5i5j.com'
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
    chromedriver_path = 'D:/install/pyhon36/chromedriver.exe'
    ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'

    driver = get_driver(chrome_path,chromedriver_path,ua)
    chromedriver_pids = get_pid_from_name("chromedriver.exe")
    webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
    webdriver_chrome_ids.extend(chromedriver_pids)
    print(f'chrome的pid:{webdriver_chrome_ids},\nchromedriver的pid:{chromedriver_pids}')

    q, group_list = bdmoIndexMonitor.read_excel('2020kwd_url_core_city_unique1.xlsx')  # 关键词队列及分类
    result = bdmoIndexMonitor.result_init(group_list)  # 结果字典
    # print(result)
    all_num = q.qsize()  # 总词数
    f = open(f'{today}bdmo1_page5_info.txt', 'w+', encoding="utf-8")
    f_all = open(f'{today}bdmo1_page5_all.txt', 'w+', encoding="utf-8")
    file_path = f.name
    # 设置线程数
    for i in list(range(1)):
        t = bdmoIndexMonitor()
        t.setDaemon(True)
        t.start()
    q.join()
    f.close()
    f_all.close()
    end = time.time()
    print('关键词任务共{0}个,耗时{2}min'.format(all_num,(end - start) / 60))
