# ‐*‐ coding: utf‐8 ‐*‐


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def get_html(kwd, retry=2):
    try:
        driver.get('https://www.baidu.com/')
        # 输入框元素,显式等待设定最多15秒
        input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "kw"))
        )
        input.click()  # 先click后clear,直接send_keys容易丢失字符
        input.clear()
        # 输入文字
        for wd in kwd:
            input.send_keys(wd)
        # 搜索按钮元素,显式等待设定最多15秒
        baidu = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "su"))
        )
        # 点击搜索
        baidu.click()
        # 等待下一页元素加载
        next_page = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "n"))
        )
        # 滚动条到底部
        driver.execute_script(js)
    except Exception as e:
        print(e)
        time.sleep(10)
        if retry > 0:
            get_html(kwd, retry - 1)
    else:
        html = driver.page_source
    return html


if __name__ == "__main__":

    pc_ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
    option = Options()
    prefs = {
        'profile.default_content_setting_values': {
            'images' : 2, # 禁止图片加载
            'notifications': 2  # 禁止弹窗
        }
    }
    option.add_experimental_option('prefs', prefs)
    js = 'window.scrollBy(0,{0})'.format('document.body.scrollHeight')
    driver = webdriver.Chrome(options=option)
    html = get_html('我爱我家')


