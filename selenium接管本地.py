# ‐*‐ coding: utf‐8 ‐*‐
"""
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\selenum\AutomationProfile"
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import traceback
import re
import os

s1 = r""" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenum\AutomationProfile" """
s2 = r""" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 """
# os.system(s2)

def get_driver(chrome_path, chromedriver_path, ua):
    ua = ua
    option = Options()
    option.add_argument("user-agent=" + ua)
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=option, executable_path=chromedriver_path)
    return driver


chrome_path = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
chromedriver_path = r'D:\install\pyhon36/chromedriver.exe'
ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
print(111)
# os.popen(s2)
print(123)
driver = get_driver(chrome_path,chromedriver_path,ua)
driver.get('https://www.ixigua.com/6807981414202475012?logTag=3Cxa5FUED2WPW5MFEpKRR&wid_try=1')
time.sleep(3)
driver.get('https://www.ixigua.com/6549004106046898691?logTag=sbe6ZEkiniggTjKjrS5dZ')
