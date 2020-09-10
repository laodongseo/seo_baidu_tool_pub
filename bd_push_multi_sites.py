# ‐*‐ coding: utf‐8 ‐*‐
import requests
import time
"""
多站点配置文件conf.txt 格式如下
qd.xxx.com=tuz16xxxxNuxa2E=qd.txt
sh.xxx.com=tuz16xxxxNuxa3E=sh.txt
qd.txt存放qd的url 一行一个
sh.txt存放sh的url 一行一个
每个域名用完配额以后会进行下一个域名的推送
"""


# 读取配置
def read_config(filepath):
    configs = open(filepath,'r',encoding='utf-8').readlines()
    configs = [line.strip() for line in configs]
    return configs

# 读取url文件格式化成二维列表
def read_txt(filepath):
    all_urls = open(filepath,'r',encoding='utf-8').readlines()
    try:
        list_format = [all_urls[i:i + 2000] for i in range(0, len(all_urls), 2000)]
    except Exception as e:
        list_format = all_urls  # 如果连接数量 <2000则取全部连接
    finally:
        return list_format


# 推送url函数
def push_url(domain,retry=1):
            if  all_urls == []:
                return '下一个'
            for data_urls in all_urls:
                try:
                    str_urls = ''.join(data_urls)
                    r = requests.post(post_url,data=str_urls,headers=user_agent,timeout=5)
                except Exception as e:
                    print('请求失败,暂停15秒',e)
                    time.sleep(15)
                    if retry > 0:
                        push_url(retry-1)
                else:
                    html = r.json()
                    keys = [ key for key,value in html.items()]
                    values = [ value for key,value in html.items()]
                    if 'success' in keys:
                        print(domain,'推送成功',len(data_urls))
                    elif 'error' in keys and 'over quota' in values:
                        print(domain,'配额不够,开始下一个域名推送',html)
                        return '下一个'
                    elif 'error' in keys and 'site' in values:
                        print(domain,'站点配置错误,略过',html)
                        return '下一个'
                    else:
                        f.write(str_urls)
                        f.flush()
                        print(domain,'推送失败，保存到文件',html)



if __name__ == "__main__":
    f = open('push_fail.txt','w',encoding='utf-8') # 推送失败的url
    user_agent = {
        'User - Agent':'curl / 7.12.1',
        'Host':'data.zz.baidu.com',
        'Content - Type':'text / plain',
        'Content - Length':'83'
    }

    configs = read_config('conf.txt')
    for line in configs:
        lis = line.split('=')
        domain = lis[0]
        print('开始推送',domain)
        token = lis[1]
        file_txt = lis[2]
        all_urls = read_txt(file_txt)  # 二维列表每组2000个url
        post_url = 'http://data.zz.baidu.com/urls?site=https://{0}&token={1}'.format(domain, token)
        # 死循环每个域名把配额用完
        while 1:
            time.sleep(1)
            res = push_url(domain)
            if '下一个' == res:
                break

    f.close()

