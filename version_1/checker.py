import os
import cv2
import glob
import csv
import pandas as pd
import numpy as np
import copy
from tqdm import tqdm
import linecache, shutil

folder = "crowd_night_annotation" # must be "OO_output"
PWD = os.getcwd() + "/"
path = PWD + folder + "_output"
files2=glob.glob(path + "/*")
checkpath = PWD + folder + "_checked"
croppath = PWD + folder + "_cropped"
csvpath = os.path.join(path, folder) + ".csv"

successive_new_frame = 0
LAST_item_cnt = 0
global dis_x, dis_y, outer_circle
dis_x = 0
dis_y = 0
outer_circle = 10
rectangle_thickness = 2
circle_thickness = 2
grid_thickness = 2
denoise = True
show_count =False

## https://note.nkmk.me/python-opencv-hconcat-vconcat-np-tile/
def hconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = min(im.shape[0] for im in im_list)
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
                      for im in im_list]
    return cv2.hconcat(im_list_resize)

def inside_discriminator(drag, initimg, start_x, start_y, end_x, end_y, fname):
	drag = cv2.rectangle(drag, (start_x, start_y), (end_x, end_y), (0, 0, 255), thickness=rectangle_thickness)
	
	cv2.imshow(fname, drag)
	enlarged = cv2.resize(drag[start_y + 2:end_y - 1, start_x + 2: end_x - 1], (600,600))
	initenlarged = cv2.resize(initimg[start_y + 2:end_y - 1, start_x + 2: end_x - 1], (600,600))
	initenlarged = cv2.circle(initenlarged, (300, 300),  outer_circle, (0, 0, 255), circle_thickness)
	initenlarged = cv2.circle(initenlarged, (300, 300), 1, (255, 255, 255), -1)
	rightimg = cv2.vconcat([enlarged, initenlarged])
	fullimg = hconcat_resize_min([drag,rightimg])
	cv2.imshow(fname, fullimg)
	
def discriminator(initimg, dis_x, dis_y, drag, fname, height, width, image_process_check):
	## hist
	if image_process_check['hist'] == 1:
		for j in range(3):
			drag[:, :, j] = cv2.equalizeHist(drag[:, :, j])  # equalize for each channel
		drag = cv2.cvtColor(drag, cv2.COLOR_BGR2RGB) # for general equilization
	
	## make it sharp
	if image_process_check['sharp'] == 1:
		#kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]], np.float32) # 8 neighbors
		kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]], np.float32) # 4 neighbors
		drag = cv2.filter2D(drag, -1, kernel)
	
	## grid
	if image_process_check['grid_binary'] == 1:
		for i in range(0, drag.shape[1], 300):
			drag = cv2.line(drag,(i,0),(i,drag.shape[0]),(102,140,58),thickness=grid_thickness)
		for j in range(0, drag.shape[0], 300):
			drag = cv2.line(drag,(0,j),(drag.shape[1],j),(102,140,58),thickness=grid_thickness)
	
	drag = cv2.circle(drag, (dis_x, dis_y),  outer_circle, (0, 0, 255), circle_thickness)
	drag = cv2.circle(drag, (dis_x, dis_y), 1, (255, 255, 255), -1)
	
	if dis_y-150 <= 0 and 0 <= dis_x-150 and dis_x+150 <= width: #upper
		inside_discriminator(drag, initimg, dis_x-150, 0, dis_x+150, 300, fname)
		
	elif dis_x-150 <= 0 and 0 <= dis_y-150 and dis_y+150 <= height: #left
		inside_discriminator(drag, initimg, 0, dis_y-150, 300, dis_y+150, fname)
		
	elif dis_y+150 >= height and 0 <= dis_x-150 and dis_x+150 <= width: #bottom
		inside_discriminator(drag, initimg, dis_x-150, height-300, dis_x+150, height, fname)
		
	elif dis_x+150 >= width and 0 <= dis_y-150 and dis_y+150 <= height: #right
		inside_discriminator(drag, initimg, width-300, dis_y-150, width, dis_y+150, fname)
		
	elif dis_y-150 <= 0 and dis_x-150 <= 0: #upper left
		inside_discriminator(drag, initimg, 0, 0, 300, 300, fname)
		
	elif dis_y-150 <= 0 and dis_x+150 >= width: #upper right
		inside_discriminator(drag, initimg, width-300, 0, width, 300, fname)
		
	elif dis_y+150 >= height and dis_x-150 <= 0: #bottom left
		inside_discriminator(drag, initimg, 0, height-300, 300, height, fname)
		
	elif dis_y+150 >= height and dis_x+150 >= width: #bottom right
		inside_discriminator(drag, initimg, width-300, height-300, width, height, fname)
		
	else:
		inside_discriminator(drag, initimg, dis_x-150, dis_y-150, dis_x+150, dis_y+150, fname)
	
def delete_nearest_pt(csvpath, path, fname):
	global img
	csvimgcnt=0
	row = 0
	start_of_newimg_index = 0
	lowest_i = 0
	dist = 999999999999
	df = pd.read_csv(csvpath, index_col=0)
	for i in range(len(df)):
		if df.loc[i, 'image'] == os.path.join(path, os.path.basename(fname)):
			cal_x = df.loc[i, 'x']
			cal_y = df.loc[i, 'y']
			if dist > pow(dis_x - cal_x, 2) + pow(dis_y - cal_y, 2):
				dist = pow(dis_x - cal_x, 2) + pow(dis_y - cal_y, 2)
				lowest_i = i
			csvimgcnt+=1
			row=i
	
	start_of_newimg_index = row - csvimgcnt + 1
	num = lowest_i + 1 - start_of_newimg_index
	df = df.drop(lowest_i, axis = 0)
	df = df.reset_index(drop=True)
	df.to_csv(csvpath)
	
	os.remove(fname2 + "/LAST/" + str(csvimgcnt) + ".jpg")
	iteration = csvimgcnt-int(num)
	
	for i in range(1, iteration+1, 1): #this two loops should be one. future work
		recov = cv2.imread(fname2 + "/LAST/"+str(int(num)-1)+".jpg")
		df = pd.read_csv(csvpath, index_col=0)
		for j in range(1, i+1, 1):
			recov_x = df.loc[start_of_newimg_index+j+int(num)-2, 'x']
			recov_y = df.loc[start_of_newimg_index+j+int(num)-2, 'y']
			recov_color = df.loc[start_of_newimg_index+j+int(num)-2, 'color']
			recov_outer_circle = df.loc[start_of_newimg_index+j+int(num)-2, 'outer_circle']
			
			if recov_color=='g': #green
				recov = cv2.circle(recov, (recov_x, recov_y), recov_outer_circle, (0, 255, 0), circle_thickness)
			elif recov_color=='b': #blue
				recov = cv2.circle(recov, (recov_x, recov_y), recov_outer_circle, (255, 0, 0), circle_thickness)
			else: #red
				recov = cv2.circle(recov, (recov_x, recov_y), recov_outer_circle, (0, 0, 255), circle_thickness)
				
			recov = cv2.circle(recov, (recov_x, recov_y), 1, (255, 255, 255), -1)
			if (show_count):
				recov = cv2.putText(recov, str(j+int(num)-1), (recov_x-10,recov_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
				recov = cv2.putText(recov, str(j+int(num)-1), (recov_x-10,recov_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
		cv2.imwrite(fname2+ "/LAST/" + str(i+int(num)-1) +".jpg", recov)
	
	img = cv2.imread(fname2 + "/LAST/" + str(csvimgcnt-1) + ".jpg")
	cv2.namedWindow(fname, cv2.WINDOW_NORMAL)
	cv2.imshow(fname, img)
	
	with open(fname2 + "/frame_people_count.txt") as f:
		frm_ppl_cnt = f.read()
	frm_ppl_cnt = int(frm_ppl_cnt)
	with open(fname2 + "/frame_people_count.txt", mode='w') as f:
		f.write(str(frm_ppl_cnt-1))

def move(dx, dy, img, fname, initimg):
	global dis_x, dis_y
	dis_x=dis_x+dx
	dis_y=dis_y+dy
	drag = copy.copy(img)
	drag = cv2.rectangle(drag, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
	discriminator(initimg, dis_x, dis_y, drag, fname, img.shape[0], img.shape[1], image_process_check)

## https://www.geeksforgeeks.org/insert-row-at-given-position-in-pandas-dataframe/
# Function to insert row in the dataframe. this is only for checker
def Insert_row(row_number, df, row_value): 

    start_upper = 0
    end_upper = row_number 
    start_lower = row_number 
    end_lower = df.shape[0] 
   
    upper_half = [*range(start_upper, end_upper, 1)] 
    lower_half = [*range(start_lower, end_lower, 1)] 
    lower_half = [x.__add__(1) for x in lower_half] 
    index_ = upper_half + lower_half 
    
    df.index = index_ 
    df.loc[row_number] = row_value 
    df = df.sort_index() 
   
    return df 
   

def dragging(event, x, y, flags, param):
	initimg, height, width, img, fname2, path, x_fix = param
	global dis_x, dis_y
	
	if initimg.shape[0]>1200.0: #shape[0] is height
		dis_x = int(x * (initimg.shape[0]/1200.0))
		if x_fix == 1:
			dis_y = int(y * (initimg.shape[0]/1200.0))
	else:
		dis_x = x
		if x_fix == 1:
			dis_y = y
	
	drag = copy.copy(img)
	drag = cv2.rectangle(drag, (50, 50), (width-50, height-50), (40, 61, 20), thickness=2)
	
	if event == cv2.EVENT_MOUSEMOVE:
		discriminator(initimg, dis_x, dis_y, drag, fname2, height, width, image_process_check)


# main

for fname2 in files2:
	frm_ppl_cnt = 1 #frame people count
	break_check=img_denoised=0
	global image_process_check, x_fix, locked
	image_process_check = {'grid_binary': -1, 'sharp': -1, 'hist': -1}
	locked = -1
	x_fix = 1
	csvcurrentimg = sum(1 for i in open(csvpath)) - 1
	basename = os.path.basename(fname2)
		
	### for checker ###
	if basename[-8:] == "_cropped" or basename[-8:] == "_checked" or basename[-4:] == ".csv":
		break_check=1

	if not bool(glob.glob(fname2 + "/*annotated.jpg")):
		break_check=1

	if break_check==0:
		end = 0
		initimg = cv2.imread(fname2 + "/LAST/0.jpg")
	###################

		LAST_item_cnt = 0
		for i in glob.glob(fname2 + "/LAST/*"):
			LAST_item_cnt+=1
		img = cv2.imread(fname2 + "/LAST/" + str(LAST_item_cnt-1) + ".jpg")
		
		cv2.namedWindow(fname2, cv2.WINDOW_NORMAL)
		cv2.imshow(fname2, img)
		
		cv2.setMouseCallback(fname2, dragging, [initimg, img.shape[0], img.shape[1], img, fname2, path, x_fix])
		
		while True:
			k = cv2.waitKey(0) # waiting input
			if end > 0:
				end-=1
				
			if locked == -1:
				## go back the previous
				if k==98: # input 'b'. See http://d.hatena.ne.jp/tosh914/20121120/1353415648
					lastrow = sum(1 for i in open(csvpath))
					LAST_item_cnt = 0
					for i in glob.glob(fname2 + "/LAST/*"):
						LAST_item_cnt+=1
					if LAST_item_cnt == 1:
						continue
					lastrow_sen = linecache.getline(os.path.join(path, folder) + ".csv", lastrow)
					imgname = lastrow_sen.split(",")
					img = cv2.imread(fname2 + "/LAST/" + str(LAST_item_cnt-2) + ".jpg")
					cv2.imshow(fname, img)
					
					#delete csv point
					lastrow = sum(1 for i in open(csvpath))
					df = pd.read_csv(csvpath, index_col=0)
					df = df.drop(int(lastrow - 2), axis=0)
					df.to_csv(csvpath)
					
					#delete current LAST image
					os.remove(fname2 + "/LAST/" + str(LAST_item_cnt-1) + ".jpg")
					
					with open(fname2 + "/frame_people_count.txt") as f:
						frm_ppl_cnt = f.read()
					frm_ppl_cnt = int(frm_ppl_cnt)
					with open(fname2 + "/frame_people_count.txt", mode='w') as f:
						f.write(str(frm_ppl_cnt-1))
						
				## check object
				elif k==120 or k==99 or k==118: # input 'x', 'c' or 'v'
					with open(fname2 + "/frame_people_count.txt") as f:
						frm_ppl_cnt = f.read()
						
					print(dis_x, dis_y)
					lastrow = sum(1 for i in open(csvpath))
					
					if k==120: #red
						img = cv2.circle(img, (dis_x, dis_y), outer_circle, (0, 0, 255), circle_thickness)
					elif k==99: #green
						img = cv2.circle(img, (dis_x, dis_y), outer_circle, (0, 255, 0), circle_thickness)
					elif k==118: #blue
						img = cv2.circle(img, (dis_x, dis_y), outer_circle, (255, 0, 0), circle_thickness)
						
					img = cv2.circle(img, (dis_x, dis_y), 1, (255, 255, 255), -1)
					if (show_count):
						img = cv2.putText(img, str(frm_ppl_cnt), (dis_x-10,dis_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
						img = cv2.putText(img, str(frm_ppl_cnt), (dis_x-10,dis_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
					img = cv2.rectangle(img, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
					
					print('You have counted {} people in this directory.\nThis time, you have counted {} people. Press E to stop.'.format(lastrow, frm_ppl_cnt))
					frm_ppl_cnt = int(frm_ppl_cnt)
					frm_ppl_cnt+=1
					
					with open(fname2 + "/frame_people_count.txt", mode='w') as f:
						f.write(str(frm_ppl_cnt))
					
					### for checker ###
					row = 0
					df = pd.read_csv(csvpath, index_col=0)
					for i in range(len(df)):
						if df.loc[i, 'image'] == os.path.join(path, os.path.basename(fname2)):
							row=i
					###################
					
					df = pd.read_csv(csvpath, index_col=0)
					if k==120:
						df = Insert_row(row+1, df, [os.path.join(path, os.path.basename(fname2)), dis_x, dis_y, 'r', outer_circle])
					elif k==99:
						df = Insert_row(row+1, df, [os.path.join(path, os.path.basename(fname2)), dis_x, dis_y, 'g', outer_circle])
					elif k==118:
						df = Insert_row(row+1, df, [os.path.join(path, os.path.basename(fname2)), dis_x, dis_y, 'b', outer_circle])
					df.to_csv(csvpath)
					LAST_item_cnt = 0
					for i in glob.glob(fname2 + "/LAST/*"):
						LAST_item_cnt+=1
					cv2.imwrite(fname2 + "/LAST/" + str(LAST_item_cnt) + ".jpg", img)
						
				## ask to move to the next image
				elif k==13: #enter key
					print('You are really OK to process current image and move to the next image? If yes, press \'y\'.')
					end = 2
					
				## go next image
				elif k==121 and end > 0: # 'y'
					end = 0
					cv2.imwrite(os.path.join(fname2, os.path.basename(fname2[:-4])) + "_annotated.jpg", img) #rewrite
					os.rename(fname2, fname2 + "_checked")
					break
					
				## delete nearest point
				elif k==102: #input 'f'
					delete_nearest_pt(csvpath, path, fname2)
					
			### Doesn't matter whether locked below.
			## end annotation
			if k==101: # input 'e'
				print('Exit')
				exit()
				
			## show/remove grid
			elif k==103: #input 'g'
				image_process_check['grid_binary'] = -image_process_check['grid_binary']
				
			## make it sharp (unsharpmasking)
			elif k==114: #input 'r'
				image_process_check['sharp'] = -image_process_check['sharp']
				
			## hist
			elif k==112: #input 'p'
				image_process_check['hist'] = -image_process_check['hist']
				
			## move position by keyboard 
			elif k==105: #input i
				move(0, -1, img, fname2, initimg)
				
			elif k==106: #input j
				move(-1, 0, img, fname2, initimg)
				
			elif k==107: #input k
				move(1, 0, img, fname2, initimg)
			
			elif k==109: #input m
				move(0, 1, img, fname2, initimg)
				
			elif k==115: #input 's'
				outer_circle = outer_circle - 1
				if outer_circle == 0:
					outer_circle = 1
			
			elif k==100: #input 'd'
				outer_circle = outer_circle + 1
				
			## fix x-axis
			elif k==117: #input 'u'
				x_fix = - x_fix
				
			## refer to original image or denoise image
			elif k==116: #input 't'
				locked = - locked
				if locked == 1: # when get locked
					img_saved = img
					img = initimg
					
					# Non-Local Means Denoising
					if denoise == True:
						if isinstance(img_denoised, int): # not defined
							img_denoised = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21)
						else: # already defined
							img = img_denoised
					else:
						img = img_saved
						
						
				else: # when get unlocked
					img = img_saved
				
			else:
				if end == 1:
					print('Cancelled.')
					end = 0
			
			cv2.setMouseCallback(fname2, dragging, [initimg, img.shape[0], img.shape[1], img, fname2, path, x_fix])
	
		cv2.destroyAllWindows()
