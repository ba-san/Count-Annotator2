import os
import glob
import shutil
import random
import pandas as pd
from joblib import Parallel, delayed
from distutils.dir_util import copy_tree

suffix = "384_384_18_18_0"
ratio = 0.2

random.seed(32)
PWD = os.getcwd() + "/"
files=glob.glob(PWD + "/*")
files = [ f for f in files if f.endswith("checked_" + suffix)]

fname = os.path.basename(os.path.dirname(PWD))
datasetf = PWD + "/" + fname + "_" + suffix
total = len(files)
cnt_train = 0
cnt_test = 0
train_frame_list = []
test_frame_list = []

if not os.path.exists(datasetf):
	os.makedirs(datasetf)
	os.makedirs(datasetf + "/train")
	os.makedirs(datasetf + "/test")

random_test_list = random.sample(range(total), k=int(ratio*total))


for i in range(len(files)):
	if i in random_test_list: #test
		current_frame = '{}:test:{}'.format(cnt_test, files[i])
		print(current_frame)
		test_frame_list.append(current_frame)
		copy_tree(files[i], datasetf + "/test")
		cnt_test = cnt_test + 1
		
	else: #train
		current_frame = '{}:train:{}'.format(cnt_train, files[i])
		print(current_frame)
		train_frame_list.append(current_frame)
		copy_tree(files[i], datasetf + "/train")
		cnt_train = cnt_train + 1
		

[os.remove(delete) for delete in glob.glob(datasetf + "/train/*.txt")]
[os.remove(delete) for delete in glob.glob(datasetf + "/train/*.jpg")]
[os.remove(delete) for delete in glob.glob(datasetf + "/train/*.csv")]
[os.remove(delete) for delete in glob.glob(datasetf + "/test/*.txt")]
[os.remove(delete) for delete in glob.glob(datasetf + "/test/*.jpg")]
[os.remove(delete) for delete in glob.glob(datasetf + "/test/*.csv")]

test_file = open(datasetf + '/test/test_frame_source.txt', 'w')	
test_file.write('\n'.join(test_frame_list))
test_file.close()
train_file = open(datasetf + '/train/train_frame_source.txt', 'w')	
train_file.write('\n'.join(train_frame_list))
train_file.close()


classes = os.listdir(datasetf + "/train")

for classf in classes:
	if os.path.isfile(classf) or classf == 'LAST' or classf == 'train_frame_source.txt':
		continue
		
	PWD = datasetf + "/train/" + classf + "/"
	currentdname = os.path.basename(datasetf)
	csvfiles=glob.glob(PWD + "/*.csv")
	
	df = pd.DataFrame(columns=['image', 'x', 'y', 'num'])
	
	if os.path.exists(PWD + classf + "_" + currentdname + ".csv"):
		print('csv file already exists.')
		continue
	
	for csvfile in csvfiles:
		csvname = os.path.basename(csvfile)
		df_each = pd.read_csv(csvfile, index_col=0)
		df = df.append(df_each, ignore_index=True)
		
	df.to_csv(PWD + classf + "_" + currentdname + ".csv")
	
	for csvfile in csvfiles:
		os.remove(csvfile)
	

classes = os.listdir(datasetf + "/test")

for classf in classes:
	if os.path.isfile(classf) or classf == 'LAST' or classf == 'test_frame_source.txt':
		continue
		
	PWD = datasetf + "/test/" + classf + "/"
	currentdname = os.path.basename(datasetf)
	csvfiles=glob.glob(PWD + "/*.csv")
	
	df = pd.DataFrame(columns=['image', 'x', 'y', 'num'])
	
	if os.path.exists(PWD + classf + "_" + currentdname + ".csv"):
		print('csv file already exists.')
		continue
	
	for csvfile in csvfiles:
		csvname = os.path.basename(csvfile)
		df_each = pd.read_csv(csvfile, index_col=0)
		df = df.append(df_each, ignore_index=True)
		
	df.to_csv(PWD + classf + "_" + currentdname + ".csv")
	
	for csvfile in csvfiles:
		os.remove(csvfile)
