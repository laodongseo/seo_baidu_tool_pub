# -*- coding:UTF-8 -*-
"""
默认3种分词
结巴模块基于tf-idf分词
结巴模块搜索引擎模式分词
北京大学的pkuseg模块分词
"""
import sys
import pymysql
import time
import jieba.analyse
import openpyxl
import pkuseg


def get_mode():
    return {'mode1':'jieba.analyse.extract_tags(title, topK = 10, withWeight = False, allowPOS = ())',
    'mode2':'jieba.cut_for_search(title)',
    'mode3':'seg.cut(title)',}


# 连接mysql
def con_mysql(dbconf,retry=2):
    try:
       conn = pymysql.connect(**dbconf)
    except Exception as e:
        print(e)
        time.sleep(10)
        if retry > 0:
            con_mysql(dbconf,retry-1)
    else:
        print('mysql成功连接')
        return conn


# 提取数据
def get_content(cursor,data_sheet):
    all_data = ''
    sql = f"select id,title from {data_sheet}"
    # 执行sql
    try:
        row_num = cursor.execute(sql)  # 提交执行，返回sql影响成功的行数
        all_data = cursor.fetchall()
    except Exception as e:
        print('get_content...error',e)
    return all_data

def create_excel(my_modes,data_sheet):
	excel_dict = {}
	for mode in my_modes:
		wb = openpyxl.Workbook()
		ws = wb.create_sheet(f'{data_sheet}',index=0) # sheet创建
		excel_dict[mode] = (wb,ws)
	return excel_dict


def main(data_sheet):
    conn = con_mysql(dbconfig)
    if not conn:
        print('数据库连接失败,exit..')
        sys.exit()
    cursor = conn.cursor()  # 游标
    all_data = get_content(cursor,data_sheet) # 数据
    excel_dict = create_excel(my_modes,data_sheet)
    for mode in my_modes:
        print('分词模式...',mode)
        wb,ws = excel_dict[mode][0],excel_dict[mode][1]
        fenci_fun = dict_modes[mode]
        for row in all_data:
            try:
                id,title = row
                new_row = [id,title]
                tags = eval(fenci_fun)
                tags = [kwd for kwd in tags if kwd not in stop_words]
            except Exception as e:
                tags = []
            new_row.extend(tags)
            ws.append(new_row)
        wb.save(f'{data_sheet}_{mode}.xlsx')


if __name__ =="__main__":
    # 数据库
    dbconfig = dict(
        host="139.196.219.44",
        db="content",
        charset="utf8mb4",
        user="root",
        password = "wocaoseo2020",
        port=3306,
        # cursorclass=pymysql.cursors.DictCursor
    )
    # 数据表
    data_sheet = 'kuaiben'
    jieba.enable_paddle()
    seg = pkuseg.pkuseg()
    # 分词模式
    dict_modes = get_mode()
    stop_words = [i.strip() for i in open('stop_words.txt','r',encoding='utf-8')]
    my_modes = ['mode1','mode2','mode3']
    # 保存文件
    main(data_sheet)
