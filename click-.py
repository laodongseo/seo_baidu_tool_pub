# ‐*‐ coding: utf‐8 ‐*‐
"""
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
from selenium.webdriver.common.action_chains import ActionChains
import random
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    No_Image_loading = {"profile.managed_default_content_settings.images": 1}
    option.add_experimental_option("prefs", No_Image_loading)
    driver = webdriver.Chrome(options=option, chrome_options=option,executable_path=chromedriver_path )
    # 屏蔽特征
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
    })
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
        # 'User-Agent': random.choice(list_headers),
        }
    return my_header


# 获取源码,异常由run函数try捕获
def get_html(kwd):
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
    bottom = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "help"))
    )
    driver.execute_script(js_xiala)
    html = driver.page_source
    now_url = driver.current_url
    return html,now_url


# 获取某词serp源码自然排名的url
def get_encrpt_urls(html, url):
    encrypt_url_list = []
    doc = pq(html)
    title = doc('title').text()
    if '_百度搜索' in title and 'https://www.baidu.com/' in url:
        div_list = doc('.result').items()  # 自然排名
        # div_op_list = doc('.result-op').items()  # 非自然排名
        for div in div_list:
            rank = div.attr('id')
            if rank:
                try:
                    a = div('h3 a')
                except Exception as e:
                    print('未提取自然排名加密链接')
                else:
                    encrypt_url = a.attr('href')
                    encrypt_url_list.append((encrypt_url, rank))
    else:
        print('源码异常,可能反爬', title)
        time.sleep(60)
    return encrypt_url_list


# 解密某条加密url
def decrypt_url(encrypt_url, my_header, retry=1):
    real_url = None  # 默认None
    if encrypt_url:
        try:
            encrypt_url = encrypt_url.replace('http://', 'https://')
            r = requests.head(encrypt_url, headers=my_header)
        except Exception as e:
            print(encrypt_url, '解密失败', e)
            time.sleep(60)
            if retry > 0:
                decrypt_url(encrypt_url, my_header, retry - 1)
        else:
            real_url = r.headers['Location'] if 'Location' in r.headers else None
    return real_url

# 提取某url的域名部分
def get_domain(real_url):
    domain = ''
    if real_url:
        try:
            res = urlparse(real_url)
        except Exception as e:
            print(e, 'real_url解析异常', real_url)
        else:
            domain = res.netloc # real_url为None返回字节数据
    return domain

# 获取某词serp源码首页排名所有域名
def get_domains(real_url_list):
    domain_str = ''
    domain_list = [get_domain(real_url) for real_url in real_url_list]
    domain_str = ','.join(domain_list)
    return domain_str


# 根据id来定位元素点击
def click_ele(id):
    global driver
    rank_domain = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='{0}']/h3/a".format(id)))
    )
    webdriver.ActionChains(driver).move_to_element(rank_domain).click(rank_domain).perform()

def close_handle():
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    # 检测完全关闭
    while 1:
        if len(driver.window_handles) == 1:
            break

# 主函数
def run():
    global driver
    my_header = get_header()
    while 1:
        # kwd,click_domain = q.get()
        kwd,click_domain = '租房','juntuan.org'
        is_click = 0 # 标记是否点击
        # 一个词前五页循环外侧加异常
        try:
            html = ''
            for page_num in list(page_dict.keys()):
                if is_click == 1:
                    break
                if page_num==1:
                    html,now_url = get_html(kwd)
                else:
                    if '下一页' in html:
                        # 点击下一页
                        driver.execute_script(next_page_click_js)
                        # 检测当前url是否为翻页url
                        while True:
                            now_url = driver.current_url
                            if 'pn={0}0'.format(page_num-1) in driver.current_url:
                                break
                        # 检测当前源码是否为翻页源码
                        now_page_js = """var now_page = document.querySelector("#page > div > strong").innerText;return now_page"""
                        while True:
                            now_page = driver.execute_script(now_page_js)
                            if int(now_page) == page_num:
                                break
                        # 翻页执行成功后获取源码
                        html,now_url = driver.page_source,driver.current_url
                encrypt_url_list_rank = get_encrpt_urls(html, now_url)
                real_urls_rank = []
                real_urls = []
                # 源码ok再往下判断
                if encrypt_url_list_rank:
                    for my_serp_url, my_order in encrypt_url_list_rank:
                        my_real_url = decrypt_url(my_serp_url, my_header)
                        time.sleep(0.2)
                        real_urls_rank.append((my_real_url, my_order))

                    for my_real_url, my_order in real_urls_rank:
                        real_urls.append(my_real_url)
                    domain_str = get_domains(real_urls)

                    if domain_str:
                        # 目标不出现则点击第1名
                        if click_domain not in domain_str:
                            id_first = (page_num-1) * 10 + 1
                            print('点击第{0}页第1个'.format(page_num))
                            click_ele(id_first)
                            time.sleep(0.5)
                            driver.execute_script(js_xiala)
                        # 目标出现直接点目标
                        else:
                            for my_real_url, my_order in real_urls_rank:
                                if click_domain in my_real_url:
                                    click_ele(my_order)
                                    is_click = 1
                                    time.sleep(2)
                                    break
        except Exception as e:
            traceback.print_exc(file=open('log.txt', 'w'))
            print(e, '重启selenium')
            driver.quit()
            gc.collect()
            driver = get_driver(chrome_path,chromedriver_path,ua)
        else:
            pass                    
        finally:
            del kwd, click_domain
            gc.collect()
            close_handle()
            exit()
            # q.task_done()


if __name__ == "__main__":
    page_dict = {1:'首页',2:'二页',3:'三页',4:'四页',5:'五页'}  # 查询页码
    # 页面下拉
    js_xiala = 'window.scrollBy(0,{0} * {1})'.format('document.body.scrollHeight', random.random() / 0.2)
    # 点击下一页js
    next_page_click_js = """var pages =document.querySelectorAll('.n');var next_page = pages[pages.length-1];next_page.click()"""
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
    chromedriver_path = 'D:/python3/install/chromedriver.exe'
    ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
    driver = get_driver(chrome_path,chromedriver_path,ua)
    run()
