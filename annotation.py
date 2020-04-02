import os, copy
import cv2, csv, glob
import linecache, shutil
import pandas as pd
import numpy as np
from tqdm import tqdm

folder = "crowd_night_annotation" #input images in this directory
PWD = os.getcwd() + "/"
files=glob.glob(PWD + folder + "/*")
path = PWD + folder + "_output"
csvpath = os.path.join(path, folder) + ".csv"

global dis_x, dis_y, outer_circle, box_size, center_white
resume = 1 # 0 is new, 1 is resume. Don't change this number. this is only for annotation (not for checker)
successive_new_frame = LAST_item_cnt = 0
dis_x = dis_y = box_size = 0

## parameters ##
outer_circle = 10
rectangle_thickness = 2
circle_thickness = 2
grid_thickness = 2
denoise = True
center_white = True
show_count = False

## https://note.nkmk.me/python-opencv-hconcat-vconcat-np-tile/
def hconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = min(im.shape[0] for im in im_list)
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation) for im in im_list]
    return cv2.hconcat(im_list_resize)

def inside_discriminator(drag, initimg, start_x, start_y, end_x, end_y, fname):
	drag = cv2.rectangle(drag, (start_x, start_y), (end_x, end_y), (0, 0, 255), thickness=rectangle_thickness)
	cv2.imshow(fname, drag)
	enlarged = cv2.resize(drag[start_y + 2:end_y - 1, start_x + 2: end_x - 1], (600,600))
	initenlarged = cv2.resize(initimg[start_y + 2:end_y - 1, start_x + 2: end_x - 1], (600,600))
	initenlarged = cv2.circle(initenlarged, (300, 300),  outer_circle, (0, 0, 255), circle_thickness)
	if center_white == True:
		initenlarged = cv2.circle(initenlarged, (300, 300), 1, (255, 255, 255), -1)
	rightimg = cv2.vconcat([enlarged, initenlarged])
	fullimg = hconcat_resize_min([drag,rightimg])
	cv2.imshow(fname, fullimg)

def discriminator(initimg, dis_x, dis_y, drag, fname, height, width, image_process_check):
	## hist
	global hist_ul_x, hist_ul_y, hist_br_x, hist_br_y, min_hist_x, max_hist_x, min_hist_y, max_hist_y
	if image_process_check['hist'] == 0:
		hist_ul_x, hist_ul_y = dis_x, dis_y
	else:
		if image_process_check['hist'] == 1:
			drag = cv2.circle(drag, (hist_ul_x, hist_ul_y), 1, (255, 255, 255), 3)
			hist_br_x, hist_br_y = dis_x, dis_y
			min_hist_x, max_hist_x = min(hist_br_x, hist_ul_x), max(hist_br_x, hist_ul_x)
			min_hist_y, max_hist_y = min(hist_br_y, hist_ul_y), max(hist_br_y, hist_ul_y)
		for j in range(3):
			drag[min_hist_y:max_hist_y, min_hist_x:max_hist_x, j] = cv2.equalizeHist(drag[min_hist_y:max_hist_y, min_hist_x:max_hist_x, j])  # equalize for each channel
			
	## mask
	global mask_ul_x, mask_ul_y, mask_br_x, mask_br_y, min_mask_x, max_mask_x, min_mask_y, max_mask_y, mask_csv_path
	if image_process_check['mask'] == 0:
		mask_ul_x, mask_ul_y = dis_x, dis_y
	else:
		drag = cv2.circle(drag, (mask_ul_x, mask_ul_y), 1, (255, 255, 255), 3)
		mask_br_x, mask_br_y = dis_x, dis_y
		min_mask_x, max_mask_x = min(mask_br_x, mask_ul_x), max(mask_br_x, mask_ul_x)
		min_mask_y, max_mask_y = min(mask_br_y, mask_ul_y), max(mask_br_y, mask_ul_y)
		drag[min_mask_y:max_mask_y, min_mask_x:max_mask_x, :] = np.zeros((max_mask_y - min_mask_y, max_mask_x - min_mask_x, 3), np.uint8)
		
	df = pd.read_csv(mask_csv_path, index_col=0)
	for i in range(len(df)):
		recov_min_mask_x, recov_max_mask_x = df.loc[i, 'min_mask_x'], df.loc[i, 'max_mask_x']
		recov_min_mask_y, recov_max_mask_y = df.loc[i, 'min_mask_y'], df.loc[i, 'max_mask_y']
		drag[recov_min_mask_y:recov_max_mask_y, recov_min_mask_x:recov_max_mask_x, :] = np.zeros((recov_max_mask_y - recov_min_mask_y, recov_max_mask_x - recov_min_mask_x, 3), np.uint8)
		
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
	if center_white == True:
		drag = cv2.circle(drag, (dis_x, dis_y), 1, (255, 255, 255), -1)
	
	if dis_y-150+box_size <= 0 and 0 <= dis_x-150+box_size and dis_x+150-box_size <= width: #upper
		inside_discriminator(drag, initimg, dis_x-150+box_size, 0, dis_x+150-box_size, 300-2*box_size, fname)
		
	elif dis_x-150+box_size <= 0 and 0 <= dis_y-150+box_size and dis_y+150-box_size <= height: #left
		inside_discriminator(drag, initimg, 0, dis_y-150+box_size, 300-2*box_size, dis_y+150-box_size, fname)
		
	elif dis_y+150-box_size >= height and 0 <= dis_x-150+box_size and dis_x+150-box_size <= width: #bottom
		inside_discriminator(drag, initimg, dis_x-150+box_size, height-300+2*box_size, dis_x+150-box_size, height, fname)
		
	elif dis_x+150-box_size >= width and 0 <= dis_y-150+box_size and dis_y+150-box_size <= height: #right
		inside_discriminator(drag, initimg, width-300+2*box_size, dis_y-150+box_size, width, dis_y+150-box_size, fname)
		
	elif dis_y-150+box_size <= 0 and dis_x-150+box_size <= 0: #upper left
		inside_discriminator(drag, initimg, 0, 0, 300-2*box_size, 300-2*box_size, fname)
		
	elif dis_y-150+box_size <= 0 and dis_x+150-box_size >= width: #upper right
		inside_discriminator(drag, initimg, width-300+2*box_size, 0, width, 300-2*box_size, fname)
		
	elif dis_y+150-box_size >= height and dis_x-150+box_size <= 0: #bottom left
		inside_discriminator(drag, initimg, 0, height-300+2*box_size, 300-2*box_size, height, fname)
		
	elif dis_y+150-box_size >= height and dis_x+150-box_size >= width: #bottom right
		inside_discriminator(drag, initimg, width-300+2*box_size, height-300+2*box_size, width, height, fname)
		
	else:
		inside_discriminator(drag, initimg, dis_x-150+box_size, dis_y-150+box_size, dis_x+150-box_size, dis_y+150-box_size, fname)
	
def delete_nearest_pt(csvpath, path, fname):
	global img
	csvimgcnt = row = start_of_newimg_index = lowest_i = 0
	dist = 999999999999
	df = pd.read_csv(csvpath, index_col=0)
	for i in range(len(df)):
		if df.loc[i, 'image'] == os.path.join(path, os.path.basename(fname)):
			cal_x, cal_y = df.loc[i, 'x'], df.loc[i, 'y']
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
			recov_x, recov_y = df.loc[start_of_newimg_index+j+int(num)-2, 'x'], df.loc[start_of_newimg_index+j+int(num)-2, 'y']
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
		cv2.imwrite(croppeddir+ "/LAST/" + str(i+int(num)-1) +".jpg", recov)
	
	img = cv2.imread(croppeddir + "/LAST/" + str(csvimgcnt-1) + ".jpg")
	cv2.namedWindow(fname, cv2.WINDOW_NORMAL)
	cv2.imshow(fname, img)
	
	with open(croppeddir + "/frame_people_count.txt") as f:
		frm_ppl_cnt = f.read()
	frm_ppl_cnt = int(frm_ppl_cnt)
	with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
		f.write(str(frm_ppl_cnt-1))

def delete_nearest_mask(mask_csv_path):
	lowest_i = 0
	dist = 999999999999
	df = pd.read_csv(mask_csv_path, index_col=0)
	
	for i in range(len(df)):
		cal_x, cal_y = df.loc[i, 'min_mask_x'], df.loc[i, 'min_mask_y']
		if dist > pow(dis_x - cal_x, 2) + pow(dis_y - cal_y, 2):
			dist = pow(dis_x - cal_x, 2) + pow(dis_y - cal_y, 2)
			lowest_i = i
	
	df = df.drop(lowest_i, axis = 0)
	df = df.reset_index(drop=True)
	df.to_csv(mask_csv_path)

def move(dx, dy, img, fname, initimg):
	global dis_x, dis_y
	dis_x, dis_y = dis_x+dx, dis_y+dy
	drag = copy.copy(img)
	drag = cv2.rectangle(drag, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
	discriminator(initimg, dis_x, dis_y, drag, fname, img.shape[0], img.shape[1], image_process_check)

def dragging(event, x, y, flags, param):
	global dis_x, dis_y
	initimg, height, width, img, fname, path, x_fix = param
	
	if initimg.shape[0]>1200.0: #shape[0] is height
		dis_x = int(x * (initimg.shape[0]/1200.0))
		dis_y = int(y * (initimg.shape[0]/1200.0)) if x_fix == 1 else dis_y
	else:
		dis_x = x
		dis_y = y if x_fix == 1 else dis_y
	
	drag = copy.copy(img)
	drag = cv2.rectangle(drag, (50, 50), (width-50, height-50), (40, 61, 20), thickness=2)
	
	if event == cv2.EVENT_MOUSEMOVE:
		discriminator(initimg, dis_x, dis_y, drag, fname, height, width, image_process_check)


def initial_frame_setting(croppeddir, fname, img): # only for annotation (not for checker)
	if not os.path.exists(croppeddir):
		os.makedirs(croppeddir)
		os.makedirs(croppeddir + "/LAST/")
		with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
			f.write('1')
		mask_csv = pd.DataFrame(columns=['min_mask_x', 'max_mask_x', 'min_mask_y', 'max_mask_y'])
		mask_csv.to_csv(os.path.join(croppeddir, os.path.basename(fname) + ".csv"))
	cv2.imwrite(croppeddir + "/LAST/0.jpg", img)


if __name__ == '__main__':
	if not os.path.exists(path): # only for annotation (not for checker)
		os.makedirs(path)
		df = pd.DataFrame(columns=['image', 'x', 'y', 'color', 'outer_circle'])
		df.to_csv(csvpath)
		resume = 0
	
	for fname in files:
		frm_ppl_cnt = 1 #frame people count
		break_check = img_denoised = 0
		global image_process_check, x_fix, locked, min_mask_x, max_mask_x, min_mask_y, max_mask_y, mask_csv_path
		image_process_check = {'grid_binary': -1, 'sharp': -1, 'hist': 0, 'mask': 0}
		locked = -1
		x_fix = 1
		csvcurrentimg = sum(1 for i in open(csvpath)) - 1
		croppeddir=os.path.join(path, os.path.basename(fname))
		mask_csv_path = os.path.join(croppeddir, os.path.basename(fname) + ".csv")
		
		if resume == 1: # too deep nest.
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
			
			initial_frame_setting(croppeddir, fname, img) if successive_new_frame == 1 else None
			initimg = cv2.imread(croppeddir + "/LAST/0.jpg")
			
			cv2.namedWindow(fname, cv2.WINDOW_NORMAL)
			cv2.imshow(fname, img)
			
			cv2.setMouseCallback(fname, dragging, [initimg, img.shape[0], img.shape[1], img, fname, path, x_fix])
			
			while True:
				k = cv2.waitKey(0) # waiting input
				end-=1 if end > 0 else 0
					
				if locked == -1:
					## check object
					if k==122 or k==120 or k==99: # input 'z', 'x' or 'c'
						with open(croppeddir + "/frame_people_count.txt") as f:
							frm_ppl_cnt = f.read()
							
						print(dis_x, dis_y)
						lastrow = sum(1 for i in open(csvpath))
						
						if k==120: #red
							img = cv2.circle(img, (dis_x, dis_y), outer_circle, (0, 0, 255), circle_thickness)
						elif k==99: #green
							img = cv2.circle(img, (dis_x, dis_y), outer_circle, (0, 255, 0), circle_thickness)
						elif k==122: #blue
							img = cv2.circle(img, (dis_x, dis_y), outer_circle, (255, 0, 0), circle_thickness)
							
						img = cv2.circle(img, (dis_x, dis_y), 1, (255, 255, 255), -1)
						if (show_count):
							img = cv2.putText(img, str(frm_ppl_cnt), (dis_x-10,dis_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
							img = cv2.putText(img, str(frm_ppl_cnt), (dis_x-10,dis_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
						img = cv2.rectangle(img, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
						
						print('You have counted {} people in this directory.\nThis time, you have counted {} people. Press B to stop.'.format(lastrow, frm_ppl_cnt))
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
						print('You are really OK to process current image and move to the next image? If yes, press \'n\'.')
						end = 2
						
					## go next image
					elif k==110 and end > 0: # 'n'
						end = 0
						df = pd.read_csv(mask_csv_path, index_col=0)
						for i in range(len(df)):
							recov_min_mask_x, recov_max_mask_x = df.loc[i, 'min_mask_x'], df.loc[i, 'max_mask_x']
							recov_min_mask_y, recov_max_mask_y = df.loc[i, 'min_mask_y'], df.loc[i, 'max_mask_y']
							img[recov_min_mask_y:recov_max_mask_y, recov_min_mask_x:recov_max_mask_x, :] = np.zeros((recov_max_mask_y - recov_min_mask_y, recov_max_mask_x - recov_min_mask_x, 3), np.uint8)
							
						cv2.imwrite(croppeddir + "/LAST/black.jpg", img)
						break
						
					## delete nearest point
					elif k==102: #input 'f'
						try:
							delete_nearest_pt(csvpath, path, fname)
						except:
							pass
						
					## black mask
					elif k==118: #input 'v'
						image_process_check['mask'] = (image_process_check['mask']+1)%2
						
						if image_process_check['mask']==0:
							mask_csv = pd.read_csv(mask_csv_path, index_col=0)
							series = pd.Series([min_mask_x, max_mask_x, min_mask_y, max_mask_y], index=mask_csv.columns)
							mask_csv = mask_csv.append(series, ignore_index=True)
							mask_csv.to_csv(mask_csv_path)
							
					elif k==100: # input 'd'
						try:
							delete_nearest_mask(mask_csv_path)
						except:
							pass
							
				### Doesn't matter whether locked below.
				## end annotation
				if k==98: # input 'b'
					print('Exit')
					exit()
					
				## show/remove grid
				elif k==103: #input 'g'
					image_process_check['grid_binary'] = -image_process_check['grid_binary']
					
				## make it sharp (unsharpmasking)
				elif k==121: #input 'y'
					image_process_check['sharp'] = -image_process_check['sharp']
					
				## hist
				elif k==117: #input 'u'
					image_process_check['hist'] = (image_process_check['hist']+1)%3
					
				## move position by keyboard 
				elif k==105: #input i
					move(0, -1, img, fname, initimg)
					
				elif k==106: #input j
					move(-1, 0, img, fname, initimg)
					
				elif k==107: #input k
					move(1, 0, img, fname, initimg)
					
				elif k==109: #input m
					move(0, 1, img, fname, initimg)
					
				elif k==97: #input 'a'
					outer_circle = outer_circle - 1
					outer_circle = 1 if outer_circle == 0 else outer_circle
					
				elif k==115: #input 's'
					outer_circle = outer_circle + 1
					
				elif k==113: #input 'q'
					box_size = box_size - 2
					
				elif k==119: #input 'w'
					box_size = box_size + 2 if box_size < 145 else box_size
					
				## fix x-axis
				elif k==104: #input 'h'
					x_fix = - x_fix
					
				elif k==101: # input 'e'
					center_white = not center_white
					
				## refer to original image or denoise image
				elif k==116: #input 't'
					locked = - locked
					if locked == 1: # when get locked
						img_saved = img
						img = initimg
						
						# Non-Local Means Denoising
						if denoise == True:
							if isinstance(img_denoised, int): # when not defined
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
				
				cv2.setMouseCallback(fname, dragging, [initimg, img.shape[0], img.shape[1], img, fname, path, x_fix])
			
			## for annotation (not for checker)
			successive_new_frame = 1
			resume = 0
			cv2.destroyAllWindows()
