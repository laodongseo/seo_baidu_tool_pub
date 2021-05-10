# ‐*‐ coding: utf‐8 ‐*‐
import requests
import time
import pandas as pd
"""
多域名推送
每个sheet为1个域名数据
excel每个sheet的表头：url token   domain

"""


# all_urls二维列表,每个元素为2000url
def push_url(domain,token,all_urls,retry=1):
    if  all_urls == []:
        return '下一个'
    post_url = f'http://data.zz.baidu.com/urls?site=https://{domain}&token={token}'
    for data_urls in all_urls:
        try:
            str_urls = ''.join(data_urls)
            r = requests.post(post_url,data=str_urls,headers=user_agent,timeout=5)
        except Exception as e:
            print('请求失败,暂停15秒',e)
            time.sleep(15)
            if retry > 0:
                push_url(post_url,domain,all_urls,retry-1)
        else:
            html = r.json()
            keys = [ key for key,value in html.items()]
            values = [ value for key,value in html.items()]
            if 'success' in keys:
                print(domain,'推送成功',len(data_urls))
            elif 'error' in keys and 'over quota' in values:
                print(domain,'配额不够,开始下一个域名推送',html)
                return '下一个'
            elif 'error' in keys and 'site error' in values:
                print(domain,'站点配置错误,略过',html)
                return '下一个'
            else:
                f.write(str_urls)
                f.flush()
                print(domain,'推送失败，保存到文件',html)


# 读取excel,每个sheet化成二维列表
def main(filepath):
    df_dict = pd.read_excel(filepath,sheet_name=None)
    for sheet_name,df_sheet in df_dict.items():
        sheet_urls = df_sheet['url'].values.tolist()
        domain,token = df_sheet['domain'][0],df_sheet['token'][0]
        print(domain,token)
        try:
            list_format = [sheet_urls[i:i + 2000] for i in range(0, len(sheet_urls), 2000)]
        except Exception as e:
            list_format = sheet_urls  # 如果连接数量 <2000则取全部连接
        finally:
            # 死循环每个域名把配额用到无法接收单次的推送量
            while 1:
                res = push_url(domain,token,list_format)
                time.sleep(1)
                if '下一个' == res:
                    break


if __name__ == "__main__":
    f = open('push_fail.txt','w',encoding='utf-8') # 推送失败的url
    user_agent = {
        'User - Agent':'curl / 7.12.1',
        'Host':'data.zz.baidu.com',
        'Content - Type':'text / plain',
        'Content - Length':'83'
    }

    main('url_domain_multi_sheet.xlsx')
    
    f.close()

