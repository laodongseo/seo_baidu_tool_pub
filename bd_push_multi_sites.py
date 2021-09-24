# ‐*‐ coding: utf‐8 ‐*‐
import requests
import time
import pandas as pd
import traceback
import urllib
"""
多域名推送
每个sheet存1个域名数据
每个sheet的表头：url token   domain

"""


# all_urls二维列表,每个元素为2000url
def push_url(domain,token,all_urls,retry=1):
    if  all_urls == []:
        return '下一个'
    post_url = f'http://data.zz.baidu.com/urls?site=https://{domain}&token={token}'
    print(post_url)
    for data_urls in all_urls:
        try:
            str_urls = '\n'.join(data_urls)
            str_urls = str_urls.encode('utf-8') # 防止中文url报错
            r = requests.post(post_url,data=str_urls,headers=user_agent,timeout=10)
        except Exception as e:
            print('请求失败,暂停15秒')
            traceback.print_exc()
            time.sleep(15)
            break
            if retry > 0:
                push_url(post_url,domain,all_urls,retry-1)
        else:
            html = r.json()
            status = r.status_code
            if status == 200:
                if html['success'] > 0:
                    print(domain,html)
                else:
                    print(f'{domain}:推送数据为0,请检查配置')
                    return '下一个'
            else:
                print(domain,html)
                return '下一个'




# 读取excel,每个sheet化成二维列表
def main(filepath):
    df_dict = pd.read_excel(filepath,sheet_name=None)
    for sheet_name,df_sheet in df_dict.items():
        sheet_urls = df_sheet['url'].values.tolist()
        domain,token = df_sheet['domain'][0],df_sheet['token'][0]
        if len(sheet_urls) >1999:
            list_format = [sheet_urls[i:i + 2000] for i in range(0, len(sheet_urls), 2000)]
        else:
            list_format = [sheet_urls]  # 如果连接数量 <2000则取全部连接
        # 死循环每个域名把配额用到无法接收单次的推送量
        post_num = 0
        while 1:
            res = push_url(domain,token,list_format)
            time.sleep(1)
            post_num+=1
            print(domain,token,post_num,'次')
            if '下一个' == res:
                break


if __name__ == "__main__":
    f = open('push_fail.txt','w',encoding='utf-8') # 推送失败的url
    user_agent = {
        'User - Agent':'curl / 7.12.1',
        'Host':'data.zz.baidu.com',
        'Content - Type':'text/plain',
        'Content - Length':'83'
    }

    main('租房二手房列表_unique_domain_multi_sheet.xlsx')
    
    f.close()

