
# -*- coding:UTF-8 -*-
"""
读取某目录下excel
指定1列或者多列分别去重每个excel(默认保留第1条数据)
"""
import pandas as pd
import os


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


def main(file_list):
    for file in file_list:
        df = pd.read_excel(file)
        print('去重:',file)
        df.drop_duplicates(inplace=True) if not ColNames else df.drop_duplicates(subset=ColNames,inplace=True)
        base_name = os.path.basename(file)
        file_name = os.path.splitext(base_name)[0]
        new_file = os.path.join(new_path,f'{file_name}_unique.xlsx')
        df.to_excel(new_file,index=False)

if __name__ == "__main__":
    file_path = './dist' # 原excel存储路径
    new_path = './1' # 去重后存储路径
    # ColNames = None代表整行去重
    ColNames = ['城市']   # 指定去重列(保留第1条出现的数据)
    file_list = get_files(file_path,'.xlsx')
    main(file_list)
