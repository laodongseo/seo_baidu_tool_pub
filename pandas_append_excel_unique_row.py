
# -*- coding:UTF-8 -*-
"""
读取某目录下所有excel文件合并
合并后去重生成excel
(指定excel最大行数,如果合并后总行数小于最大行数则直接生成1个文件，否则按最大行数分别生成多个文件)
"""
import pandas as pd
import os
import math


# 获取某目录下的特定文件(含路径),ext为文件后缀(带点)
def get_files(file_path, ext):
    file_list = []
    dir_or_files = os.listdir(file_path)
    # dir_or_file不带路径
    for dir_or_file in dir_or_files:
        # 添加路径
        dir_file_path = os.path.join(file_path, dir_or_file)
        # 保留文件,去除文件夹
        if not os.path.isdir(dir_file_path):
            if os.path.splitext(dir_file_path)[-1] == ext:
                file_list.append(dir_file_path)
    return file_list



# 按固定行数分割excel
def split_excel(df,split_num):
    rows,cols = df.shape # 行数列数,默认第一列表头不算行数
    value = math.floor(rows/split_num) # 标准分割次数
    rows_format = value*split_num # 标准分割所占用总行数
    new_list = [[i,i+split_num] for i in range(0,rows_format,split_num)]

    # 标准行数文件
    for i_j in new_list:
        i,j = i_j
        excel_small = df[i:j]
        excel_small.to_excel(f'去重分割res_{i}_{j}.xlsx',index=False)

    # 剩余的行分割出的文件
    df[rows_format:].to_excel(f'去重分割res_last.xlsx',index=False)



def main(file_list):
    df_all = pd.DataFrame()
    for file in file_list:
        df = pd.read_excel(file)
        df_all = df_all.append(df)
    print('合并后总行数:',df_all.shape[0])
    df_all.drop_duplicates(inplace=True) if not ColNames else df_all.drop_duplicates(subset=ColNames,inplace=True)
    print('合并去重后行数:',df_all.shape[0])
    if df_all.shape[0] > excel_max_row:
        split_excel(df_all,split_num=split_num)
    else:
        df_all.to_excel('去重res.xlsx',index=False)



if __name__ == "__main__":
    file_path = './dist' # excel文件路径
    excel_max_row = 1000000 # excel最大行数
    split_num = 10000 # 指定分割行数
    # ColNames = None代表整行去重
    ColNames = ['城市']   # 指定去重列(保留第1条出现的数据)
    file_list = get_files(file_path,'.xlsx')
    main(file_list)
