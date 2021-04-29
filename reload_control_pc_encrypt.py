# -*- coding: utf-8 -*-

"""
控制点击脚本的执行
每次开启前尝试杀死再执行的点击脚本进程,chrome及chromedriver进程
日期和文件名写死
"""
import os
import re
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import gc
import pandas as pd
from openpyxl import load_workbook
from openpyxl import Workbook


# 获取目标python脚本产生的python进程id
def get_process_id(py_script_name):
    ids = []
    result = os.popen('wmic process where name="python.exe" get processid,commandline')
    res = result.read()
    res = res.strip().splitlines()
    for line in res:
        print(line)
        if py_script_name in line:
            lis = line.split(' ')
            for element in lis:
                element = element.strip()
                re_ret = re.search('^\d+$',element)
                if re_ret:
                    id = re_ret.group()
                    ids.append(id)
    return ids


# 根据id杀死进程
def kill_ids(p_ids):
    for pid in p_ids:
        try:
            os.system('taskkill /f /pid {0}'.format(pid))
            print('kill id',pid)
        except:
            pass


# 读取excel的总词 kwd city列
def read_excel(filepath):
    df_kwd_all = pd.DataFrame(columns=['kwd','city'])
    wb_kwd = load_workbook(filepath)
    for sheet_obj in wb_kwd:
        sheet_name = sheet_obj.title
        col_a = sheet_obj['A']
        sheet_kwds = [[cell.value,sheet_name] for cell in col_a if cell.value]
        df_sheet = pd.DataFrame(data=sheet_kwds,columns=['kwd','city'])
        df_kwd_all = pd.concat([df_kwd_all,df_sheet],axis=0)
    return df_kwd_all


# 获取已经抓取结果,防止误差把最后一个词的结果删除重新生成一遍结果
def get_res_now(new_file,columns):
    df = pd.read_table(new_file,names=columns)
    if len(df) > 0:
        df_last_row = df.iloc[-1] # 最后1行
        city = df_last_row['city']
        kwd = df_last_row['kwd']
        bool_if = (df['kwd'] == kwd) & (df['city'] == city)
        df_res = df[~bool_if]
        df_res.to_csv(new_file,sep='\t',index=False,header=False,mode='w')
        df_now_kwd = df_res[['kwd','city']]
        return df_now_kwd.drop_duplicates()
    else:
        return df.drop_duplicates()


# 差集
def chaji(df_kwd_all,df_now_kwd):
    df_kwd_all = df_kwd_all.append(df_now_kwd)
    df_kwd_all = df_kwd_all.append(df_now_kwd)
    set_diff_df = df_kwd_all.drop_duplicates(keep=False)
    return set_diff_df


# 差集写到excel
def to_new_excel(df,colname):
    city_uniques = df[colname].drop_duplicates().to_list()
    with pd.ExcelWriter(kwd_temp_excel) as excel_writer:
        # 循环每一类写入
        for col in city_uniques:
            bool_df = df[colname] == col
            my_df = df[bool_df]
            my_df.to_excel(excel_writer,sheet_name=col,index=False,header=False)


# 启动前先把存在的杀死
def go_run():
    ids = get_process_id(py_script_name)
    print(ids)
    kill_ids(ids)
    chrome_driver_ids = [id.strip() for id in open('bdpc1_script_ids.txt','r',encoding='utf-8')]
    print(chrome_driver_ids)
    kill_ids(chrome_driver_ids)
    time.sleep(2)
    df_kwd_all = read_excel(kwd_all_excel)
    print('总词表:',df_kwd_all.shape)
    df_now_kwd = get_res_now(res_data_file,columns)
    print('已抓取的结果',df_now_kwd.shape)
    diff_df = chaji(df_kwd_all,df_now_kwd)
    print('剩余的结果',diff_df.shape[0])
    if diff_df.shape == (0,0):
        return
    to_new_excel(diff_df,'city')
    print("写入excel完毕")
    del df_kwd_all
    gc.collect()
    os.system(cmd_str)



if __name__ == "__main__":
    start = time.time()
    today = time.strftime('%Y%m%d', time.localtime())
    now_date = '20210419' # 和py_script_name脚本写死的日期相同
    kwd_all_excel = '2021xiaoqu_kwd_city_副本.xlsx' # 总kwd
    kwd_temp_excel = '2021xiaoqu_kwd_city.xlsx' # 每次剩余待抓取的kwd
    py_script_name = 'bdpc1_index_encrypt_selenium_reload_multi_monitor2.py'
    res_data_file = f'{now_date}bdpc1_index_encrypt_all.txt' # 存储现有结果的txt文件特征
    columns = ['kwd','encrypt_url','rank','style','city','is_jiami']
    if not os.path.exists(f'{now_date}{res_data_file}'):
        f = open(res_data_file,'a+',encoding='utf-8')
        f.close()
    # cmd命令
    cmd_str = f'python {py_script_name}'
    # 定时执行任务
    schedudler = BlockingScheduler()
    # 每隔多少秒执行1次
    schedudler.add_job(go_run, 'interval', seconds=1800,max_instances=10000,misfire_grace_time=3600)
    schedudler.start()
