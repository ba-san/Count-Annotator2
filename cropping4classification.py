import os
import cv2
import glob
import csv
import pandas as pd
from tqdm import tqdm
import linecache, shutil

folder = "test" # must be "OO_output"
PWD = os.getcwd() + "/"
path = PWD + folder + "_output"
files2=glob.glob(path + "/*")
csvpath = os.path.join(path, folder) + ".csv"

total = 0
fcnt = 1
width = 512 #256
height = 512 #256
x_gap = 30
y_gap = 30
thorn = 0

print('--directories to be cropped--')

for cname in files2:
	if cname.endswith("_checked"):
		print(os.path.basename(cname))
		total+=1

print('-----------------------------')
print('-----Total:{} directories-----'.format(total))


for cname in files2:
	break_check2 = 0
	
	if not cname.endswith("_checked"):
		break_check2=1
	
	if break_check2 == 0:
		csvimgcnt=0
		row = 0
		start_of_newimg_index = 0
		df = pd.read_csv(csvpath, index_col=0)
		for pt in range(len(df)): # http://www.kisse-logs.com/2017/04/11/python-dataframe-drop/
			if df.loc[pt, 'image'] == cname[:-8]:
				csvimgcnt+=1
				row=pt
		start_of_newimg_index = row - csvimgcnt + 1

		basename = os.path.basename(cname)
		#crpimg = cv2.imread(cname + "/" + basename[:-12] + "_annotated.jpg") #this is for checking. DO NOT DELETE IT.
		crpimg = cv2.imread(cname + "/LAST/0.jpg")
		pbar = tqdm(total=int(((crpimg.shape[0]-height-100)/y_gap)*((crpimg.shape[1]-width-100)/x_gap)))
		pbar.set_description("{}: {}".format(fcnt, os.path.basename(cname)))
		fcnt+=1
		
		for i in range(50, crpimg.shape[0]-height-50, y_gap): # y
			for j in range(50, crpimg.shape[1]-width-50, x_gap): # x
				cropped=crpimg[i:i+height, j:j+width]
				df = pd.read_csv(csvpath, index_col=0)
				cnt = 0
				for pt in range(start_of_newimg_index, start_of_newimg_index+csvimgcnt, 1): # http://www.kisse-logs.com/2017/04/11/python-dataframe-drop/
					if df.loc[pt, 'image'] == cname[:-8]: #double check
						pt_x = df.loc[pt, 'x']
						pt_y = df.loc[pt, 'y']
						if j + thorn <= pt_x and pt_x <= j + width - thorn and i + thorn <= pt_y  and pt_y <= i + height - thorn:
							cnt+=1
				if not os.path.exists(cname + "/" + str(cnt) + "/"):
					os.makedirs(cname + "/" + str(cnt) + "/")
				cv2.imwrite(cname + "/" + str(cnt) + "/" + os.path.basename(cname) + "_" + str(j) + "_" + str(i) + ".jpg", cropped)
				pbar.update(1)
		pbar.close()
		os.rename(cname, cname[:-8]+"_cropped")
				
	
