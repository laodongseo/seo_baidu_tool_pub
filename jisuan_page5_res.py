import pandas as pd
import numpy as np

"""
从xxxbdpc1_page5_info.txt
分城市分域名计算首页到前五页

"""
def jisuan(txt_file,date,pc_or_mo):
    with pd.ExcelWriter(f'{date}{pc_or_mo}page5_domains.xlsx') as writer:
        page_types = ['首页','二页','三页','四页','五页']
        df_all = pd.read_table(txt_file,names=['kwd','url','rank','city','domain','style','page_num'])
        domains = df_all['domain'].drop_duplicates().values.tolist()
        citys = df_all['city'].drop_duplicates().values.tolist()
        for city in citys:
            dict_city = {}
            dict_city_res = {}
            df_city = df_all[df_all['city']==city]
            for domain in domains:
                dict_city[domain] = {}
                dict_city_res[domain] = {}
                df_city_domain = df_city[df_city['domain'] == domain]
                for page_num in page_types:
                    df_city_domain_page=df_city_domain[df_city_domain['page_num'] == page_num]
                    dict_city[domain][page_num] = len(df_city_domain_page)

            for domain,dict_values in dict_city.items():
                dict_city_res[domain]['首页'] = dict_city[domain]['首页']
                dict_city_res[domain]['前二页'] = dict_city[domain]['首页'] + dict_city[domain]['二页']
                dict_city_res[domain]['前三页'] = dict_city[domain]['首页'] + dict_city[domain]['二页'] + dict_city[domain]['三页']
                dict_city_res[domain]['前四页'] = dict_city[domain]['首页'] + dict_city[domain]['二页'] + dict_city[domain]['三页'] + dict_city[domain]['四页']
                dict_city_res[domain]['前五页'] = dict_city[domain]['首页'] + dict_city[domain]['二页'] + dict_city[domain]['三页'] + dict_city[domain]['四页'] + dict_city[domain]['五页']

            print(dict_city_res)
            df_city_now = pd.DataFrame(dict_city_res)
            df_city_now.index.name = city
            df_city_now.to_excel(writer,sheet_name=str(city))


if __name__ =="__main__":
    date,pc_or_mo = '20210308','bdpc1'
    txt_file = f'{date}{pc_or_mo}_page5_info.txt'
    jisuan(txt_file,date,pc_or_mo)
