# ‐*‐ coding: utf‐8 ‐*‐
"""
对文件中的url提取域名
去重并统计域名出现次数
"""

from urllib.parse import urlparse
import pandas as pd 


def get_domain(link):
    try:
        o = urlparse(link)
    except Exception as e:
        return 'xxx'
    else:
        return o.netloc


def do(txt_file):
    df = pd.read_table(txt_file,names=['url'])
    df['domain'] = df['url'].apply(get_domain)
    df['domain'].value_counts().to_excel('domain_value.xlsx')



if __name__ == "__main__":
    txt_file = './bdpc_real.txt'
    do(txt_file)

