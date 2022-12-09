"""
1条url下有多个回答,每个回答是1行
本脚本完成1条url下多行合并
同时按条件筛选出指定字数的数据分到不同sheet
"""
#‐*‐coding:utf‐8‐*‐
import pandas as pd
import time

def concat_func(s):
	merge_content = []
	row_list = s.tolist()
	for i in range(0,len(row_list)):
		row_html_content = row_list[i]
		row_html_content_add = f'<p>　　<strong>第{i+1}部分内容</strong>：</p>{row_html_content}'
		merge_content.append(row_html_content_add)
	return ''.join(merge_content)


def read_excel(filepath):
	df = pd.read_excel(filepath)
	gb_obj = df.groupby('url')
	print('分组后个数',gb_obj.ngroups)

	# 计算合并后内容长度
	df['文章长度合并'] = gb_obj['文章长度'].transform('sum')
	# 增加1列代表每组内的回答合并
	df[f'{Col_Content_Name}合并'] = gb_obj[Col_Content_Name].transform(concat_func)

	with pd.ExcelWriter('answer_merge.xlsx',engine='xlsxwriter',engine_kwargs={"options":{'strings_to_urls': False}}) as writer:
		# 只保留1行回答即可
		df = df.drop_duplicates(subset=['url']) 
		for i in [350,400,450,500]:
			df_gtnum = df[df['文章长度合并'] >= i]
			df_gtnum.to_excel(writer,index=False,sheet_name=f'字数大于{i}')
		df.to_excel(writer,index=False,sheet_name='所有')


if __name__ == "__main__":
	s_time = time.time()
	Col_Content_Name = '答案html_filter' # 需要合并同类项的列
	read_excel('toutiao_answer_res_filter.xlsx')
	e_time = time.time()
	print((e_time - s_time) / 60 ,'min')
