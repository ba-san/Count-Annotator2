#https://note.nkmk.me/python-pillow-image-resize/

import os
import glob
import pandas as pd
from PIL import Image

dirname = "pocari-cm.mp4_output_256_256_30_30_0" # set the directory name
resized = 32 # set the size here

files = glob.glob('./' + dirname + '/*/*/*.jpg')
csvfiles = glob.glob('./' + dirname + '/*/*/*.csv')
dirname_split = dirname.split('_')
ratio = float(resized)/float(dirname_split[2])

for f in files:
    img = Image.open(f)
    img_resize = img.resize((resized, resized), Image.LANCZOS)
    ftitle, fext = os.path.splitext(f)
    flist = ftitle.split("/")
    new_folder = "../resized/" + flist[1] + "_resized_" + str(resized) + "_" + str(resized) + "/" + flist[2] + "/" + flist[3] + "/"
       
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
    img_resize.save(new_folder + flist[4] + '_resized' + fext)


for csvf in csvfiles:
	df = pd.read_csv(csvf, index_col=0)
	ori_x = df.loc[:, 'x']
	df.loc[:, 'x'] = ori_x*ratio
	ori_y = df.loc[:, 'y']
	df.loc[:, 'y'] = ori_y*ratio
	
	ftitle, fext = os.path.splitext(csvf)
	flist = ftitle.split("/")
	new_folder = "../resized/" + flist[1] + "_resized_" + str(resized) + "_" + str(resized) + "/csv/" + flist[2] + "/"
	if not os.path.exists(new_folder):
		os.makedirs(new_folder)
    
	df.to_csv(new_folder + flist[4] + '_resized' + fext)
