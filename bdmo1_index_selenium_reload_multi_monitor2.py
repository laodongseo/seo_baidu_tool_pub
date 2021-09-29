# ‐*‐ coding: utf‐8 ‐*‐
"""
selenium持续操作浏览器浏览器会崩溃,所以该脚本由reload_control_mo.py控制,
定时重启,重启前会去重已抓取的词
多线程脚本,默认是1

功能:
   1)指定几个域名,分关键词种类监控首页词数
   2)采集serp所有url,提取域名并统计各域名首页覆盖率
   3)采集了serp上的排名url特征srcid值
   4)支持顶级域名或者其他域名
提示:
  1)相关网站.相关企业.智能小程序.其他人还在搜.热议聚合.资讯聚合.搜索智能聚合.视频全部算在内
    所以首页排名有可能大于10
  2)serp上自然排名mu属性值为排名url,特殊样式mu为空或不存在,
    提取article里url,该url是baidu域名,二次访问才能获得真实url,本脚本直接取baidu链接
  3)2020kwd_url_core_city.xlsx:sheet名为关键词种类,sheet第一列放关键词
结果:
    bdmo1_index_info.txt:各监控站点词的排名及url,如有2个url排名,只取第一个
    bdmo1_index_all.txt:serp所有url及样式特征,依此统计各域名首页覆盖率-单写脚本完成
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


cookie_str = """
PSTM=1615340407; BIDUPSID=F2515E4F29BB88B255962F2CFE19C3F9; __yjs_duid=1_a1942d4ca1a959bb32e3ffff0cf07ad41617946073654; BAIDUID={0}:SL=0:NR=10:FG=1; MSA_WH=375_667; MAWEBCUID=web_HZaROXCyXvOjHUxdDgsRzFWcFvyytfvmhKNANGkMBMqFBkpuhv; MSA_ZOOM=1056; MSA_PBT=148; MSA_PHY_WH=750_1334; FC_MODEL=-1_2_7_0_7.85_0_1_0_0_0_23.18_-1_6_4_6_24_0_1631263335_1631263305%7C9%237.85_-1_-1_6_6_1631263335_1631263305%7C9%230_adbxx_1_0_0_0_128_1631263305; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BAIDUID_BFESS=D568D1B0D0B3879A1E7112528EF2623A:FG=1; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03827201144a0JlvNBhzyaMMfZdwH90RT8OBkn8ABSLhaGIsbPpjPkNdVCsxeqDYr%2F7U8he1Kgj1mSb3qwBV86TLdvd2JIvZaVS5ikyHbS9DWyRRn%2Bbsqce7RMq0iGcmMGJfzwZ5oD0e7BchUkHdy7ClrSG3SzUsRTA3iPbN6vO0jhskOmFqT9WSfjiuoPRIvB61C3OPOH2T%2FKqxLRZsq%2B44dY2z%2FRHfcLmKf3U%2FrxmB81C2YK2cplSOChRA4k8GWM%2FFpgL9eWKDBQXG9r0%2B9oxwyRKuT04Q1%2Fa5%2Fx9l6ZPFhw7P3qyuXExgCEjVCbwaT9MMOYL0vrz33rW5ObnlHVlk8uEJ%2FntWU%2FedvtyK7dwBN9YUkLrhMD7wknzBV7XimErvoGqS7Ys14490981776443311184956874718000; BDRCVFR[PaHiFN6tims]=9xWipS8B-FspA7EnHc1QhPEUf; delPer=0; BDRCVFR[YDNdHN8k-cs]=9xWipS8B-FspA7EnHc1QhPEUf; wpr=0; COOKIE_SESSION=0_0_0_0_0_0_0_0_0_0_0_0_0_1632724773%7C1%230_0_0_0_0_0_0_0_1632724773%7C1; G_PSCBD=105%3A1; G_LAUNCH=105%3A27212082; PSINO=7; BCLID=8122778086092787701; BDSFRCVID=vgkOJeC62xkxKfjH_8JJt_0-QbzD6yQTH6aoiNadLAIWb-7j6rFpEG0PMU8g0K4-gVGPogKK0mOTHUuF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF=tRk8oK-atDvDqTrP-trf5DCShUFsaqTWB2Q-XPoO3KJ-_nD6yhnMbUA3BN0LQCrRBKOrbfbgy4op8P3y0bb2DUA1y4vpKMRUX2TxoUJ25fj8enrDqtnWhfkebPRiJPr9QgbP5lQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wDT8hD6PVKgTa54cbb4o2WbCQ-b7P8pcN2b5oQT8BBULfBpRJ5bRJMKtEL66U8n7s0lOUWJDkXpJvQnJjt2JxaqRC5h7R_p5jDh3Mbl_qbUTle4ROamby0hvctn6cShnaLfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDHt8J50ttJ3aQ5rtKRTffjrnhPF3qqkmXP6-hnjy3bRqMbD5WU7MeU3mBT0V0DuvXUnrQq3Ry6r42-39LPO2hpRjyxv4bU4iBPoxJpOJ5H6B0brIHR7WDqnvbURvD-ug3-7P3x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIEoC0XtK-hhCvPKITD-tFO5eT22-usWJ6m2hcHMPoosIJCBPLbyh43bPOJy58LL4jR2b71LfbUotoHXnJi0btQDPvxBf7p52OUMh5TtUJMexjFbPTPqt4bht7yKMnitIj9-pnG0lQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuDj0WD5O0eats-bbfHD3t3RcVaJ3-qTrnhPF354-fXP6-35KHMI3OabQ_WUAWOlcmBT0V0tDhQaj8Ql37JD6yBlrq5pRNOf3PqjJ8jRDzK-oxJpOuQRbMopk2HR34sUJvbURvD-ug3-7P-x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-j5JIE3-oJqC-MMKoP; BCLID_BFESS=8122778086092787701; BDSFRCVID_BFESS=vgkOJeC62xkxKfjH_8JJt_0-QbzD6yQTH6aoiNadLAIWb-7j6rFpEG0PMU8g0K4-gVGPogKK0mOTHUuF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF_BFESS=tRk8oK-atDvDqTrP-trf5DCShUFsaqTWB2Q-XPoO3KJ-_nD6yhnMbUA3BN0LQCrRBKOrbfbgy4op8P3y0bb2DUA1y4vpKMRUX2TxoUJ25fj8enrDqtnWhfkebPRiJPr9QgbP5lQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0hD0wDT8hD6PVKgTa54cbb4o2WbCQ-b7P8pcN2b5oQT8BBULfBpRJ5bRJMKtEL66U8n7s0lOUWJDkXpJvQnJjt2JxaqRC5h7R_p5jDh3Mbl_qbUTle4ROamby0hvctn6cShnaLfjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhDHt8J50ttJ3aQ5rtKRTffjrnhPF3qqkmXP6-hnjy3bRqMbD5WU7MeU3mBT0V0DuvXUnrQq3Ry6r42-39LPO2hpRjyxv4bU4iBPoxJpOJ5H6B0brIHR7WDqnvbURvD-ug3-7P3x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIEoC0XtK-hhCvPKITD-tFO5eT22-usWJ6m2hcHMPoosIJCBPLbyh43bPOJy58LL4jR2b71LfbUotoHXnJi0btQDPvxBf7p52OUMh5TtUJMexjFbPTPqt4bht7yKMnitIj9-pnG0lQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuDj0WD5O0eats-bbfHD3t3RcVaJ3-qTrnhPF354-fXP6-35KHMI3OabQ_WUAWOlcmBT0V0tDhQaj8Ql37JD6yBlrq5pRNOf3PqjJ8jRDzK-oxJpOuQRbMopk2HR34sUJvbURvD-ug3-7P-x5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-j5JIE3-oJqC-MMKoP; H_PS_PSSID=34648_34446_34067_31254_34554_34712_34584_34504_26350_34724_34627_34691; BA_HECTOR=2g8gag212h85a08hh81gl34nt0q; ZD_ENTRY=baidu; ab_sr=1.0.1_ZGVmMGQ5Y2YxZTAxOGUxMDdlZWM2ZDExOWM1YzFmM2FmMmJlYTM2ZTU1MTk5MWU1ZTg3ZWFjMjA3MDEyZmQwNDdiY2FiNjkxNTI2YTdhNGRmY2FkMjYzODE2NDFjYWM0NjU1MTQwOWMyMGU1ZGRkYzI2MWUxMzJlOGE4NjQyMTMyYmE1MTZlMTBlYzE4MTgxNzY3NTA0YTEzMGM0NDZkZQ==; H_WISE_SIDS=110085_114550_127969_164325_178384_178529_178640_179349_179379_179432_179623_181133_181588_181713_181824_182233_182273_182290_182531_183035_183330_183346_183536_183581_183611_184012_184267_184321_184794_184809_184891_185029_185036_185136_185268_185519_185632_185652_185880_186015_186022_186313_186318_186412_186580_186596_186625_186662_186820_186841_187003_187023_187067_187087_187206_187214_187287_187324_187345_187433_187563_187669_187726_187815_187915_187926_187929_188267_188425_188468; rsv_i=1cdatUPaDm97BsfTtvWyulo5FOphMnmrvW2%2FJA3JMSTb1ulpjNrdsn6YY8alfP9Mw%2BKY66ZZEYKk9Z9ySelBOhm3jpKgjO4; BDSVRTM=431; BDSVRBFE=Go; plus_lsv=e9e1d7eaf5c62da9; Hm_lvt_12423ecbc0e2ca965d84259063d35238=1631067986,1631263304,1631264087,1632736260; Hm_lpvt_12423ecbc0e2ca965d84259063d35238=1632736260; plus_cv=1::m:7.94e+147; SE_LAUNCH=5%3A27212270; __bsi=8919015060149402714_00_48_N_R_9_0303_c02f_Y
"""

# 生成随机cookie
def get_cookie():
    seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lis = []
    [lis.append(random.choice(seed)) for _ in range(33)]
    uid = ''.join(lis)
    return uid


# 获取ua
def get_ua(filepath):
    cookie_list = []
    cookie_list = [line.strip() for line in open(filepath,'r',encoding='utf-8')]
    return cookie_list




# 获取chromedriver及启动的浏览器pid
def get_webdriver_chrome_ids(driver):
    """
    浏览器pid是chromedriver的子进程
    """
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
            kwd_dict[sheet_name]= []
            col_a = sheet_obj['A']
            for cell in col_a:
                kwd = (cell.value)
                # 加个判断吧
                if kwd:
                    q.put([sheet_name,kwd])
        return q, group_list

    # 初始化结果字典
    @staticmethod
    def result_init(group_list):
        result = {}
        for domain in domains:
            result[domain] = {}
            for group in group_list:
                result[domain][group] = {'首页':0,'总词数':0}
        print("结果字典init...")
        return result


    # 获取源码,有异常由run函数的try捕获
    def get_html(self,kwd):
        global cookie_str
        global driver
        html = now_url = ''
        user_agent = random.choice(user_agents)
        cookie_str = cookie_str.strip().format(get_cookie())
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent":user_agent,'Cookie':cookie_str}})
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

    # 提取排名的真实url
    def get_real_urls(self, div_list):
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
                        real_urls_rank.append((rank_url,rank,srcid))
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
                        real_urls_rank.append((link,rank,srcid))
        return real_urls_rank

    # 提取某url的域名部分
    def get_domain(self,real_url):
        domain = None
        if real_url:
            try:
               res = urlparse(real_url)
            except Exception as e:
               print(e,'real_url:error')
            else:
               domain = res.netloc
        return domain


    # 提取某url的顶级域名
    def get_top_domain(self,real_url):
        top_domain = None
        if real_url:
            try:
                real_url = f'http://{real_url}' if not real_url.startswith('http') else real_url
                obj = tld.get_tld(real_url,as_object=True)
                top_domain = obj.fld
            except Exception as e:
                print(e,'top domain:error')
        return top_domain
        

    # 获取某词serp源码首页排名所有域名
    def get_domains(self,real_urls_rank):
            domain_url_dicts = {}
            for real_url,my_order,my_attr in real_urls_rank:
                if real_url:
                    top_domain = self.get_domain(real_url)
                    # 一个词某域名多个url有排名,算一次
                    domain_url_dicts[top_domain] = (real_url,my_order,my_attr) if top_domain not in domain_url_dicts else domain_url_dicts[top_domain]
            return domain_url_dicts

    # 获取某词serp源码首页排名的顶级域名
    def get_top_domains(self,real_urls_rank):
            domain_url_dicts = {}
            for real_url,my_order,my_attr in real_urls_rank:
                if real_url:
                    top_domain = self.get_top_domain(real_url)
                    # 一个词某域名多个url有排名,算一次
                    domain_url_dicts[top_domain] = (real_url,my_order,my_attr) if top_domain not in domain_url_dicts else domain_url_dicts[top_domain]
            return domain_url_dicts


    # 线程函数
    def run(self):
        global driver,webdriver_chrome_ids
        while 1:
            group_kwd = q.get()
            group,kwd = group_kwd
            print(group,kwd)
            try:
                html,now_url = self.get_html(kwd)
                divs_res = self.get_divs(html,now_url)
            except Exception as e:
                traceback.print_exc()
                q.put(group_kwd)
                traceback.print_exc(file=open(f'{today}log.txt', 'a'))
                driver.quit()
                kill_process(webdriver_chrome_ids)
                driver = get_driver(chrome_path, chromedriver_path, ua)
                webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
                print(f'相关pid:{webdriver_chrome_ids}')
                # 定时重启之前崩溃重启后就重写pid
                with open('bdmo1_script_ids.txt', 'w', encoding='utf-8') as f_pid:
                    f_pid.write('\n'.join([str(id) for id in webdriver_chrome_ids]))
            else:
                # 源码ok再写入
                if divs_res:
                    real_urls_rank = self.get_real_urls(divs_res)
                    for my_url,my_order,my_attr in real_urls_rank:
                        lock.acquire()
                        f_all.write(f'{kwd}\t{my_url}\t{my_order}\t{my_attr}\t{group}\n')
                        f_all.flush()
                        lock.release()
                    domain_url_dicts = self.get_top_domains(real_urls_rank)
                    domain_all = domain_url_dicts.keys()
                    # 目标站点是否出现
                    for domain in domains:
                        lock.acquire()
                        if domain not in domain_all:
                              f.write(f'{kwd}\t无\t无\t{group}\t{domain}\n')
                        else:
                            my_url,my_order,my_attr = domain_url_dicts[domain]
                            f.write(f'{kwd}\t{my_url}\t{my_order}\t{group}\t{domain}\t{my_attr}\n')
                            print(my_url, my_order)
                        f.flush()
                        lock.release()
            finally:
                del kwd,group
                gc.collect()
                q.task_done()
                time.sleep(2)
                

if __name__ == "__main__":
    start = time.time()
    local_time = time.localtime()
    # today = time.strftime('%Y%m%d',local_time)
    today = open('the_date.txt','r',encoding='utf-8').readlines()[0].strip()
    user_agents = get_ua('ua_mo.txt')
    domains = ['5i5j.com','lianjia.com','anjuke.com','fang.com','ke.com'] # 目标域名
    my_domain = '5i5j.com' # 自己域名
    js_xiala = 'window.scrollBy(0,{0} * {1})'.format('document.body.scrollHeight',random.random())
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
    chromedriver_path = 'D:/install/pyhon36/chromedriver.exe'
    ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    driver = get_driver(chrome_path,chromedriver_path,ua)
    webdriver_chrome_ids = get_webdriver_chrome_ids(driver)
    print(f'chrome的pid:{webdriver_chrome_ids}')
    with open('bdmo1_script_ids.txt','w',encoding='utf-8') as f_pid:
        f_pid.write('\n'.join([str(id) for id in webdriver_chrome_ids]))

    q,group_list = bdmoIndexMonitor.read_excel('2021kwd_url_core_city.xlsx')  # 关键词队列及分类
    result = bdmoIndexMonitor.result_init(group_list)  # 初始化结果
    f = open(f'{today}bdmo1_index_info.txt','a+',encoding="utf-8")
    f_all = open(f'{today}bdmo1_index_all.txt','a+',encoding="utf-8")
    file_path = f.name
    lock = threading.Lock()
    # 设置线程数
    for i in list(range(1)):
        t = bdmoIndexMonitor()
        t.setDaemon(True)
        t.start()
    q.join()
    f.close()
    f_all.close()

     # 统计查询成功的词数
    with open(file_path,'r',encoding='utf-8') as fp:
         success = int(sum(1 for x in fp)/len(domains))
    end = time.time()
    print(f'查询成功{success}')
