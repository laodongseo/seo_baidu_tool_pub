# ‐*‐ coding: utf‐8 ‐*‐
"""
读取某文件夹内的txt文件
依次转为excel
"""
import pandas as pd
import os
import xlsxwriter


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


def main(txt_files):
    for txt_file in txt_files:
        base_name = os.path.basename(txt_file)
        file_name = os.path.splitext(base_name)[0]
        excel_file = os.path.join(excel_path,f'{file_name}.xlsx')
        print(excel_file)
        df = pd.read_csv(txt_file,sep='\t',names=Columns)
        df.to_excel(excel_file,index=False,engine='xlsxwriter')
        print(f'{txt_file}---生成--->>{excel_file}')


if __name__ == "__main__":
    txt_path = './excel_txt/'
    excel_path = './excel_done/'
    # 表头
    Columns = ['产品ID','标题','关键词','主图','信誉','旺旺号','价格','付款人数','pdd_id','pdd_销量','pdd_价格','pdd_类目','pdd_标题','pdd_图片','tb/pdd','tb-pdd']
    txt_files = get_files(txt_path,'.txt')
    main(txt_files)
