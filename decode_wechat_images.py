#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os,sys
import gc
from datetime import datetime
from dateutil.relativedelta import relativedelta

#微信的文件存储所在目录
g_wx_files_path=""
g_wx_sub_paths=[]
g_wx_dat_key = 0x00


# 定义统计指定文目录大小的函数
# 可使用 os.stat().st_size	替换 os.path.getsize()
def	dir_size(dir):
	size = 0
	# 指定目录是否为文件
	if os.path.isfile(dir):
		size +=	os.path.getsize(dir)
	# 指定目录是否为文件夹
	if os.path.isdir(dir):
		dir_lst	= os.listdir(dir)
		# 遍历目录
		for	i in dir_lst:
			file = os.path.join(dir, i)
			if os.path.isfile(file):
				size +=	os.path.getsize(file)
			if os.path.isdir(file):
				size +=	dir_size(file)
	return size

# 格式化文件大小的函数
def	format_size(size):
	formatbyte = [(1024	** 3, "GB"), (1024 ** 2, "MB"),	(1024, "KB")]
	for	(scale,	lable) in formatbyte:
		if size	>= scale:
			byte = "%.2f" %	(size /	scale)
			byte[:-3] if byte.endswith('.00') else byte
			return "文件大小: {1} {2}	({0:,}	字节)".format(size, str(byte), lable)
		elif size == 0:
			return "文件大小: 0	字节"
		else:
			pass
	return "文件大小: {0}	字节	({0:,} 字节)".format(size)

#列出当前目录所有的dat文件列表
def list_image_dat_files(aDir, aList):
	dir_lst	= os.listdir(aDir)
	# 遍历目录
	for	i in dir_lst:
		file = os.path.join(aDir, i)
		if os.path.isfile(file):
			if (os.path.basename(file)[-4:] != '.dat'):
				continue
			aList.append(file)
		if os.path.isdir(file):
			list_image_dat_files(file , aList)
	

#探测您的Image文件的解码Key是多少。
def detect_decode_key(aFile):
	#检测10个文件，确认解码用的key值
	if (os.path.basename(aFile)[-4:] != '.dat'):
		print("Skip. %s" % os.path.basename(aFile))
		return
	dat	= open(aFile, "rb")
	aStd=[[0xFF, 0xD8],[0x89, 0x50], [0x47, 0x49]] 
	bHead= dat.read(2)
	dat.close()
	global g_wx_dat_key
	gc.collect()
	for bKey  in range(0xFF) :
		bHead2 = []
		bHead2.append( bHead[0] ^ bKey )
		bHead2.append( bHead[1] ^ bKey )
		for i, fExt in enumerate(aStd):
			if (bHead2[0] == fExt[0]) and (bHead2[1] == fExt[1]):
				print("%s		OK. " % os.path.basename(aFile)[:-4] )
				g_wx_dat_key = bKey
				return True
	return False

def	image_dat_file_decoding(f, fExt):
	dat	= open(f, "rb")
	out	= f[:-4] + "." + fExt
	png	= open(out,	"wb")
	for	now	in dat:
		for	nowByte	in now:
			newByte	= nowByte ^	g_wx_dat_key #修改为自己的解密码
			png.write(bytes([newByte]))
	dat.close()
	png.close()
	#os.remove(f)

#jpg FF	D8
#png 89	50
#gif 47	49

def convert_dat_files(aFile):
	if (os.path.basename(aFile)[-4:] != '.dat'):
		print("Skip. %s" % os.path.basename(aFile))
		return
	dat	= open(aFile, "rb")
	aStd=[[0xFF, 0xD8],[0x89, 0x50], [0x47, 0x49]] 
	bHead= dat.read(2)
	dat.close()
	gc.collect()
	bHead2 = []
	bHead2.append( bHead[0] ^ g_wx_dat_key )
	bHead2.append( bHead[1] ^ g_wx_dat_key )
	for i, fExt in enumerate(aStd):
		if (bHead2[0] == fExt[0]) and (bHead2[1] == fExt[1]):
			print("%s		OK. " % os.path.basename(aFile)[:-4] )
			if i==0:
				image_dat_file_decoding(aFile, "jpg")
			if i==1:
				image_dat_file_decoding(aFile, "png")
			if i==2:
				image_dat_file_decoding(aFile, "gif")
			return 
	print("Fail. ")
	


def cmd_setting_wx_path():
	print("\n请输入微信文件所在目录，  例如：")
	print("C:\Data.Tencent\WeChat\WeChat Files\{mywechat_id}\FileStorage")
	tmpPath = input("\n请输入微信文件所在目录:	")
	if tmpPath=="":
		tmpPath = r"E:\Data.Tencent\WeChat\WeChat Files\mywechat_id\FileStorage"
	if (os.path.exists(tmpPath) == True and \
		os.path.exists(os.path.join(tmpPath, "Image/")) == True and		\
		os.path.exists(os.path.join(tmpPath, "Video/")) == True and		\
		os.path.exists(os.path.join(tmpPath, "File/")) == True) :
			global g_wx_files_path 
			g_wx_files_path = tmpPath
			print("\n微信存储目录：%s\n" % g_wx_files_path)
			cmd_gen_sub_path_list()
	else:
		print("\n	目录不存在，请检查后重新输入！！\n")


#倒推2年的所有可能存在的日期目录
def cmd_gen_sub_year_month(sSubKey):
	nYear = int(datetime.now().strftime("%Y"))
	nMonth = int(datetime.now().strftime("%m"))
	print("\n┏━ %s" %  os.path.join(g_wx_files_path, sSubKey))
	#往前推两年，检查子目录
	for iY in range((nYear-2), nYear):
		for iM in range(1, 12+1):
			sSubPath = "%s/%04d-%02d" % (sSubKey, iY, iM)
			tmpPath = os.path.join(g_wx_files_path, sSubPath)
			if os.path.exists(tmpPath) == True :
				print("┣━ %s" %sSubPath)
				g_wx_sub_paths.append(sSubPath)
	for iM in range(1, nMonth+1):
		sSubPath = "%s/%04d-%02d" % (sSubKey, nYear, iM)
		tmpPath = os.path.join(g_wx_files_path, sSubPath)
		if os.path.exists(tmpPath) == True :
			print("┣━ %s" %sSubPath)
			g_wx_sub_paths.append(sSubPath)
	
#核实列出所有的月份子目录
def cmd_gen_sub_path_list():
	####统计当前目录下的月份目录
	# 获取当前月
	sYear = datetime.now().strftime("%Y")
	sMonth = datetime.now().strftime("%m")
	g_wx_sub_paths = []
	print("\nWeChat Path: %s\n" % g_wx_files_path)
	print("Current Date: %s-%s\n" % (sYear,sMonth) )	
	cmd_gen_sub_year_month("Image")
	cmd_gen_sub_year_month("Video")
	cmd_gen_sub_year_month("File")
	g_wx_sub_paths.sort()


#统计所有的子目录磁盘空间占用
def cmd_sum_diskspace_of(nSumFlag):	
	####统计当前目录下的月份目录
	# 获取当前月
	sYear = datetime.now().strftime("%Y")
	sMonth = datetime.now().strftime("%m")
	if g_wx_files_path == "":
		print("\n请先用 1、设定您微信所在目录. \n")
		return 
	print("开始统计磁盘占用... 比较耗时请耐心等待\n")
	
	nTotalSize = 0
	nSubSize = 0
	sFlag= ""
	for aPath in g_wx_sub_paths:
		if aPath.find("Image")==0:
			if sFlag != "Image":
				if nSubSize!=0:
					print("%s 合计占用：%s\n" % (sFlag,format_size(nSubSize)))
				nSubSize =0
				sFlag = "Image"
		if aPath.find("Video")==0:
			if sFlag != "Video":
				if nSubSize!=0:
					print("%s 合计占用：%s\n" % (sFlag,format_size(nSubSize)))
				nSubSize =0
				sFlag = "Video"
		if aPath.find("File")==0:
			if sFlag != "File":
				if nSubSize!=0:
					print("%s 合计占用：%s\n" % (sFlag,format_size(nSubSize)))
				nSubSize =0
				sFlag = "File"
		nSize = dir_size(os.path.join(g_wx_files_path, aPath))
		nTotalSize += nSize
		nSubSize += nSize
		print("%s = %s" %  (aPath, format_size(nSize)))
	print("%s 合计占用：%s\n" % (sFlag,format_size(nSubSize)))
	print("Image/Video/File 三项总合计占用：%s\n" % format_size(nTotalSize))

		

#解码特定月份的图片目录
def cmd_decode_sub_path():
	#显示可解码的Image目录
	nTotalSize = 0
	nSubSize = 0
	sSubPath = ""
	if g_wx_files_path == "":
		print("\n请先用 1、设定您微信所在目录. \n")
		return 

	while True:
		sSubPath = ""
		print("\n┏━ %s" %  os.path.join(g_wx_files_path, "Image"))
		for aPath in g_wx_sub_paths:
			if aPath.find("Image")==0:
				print("┣━ %s" %aPath)
		print("\n")
		tmpPath = input("请输入YYYY-MM格式的待解码目录名字(q)：\n")
		if tmpPath == "q" or tmpPath == "Q" : 
			return 
		if len(tmpPath) != 7 :
			print("名称错误， 请输入名称格式：YYYY-MM       (q)退出")
			continue
		tmpPath = "Image/%s" % (tmpPath)
		for aPath in g_wx_sub_paths:
			if aPath == tmpPath:
				sSubPath = tmpPath
				break
				#Done
		if sSubPath =="":
			continue
		break
	
	#找到目录啦，开始解码	
	print("准备解码目录：%s\n" % sSubPath)
	#先探测你的解密密钥
	aList=[]
	list_image_dat_files(os.path.join(g_wx_files_path, sSubPath), aList)
	print("合集dat文件%d个 \n" % len(aList))
	if (len(aList)<1):
		return
	global g_wx_dat_key
	g_wx_dat_key = 0x00
	for a in aList:
		if detect_decode_key(a) == True:
			break;
	if g_wx_dat_key == 0x00:
		print("检测解码KEY值失败\n")
		return 
	print("解码KEY值：0x%02X\n" % g_wx_dat_key)
	print("解码中...%s\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	for a in aList:
		convert_dat_files(a)
	print("\n解码完成.	[%s]	Done.\n"% datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	
	
	


		

def menu_cmd():
	os.system("cls")
	while True:
		print("\n=================电脑版-微信 图片解码工具=========================\n")
		print("	1、设定您微信的基础目录\n")
		print("	2、检查Image/Video/File 磁盘占用情况\n")
		print("	3、解码特定月份的Image文件\n")
		print("	0、退出程序(q)\n")
		print("==========================================\n")
		sInput = input("请输入操作编号：")
		if sInput == "q" or sInput == "Q" :
			flag = 0
		else:
			flag = int(sInput)
		if flag	== 0:
			exit(1)
		elif flag == 1:
			cmd_setting_wx_path()
		elif flag == 2:
			cmd_sum_diskspace_of(0)
		elif flag == 3:
			cmd_decode_sub_path()
		else:
			print("请输入正确的操作编号！！")


#
if __name__	== '__main__':
	menu_cmd()

