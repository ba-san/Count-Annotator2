import os
import cv2
import glob
import csv
import pandas as pd
import copy
from tqdm import tqdm
import linecache, shutil

folder = "pocari-cm.mp4" #input images in this directory
PWD = os.getcwd() + "/"
files=glob.glob(PWD + folder + "/*")
path = PWD + folder + "_output"
csvpath = os.path.join(path, folder) + ".csv"

resume = 1 # 0 is new, 1 is resume. Don't change this number.
successive_new_frame = 0
LAST_item_cnt = 0
global dis_x, dis_y, outer_circle
dis_x = 0
dis_y = 0
outer_circle = 10

## https://note.nkmk.me/python-opencv-hconcat-vconcat-np-tile/
def hconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = min(im.shape[0] for im in im_list)
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
                      for im in im_list]
    return cv2.hconcat(im_list_resize)

def inside_discriminator(drag, initimg, start_x, start_y, end_x, end_y, fname, grid_binary):
	drag = cv2.rectangle(drag, (start_x, start_y), (end_x, end_y), (0, 0, 255), thickness=2)
	
	#grid
	if grid_binary == 1:
		for i in range(0, drag.shape[1], 300):
			drag = cv2.line(drag,(i,0),(i,drag.shape[0]),(102,140,58),thickness=2)
		for j in range(0, drag.shape[0], 300):
			drag = cv2.line(drag,(0,j),(drag.shape[1],j),(102,140,58),thickness=2)
	
	cv2.imshow(fname, drag)		
	enlarged = cv2.resize(drag[start_y + 2:end_y - 1, start_x + 2: end_x - 1], (600,600))
	initenlarged = cv2.resize(initimg[start_y + 2:end_y - 1, start_x + 2: end_x - 1], (600,600))
	initenlarged = cv2.circle(initenlarged, (300, 300),  outer_circle, (0, 0, 255), 2)
	initenlarged = cv2.circle(initenlarged, (300, 300), 1, (255, 255, 255), -1)
	rightimg = cv2.vconcat([enlarged, initenlarged])
	fullimg = hconcat_resize_min([drag,rightimg])
	cv2.imshow(fname, fullimg)
	
def discriminator(initimg, dis_x, dis_y, drag, fname, height, width, grid_binary):
		
	drag = cv2.circle(drag, (dis_x, dis_y),  outer_circle, (0, 0, 255), 2)
	drag = cv2.circle(drag, (dis_x, dis_y), 1, (255, 255, 255), -1)
	
	if dis_y-150 <= 0 and 0 <= dis_x-150 and dis_x+150 <= width: #upper
		inside_discriminator(drag, initimg, dis_x-150, 0, dis_x+150, 300, fname, grid_binary)
		
	elif dis_x-150 <= 0 and 0 <= dis_y-150 and dis_y+150 <= height: #left
		inside_discriminator(drag, initimg, 0, dis_y-150, 300, dis_y+150, fname, grid_binary)
		
	elif dis_y+150 >= height and 0 <= dis_x-150 and dis_x+150 <= width: #bottom
		inside_discriminator(drag, initimg, dis_x-150, height-300, dis_x+150, height, fname, grid_binary)
		
	elif dis_x+150 >= width and 0 <= dis_y-150 and dis_y+150 <= height: #right
		inside_discriminator(drag, initimg, width-300, dis_y-150, width, dis_y+150, fname, grid_binary)
		
	elif dis_y-150 <= 0 and dis_x-150 <= 0: #upper left
		inside_discriminator(drag, initimg, 0, 0, 300, 300, fname, grid_binary)
		
	elif dis_y-150 <= 0 and dis_x+150 >= width: #upper right
		inside_discriminator(drag, initimg, width-300, 0, width, 300, fname, grid_binary)
		
	elif dis_y+150 >= height and dis_x-150 <= 0: #bottom left
		inside_discriminator(drag, initimg, 0, height-300, 300, height, fname, grid_binary)
		
	elif dis_y+150 >= height and dis_x+150 >= width: #bottom right
		inside_discriminator(drag, initimg, width-300, height-300, width, height, fname, grid_binary)
		
	else:
		inside_discriminator(drag, initimg, dis_x-150, dis_y-150, dis_x+150, dis_y+150, fname, grid_binary)
		
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
		
	os.remove(croppeddir + "/LAST/" + str(csvimgcnt) + ".jpg")
	iteration = csvimgcnt-int(num)
	
	for i in range(1, iteration+1, 1):
		recov = cv2.imread(croppeddir + "/LAST/"+str(int(num)-1)+".jpg")
		df = pd.read_csv(csvpath, index_col=0)
		for j in range(1, i+1, 1):
			recov_x = df.loc[start_of_newimg_index+j+int(num)-2, 'x']
			recov_y = df.loc[start_of_newimg_index+j+int(num)-2, 'y']
			recov_color = df.loc[start_of_newimg_index+j+int(num)-2, 'color']
			recov_outer_circle = df.loc[start_of_newimg_index+j+int(num)-2, 'outer_circle']
			
			if recov_color=='g': #green
				recov = cv2.circle(recov, (recov_x, recov_y), recov_outer_circle, (0, 255, 0), 2)
			elif recov_color=='b': #blue
				recov = cv2.circle(recov, (recov_x, recov_y), recov_outer_circle, (255, 0, 0), 2)
			else: #red
				recov = cv2.circle(recov, (recov_x, recov_y), recov_outer_circle, (0, 0, 255), 2)
					
			recov = cv2.circle(recov, (recov_x, recov_y), 1, (255, 255, 255), -1)
			recov = cv2.putText(recov, str(j+int(num)-1), (recov_x-10,recov_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
			recov = cv2.putText(recov, str(j+int(num)-1), (recov_x-10,recov_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
		cv2.imwrite(croppeddir+ "/LAST/" + str(i+int(num)-1) +".jpg", recov)	
	
	img = cv2.imread(croppeddir + "/LAST/" + str(csvimgcnt-1) + ".jpg")
	cv2.namedWindow(fname, cv2.WINDOW_NORMAL)
	cv2.imshow(fname, img)
	
	with open(croppeddir + "/frame_people_count.txt") as f:
		frm_ppl_cnt = f.read()
	frm_ppl_cnt = int(frm_ppl_cnt)
	with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
		f.write(str(frm_ppl_cnt-1))

def move(dx, dy, img, fname, initimg):
	global dis_x, dis_y
	dis_x=dis_x+dx
	dis_y=dis_y+dy
	drag = copy.copy(img)
	drag = cv2.rectangle(drag, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
	discriminator(initimg, dis_x, dis_y, drag, fname, img.shape[0], img.shape[1], grid_binary)
	
def dragging(event, x, y, flags, param):
	initimg, height, width, img, fname, path, x_fix = param
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
	drag = cv2.rectangle(drag, (50, 50), (width-50, height-50), (40, 61, 20), thickness=3)
	
	if event == cv2.EVENT_MOUSEMOVE:
		discriminator(initimg, dis_x, dis_y, drag, fname, height, width, grid_binary)
		
def initial_frame_setting(croppeddir, fname, img):
	if not os.path.exists(croppeddir):
		os.makedirs(croppeddir)
		os.makedirs(croppeddir + "/LAST/")
		with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
			f.write('1')
		crpdcsv = pd.DataFrame(columns=['image', 'x', 'y', 'color', 'outer_circle'])
		crpdcsv.to_csv(os.path.join(croppeddir, os.path.basename(fname) + ".csv"))
	cv2.imwrite(croppeddir + "/LAST/0.jpg", img)
	

# main

if not os.path.exists(path):
	os.makedirs(path)
	df = pd.DataFrame(columns=['image', 'x', 'y', 'color', 'outer_circle'])
	df.to_csv(csvpath)
	resume = 0
	

for fname in files:
	frm_ppl_cnt = 1 #frame people count
	break_check=0
	global grid_binary, x_fix
	grid_binary = -1
	x_fix = 1
	csvcurrentimg = sum(1 for i in open(csvpath)) - 1
	croppeddir=os.path.join(path, os.path.basename(fname))

	if resume == 1:		
		if successive_new_frame == 0:
			for left in glob.glob(path + '/*'):
				if os.path.basename(left) == os.path.basename(fname):
					if bool(glob.glob(croppeddir + "/*annotated.jpg")):
						break_check = 1
						break
				elif os.path.basename(fname) + "_cropped" == os.path.basename(left) or os.path.basename(fname) + "_checked" == os.path.basename(left):
					break_check = 1
					break
						
		successive_new_frame = 0
		
		LAST_item_cnt = 0
		for i in glob.glob(croppeddir + "/LAST/*"):
			LAST_item_cnt+=1
		img = cv2.imread(croppeddir + "/LAST/" + str(LAST_item_cnt-1) + ".jpg")
		
	else:
		img = cv2.imread(fname)
		initial_frame_setting(croppeddir, fname, img)
	
	
	if break_check==0:
		end = 0
		
		if successive_new_frame == 1:
			initial_frame_setting(croppeddir, fname, img)
			
		initimg = cv2.imread(croppeddir + "/LAST/0.jpg")
		
		cv2.namedWindow(fname, cv2.WINDOW_NORMAL)
		cv2.imshow(fname, img)
		
		cv2.setMouseCallback(fname, dragging, [initimg, img.shape[0], img.shape[1], img, fname, path, x_fix])
		
		while True:
			k = cv2.waitKey(0) # waiting input
			if end > 0:
				end-=1
						
			## go back the previous
			if k==98: # input 'b'. See http://d.hatena.ne.jp/tosh914/20121120/1353415648
				lastrow = sum(1 for i in open(csvpath))
				LAST_item_cnt = 0
				for i in glob.glob(croppeddir + "/LAST/*"):
					LAST_item_cnt+=1
				if LAST_item_cnt == 1:
					continue
				lastrow_sen = linecache.getline(os.path.join(path, folder) + ".csv", lastrow)
				imgname = lastrow_sen.split(",")
				img = cv2.imread(croppeddir + "/LAST/" + str(LAST_item_cnt-2) + ".jpg")
				cv2.imshow(fname, img)
				
				#delete csv point
				lastrow = sum(1 for i in open(csvpath))
				df = pd.read_csv(csvpath, index_col=0)
				df = df.drop(int(lastrow - 2), axis=0)
				df.to_csv(csvpath)
				
				#delete current LAST image
				os.remove(croppeddir + "/LAST/" + str(LAST_item_cnt-1) + ".jpg")
				
				with open(croppeddir + "/frame_people_count.txt") as f:
					frm_ppl_cnt = f.read()
				frm_ppl_cnt = int(frm_ppl_cnt)
				with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
					f.write(str(frm_ppl_cnt-1))
					
			## check object
			elif k==120 or k==99 or k==118: # input 'x', 'c' or 'v'
				with open(croppeddir + "/frame_people_count.txt") as f:
					frm_ppl_cnt = f.read()
								
				print(dis_x, dis_y)
				lastrow = sum(1 for i in open(csvpath))

				if k==120: #red
					img = cv2.circle(img, (dis_x, dis_y), outer_circle, (0, 0, 255), 2)
				elif k==99: #green
					img = cv2.circle(img, (dis_x, dis_y), outer_circle, (0, 255, 0), 2)
				elif k==118: #blue
					img = cv2.circle(img, (dis_x, dis_y), outer_circle, (255, 0, 0), 2)
					
				img = cv2.circle(img, (dis_x, dis_y), 1, (255, 255, 255), -1)
				img = cv2.putText(img, str(frm_ppl_cnt), (dis_x-10,dis_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
				img = cv2.putText(img, str(frm_ppl_cnt), (dis_x-10,dis_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
				img = cv2.rectangle(img, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
				
				print('You have counted {} people in this directory.\nThis time, you have counted {} people. Press E to stop.'.format(lastrow, frm_ppl_cnt))
				frm_ppl_cnt = int(frm_ppl_cnt)
				frm_ppl_cnt+=1
				
				with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
					f.write(str(frm_ppl_cnt))
				
				df = pd.read_csv(csvpath, index_col=0)
				if k==120:
					series = pd.Series([os.path.join(path, os.path.basename(fname)), dis_x, dis_y, 'r', outer_circle], index=df.columns)
				elif k==99:
					series = pd.Series([os.path.join(path, os.path.basename(fname)), dis_x, dis_y, 'g', outer_circle], index=df.columns)
				elif k==118:
					series = pd.Series([os.path.join(path, os.path.basename(fname)), dis_x, dis_y, 'b', outer_circle], index=df.columns)
				df = df.append(series, ignore_index=True)
				df.to_csv(csvpath)
				if resume == 1:
					LAST_item_cnt = 0
					for i in glob.glob(croppeddir + "/LAST/*"):
						LAST_item_cnt+=1
					cv2.imwrite(croppeddir + "/LAST/" + str(LAST_item_cnt) + ".jpg", img)
				else:
					cv2.imwrite(croppeddir + "/LAST/" + str(lastrow - csvcurrentimg) + ".jpg", img)
					
			## ask to move to the next image
			elif k==13: #enter key
				print('You are really OK to process current image and move to the next image? If yes, press \'y\'.')
				end = 2
			
			## go next image
			elif k==121 and end > 0: # 'y'
				end = 0
				cv2.imwrite(os.path.join(croppeddir, os.path.basename(fname[:-4])) + "_annotated.jpg", img)
				break
										
			## end annotation
			elif k==101: # input 'e'
				print('Exit')
				exit()
	
			## delete nearest point
			elif k==102: #input 'f'
				delete_nearest_pt(csvpath, path, fname)
				
			## show/remove grid
			elif k==103: #input 'g'
				grid_binary = -grid_binary
					
			## move position by keyboard 
			elif k==105: #input i
				move(0, -1, img, fname, initimg)
				
			elif k==106: #input j
				move(-1, 0, img, fname, initimg)
				
			elif k==107: #input k
				move(1, 0, img, fname, initimg)
			
			elif k==109: #input m
				move(0, 1, img, fname, initimg)	
				
			elif k==117: #input 'u'
				x_fix = -x_fix
				
			elif k==114: #input 'r'
				print('Enter new outer_circle:')
				new_outer_circle = input()
				outer_circle = int(new_outer_circle)
			
			elif k==115: #input 's'
				outer_circle = outer_circle - 1
				if outer_circle == 0:
					outer_circle = 1
			
			elif k==100: #input 'd'
				outer_circle = outer_circle + 1
				
			else:
				if end == 1:
					print('Cancelled.')
					end = 0
					
			cv2.setMouseCallback(fname, dragging, [initimg, img.shape[0], img.shape[1], img, fname, path, x_fix])
	
					
		successive_new_frame = 1
		resume = 0
		cv2.destroyAllWindows()
