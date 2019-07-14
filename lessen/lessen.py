import os
import random
import shutil
import pandas as pd
from joblib import Parallel, delayed

random.seed(32)

#source = "name_of_folder"
source = "pocari-cm.mp4_output_256_256_30_30_0"
max_train = 222
max_test = 153

PWD = os.getcwd()
root = os.path.join(PWD, source)
csvpath = os.path.join(root, source + ".csv")

trainf=os.path.join(root, "train")	
testf=os.path.join(root, "test")

files = os.listdir(trainf)

infocsv = pd.DataFrame(columns=['class', 'total', 'train', 'test'])
infocsv.to_csv(csvpath)

#for category in files:
def lessen(category): 
	if category.endswith('txt'):
		return
		
	if category == 'LAST':
		shutil.rmtree(os.path.join(trainf, category))
		shutil.rmtree(os.path.join(testf, category))
		return
	
	train_images = os.listdir(os.path.join(trainf, category))
	train_images = [img for img in train_images if img.endswith('.jpg')]
	total_train_num = len(train_images)
	
	test_images = os.listdir(os.path.join(testf, category))
	test_images = [img for img in test_images if img.endswith('.jpg')]
	total_test_num = len(test_images)
	
	if total_train_num >= max_train:
		del_num = total_train_num - max_train
		random_delete_list = random.sample(range(total_train_num), k=del_num)
		df_train = pd.read_csv(trainf + "/" + category + "/" + category + "_" + source + ".csv", index_col=0)
		
		for i in range(len(train_images)):
			if i in random_delete_list:
				os.remove(os.path.join(trainf, category + "/" + train_images[i]))
				df_train = df_train[~df_train['image'].str.contains(train_images[i])]
				df_train = df_train.reset_index(drop=True)
				
		df_train.to_csv(trainf + "/" + category + "/" + category + "_" + source + ".csv")
	else:
		shutil.rmtree(os.path.join(trainf, category))
		
	if total_test_num >= max_test:
		del_num = total_test_num - max_test
		random_delete_list = random.sample(range(total_test_num), k=del_num)
		df_test = pd.read_csv(testf + "/" + category + "/" + category + "_" + source + ".csv", index_col=0)
		
		for i in range(len(test_images)):
			if i in random_delete_list:
				os.remove(os.path.join(testf, category + "/" + test_images[i]))
				df_test = df_test[~df_test['image'].str.contains(test_images[i])]
				df_test = df_test.reset_index(drop=True)
				
		df_test.to_csv(testf + "/" + category + "/" + category + "_" + source + ".csv")
	else:
		shutil.rmtree(os.path.join(testf, category))

	print('category:{} finished.'.format(category))


if __name__ == '__main__':
	
	result = Parallel(n_jobs=-1)([delayed(lessen)(category) for category in files])
