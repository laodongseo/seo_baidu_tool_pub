# ‐*‐ coding: utf‐8 ‐*‐
"""
读取文件关键词
然后排序
"""
import os 


# 获取文件的词
def get_kwds(filepath):
    dicts_kwd = {}
    for kwd in open(filepath,'r',encoding='utf-8'):
        kwd = kwd.strip()
        dicts_kwd[kwd] = dicts_kwd[kwd] + 1 if kwd in dicts_kwd else 1
    return dicts_kwd


# 结果排序
def sort_dict(dicts_kwd):
    res = sorted(dicts_kwd.items(), key=lambda e:e[1], reverse=True)
    for kwd,count in res:
        f_count.write(f'{kwd}\t{count}\n')
        f_count.flush()


if __name__ == "__main__":
    base_file  = 'kwd_serpkwds20230727.txt'
    res_file = os.path.splitext(base_file)[0] + 'sort.txt'
    f_count = open(res_file,'w',encoding='utf-8')
    dict_kwds = get_kwds(base_file)
    sort_dict(dict_kwds)
    f_count.close()