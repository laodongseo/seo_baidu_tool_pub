# ‐*‐ coding: utf‐8 ‐*‐

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
        f_count.write('{0}\t{1}\n'.format(kwd,count))
        f_count.flush()

if __name__ == "__main__":
    base_file  = 'bdpc_xiala'
    f_count = open(f'{base_file}_sort.txt','w',encoding='utf-8')
    dict_kwds = get_kwds(f'{base_file}.txt')
    sort_dict(dict_kwds)
    f_count.close()
