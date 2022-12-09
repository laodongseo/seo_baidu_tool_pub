"""
读取excel
给正文添加img标签且增加1列记录图片名字
"""

#‐*‐coding:utf‐8‐*‐
import pandas as pd
import random,string,os,shutil,traceback
from PIL import Image, ImageDraw, ImageFont
import threading,queue
import queue,time


# 生成图片
def image_add_text(text, logo,img_res):
	# 随机获取一张图片
	img = random.choice(all_imgs)
	# 补全图片路径
	img_path = os.path.join(img_folder, img)
	# 用RGBA的模式打开图片
	im = Image.open(img_path).convert("RGBA")
	# 创建一张和原图一样大小的图片
	txt_img = Image.new('RGBA', im.size, (0, 0, 0, 0))
	# 设置字体大小，字体的个数除以图片的长度
	font_size = (txt_img.size[0] // len(text))
	logo_font_size = font_size // 2
	# 设置使用的字体
	tfont = ImageFont.truetype(os.path.join(curdir, FontPath),
							   size=font_size)
	logofont = ImageFont.truetype(os.path.join(curdir, FontPath),
								  size=logo_font_size)
	# 在新建的图片上添加文字
	draw = ImageDraw.Draw(txt_img)
	# 获取字体大小和位置
	text_x, text_y = draw.textsize(text, font=tfont)
	xz, yz = (txt_img.size[0] - text_x) / 2, (txt_img.size[1] - text_y) / 2
	lx, ly = (txt_img.size[0] - logo_font_size * len(logo)), (txt_img.size[1] - logo_font_size * 2)
	draw.text((xz, yz), text=text, fill='#00008B', font=tfont)

	# print(txt_img.size, lx, ly, xz, yz)
	draw.text((lx, ly), text=logo, fill='#00008B', font=logofont)
	# 合并图片
	out = Image.alpha_composite(im, txt_img)
	# 转为RGB好输出为jpg，不转的话就必须是png
	out = out.convert('RGB')
	# 保存
	out.save(img_res)



def get_pwd(length):
	# ofnum个数字
	# slcNum=[random.choice(string.digits) for i in range(Ofnum)]
	# length个字母
	slcLetter=[random.choice(string.ascii_letters) for i in range(length)]
	random.shuffle(slcLetter)
	ret =''.join(slcLetter)
	return ret

def read_excel(filepath):
	q = queue.Queue()
	df = pd.read_excel(filepath).dropna()
	for index,row in df.iterrows():
		row['pic_index'] = index
		q.put(row)
	return q


def main():
	global IsHeader,PicHome
	while True:
		row = q.get()
		index = row['pic_index']
		content_list = row[Col_Article].split('</p>')
		content_list = [f'{i}</p>' for i in content_list if i.strip()]
		duanluo_count = len(content_list)
		print(index,row['title'],duanluo_count)

		img1 = f'{PicHome}/{index}{get_pwd(1)}.jpg'
		img2 = f'{PicHome}/{index}{get_pwd(2)}.jpg'
		img3 = f'{PicHome}/{index}{get_pwd(3)}.jpg'

		img1_html = f'<p>　　<img src="{PicDomain}/{img1}"/></p>'
		img2_html = f'<p>　　<img src="{PicDomain}/{img2}"/></p>'
		img3_html = f'<p>　　<img src="{PicDomain}/{img3}"/></p>'
		try:
			# 插入图片
			if duanluo_count > 5:
				# 选取3个位置
				loc1 = random.randint(1,int(duanluo_count/3))
				loc2 = random.randint(int(duanluo_count/3)+1,duanluo_count)
				content_list.insert(loc1,img1_html) # 插入图片
				content_list.insert(loc2 + 1,img2_html) #插入loc1后元素个数+1,所以此处loc2+1
				content_list.insert(-1,img3_html) # 倒数第一行前插入
				row['图片'] = f'{img1}#{img2}#{img3}' # 增加1列记录图片位置
				image_add_text(text=row['title'],logo='',img_res=img1) #生成图片
				image_add_text(text=row['title'],logo='',img_res=img2) #生成图片
				image_add_text(text=row['title'],logo='',img_res=img3) #生成图片
			elif duanluo_count > 1:
				# 选取2个位置
				loc1 = random.randint(1,int(duanluo_count/2))
				loc2 = random.randint(int(duanluo_count/2)+1,duanluo_count)
				content_list.insert(loc1,img1_html) # 插入图片
				content_list.insert(loc2 + 1,img2_html) #插入loc1后元素个数+1,所以此处loc2+1
				row['图片'] = f'{img1}#{img2}' # 增加1列记录图片位置
				image_add_text(text=row['title'],logo='',img_res=img1) #生成图片
				image_add_text(text=row['title'],logo='',img_res=img2) #生成图片
			else:
				content_list.insert(1,img1_html)
				row['图片'] = f'{img1}'
				image_add_text(text=row['title'],logo='',img_res=img1) #生成图片

			# 文章插入图片
			row[Col_Article_Img] = ''.join(content_list)
		except Exception as e:
			traceback.print_exc()
			q.put(row)
			with lock:
				PicHome = f'{PicHome}2'
				os.mkdir(PicHome) if not os.path.exists(PicHome) else 1
		else:
			with lock:
				df = row.to_frame().T
				if IsHeader == 0:
					df.to_csv(CsvFile,encoding='utf-8-sig',mode='w+',index=False,sep='\t')
					IsHeader = 1
				else:
					df.to_csv(CsvFile,encoding='utf-8-sig',mode='a+',index=False,header=False,sep='\t')
		finally:
			q.task_done()




if __name__ == "__main__":
	PicHome = 'myimg' # 生成的图片路径
	PicDomain = 'http://cdnzhi.python66.com'
	Col_Article = 'article'
	Col_Article_Img = 'article_img'
	os.mkdir(PicHome) if not os.path.exists(PicHome) else shutil.rmtree(PicHome)
	os.mkdir(PicHome) if not os.path.exists(PicHome) else 1
	FontPath = r'C:\Windows\Fonts\simkai.ttf'
	curdir = os.path.dirname(os.path.abspath(__file__))
	img_folder = os.path.join(curdir, "image_template")
	all_imgs = os.listdir(img_folder)
	IsHeader = 0
	lock = threading.Lock()
	q = read_excel('answer_merge_splittext_uq.xlsx')
	CsvFile = 'toutiao_answer_article_imgres.csv'

	for i  in range(1):
		t = threading.Thread(target=main)
		t.setDaemon(True)
		t.start()
	q.join()

