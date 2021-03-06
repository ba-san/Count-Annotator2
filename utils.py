### v2 has cover/remove mask functions ###
import os, copy
import cv2, csv, glob
import linecache, shutil
import pandas as pd
import numpy as np
from tqdm import tqdm


class Annotation:
	def __init__(self, outer_circle, rectangle_thickness, circle_thickness, grid_thickness, denoise, center_white, show_count):
		self.outer_circle = outer_circle
		self.rectangle_thickness = rectangle_thickness
		self.circle_thickness = circle_thickness
		self.grid_thickness = grid_thickness
		self.denoise = denoise
		self.center_white = center_white
		self.show_count = show_count
		## initialize ##
		self.box_size = 0
		self.dis_x = self.dis_y = 0
		self.img_saved = self.img_denoised = 0
		self.min_mask_x = self.max_mask_x = self.min_mask_y = self.max_mask_y = 0
		self.mask_csv_path = ''
	
	def get_row_cnt(self, csvpath, path, croppeddir):
		df = pd.read_csv(csvpath, index_col=0)
		row_cnt = 0
		for i in range(len(df)):
			if df.loc[i, 'image'] == os.path.join(path, os.path.basename(croppeddir)):
				row_cnt+=1
		return row_cnt
	
	## https://www.geeksforgeeks.org/insert-row-at-given-position-in-pandas-dataframe/
	# Function to insert row in the dataframe. this is only for checker
	def Insert_row(self, row_number, df, row_value):
		start_upper, end_lower = 0, df.shape[0]
		start_lower, end_upper = row_number, row_number
		
		upper_half = [*range(start_upper, end_upper, 1)]
		lower_half = [*range(start_lower, end_lower, 1)]
		lower_half = [x.__add__(1) for x in lower_half]
		index_ = upper_half + lower_half
		
		df.index = index_
		df.loc[row_number] = row_value
		df = df.sort_index()
		
		return df
		
	## https://note.nkmk.me/python-opencv-hconcat-vconcat-np-tile/
	def hconcat_resize_min(self, im_list, interpolation=cv2.INTER_CUBIC):
		h_min = min(im.shape[0] for im in im_list)
		im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation) for im in im_list]
		return cv2.hconcat(im_list_resize)
		
	def inside_discriminator(self, drag, initimg, start_x, start_y, end_x, end_y, fname):
		drag = cv2.rectangle(drag, (start_x, start_y), (end_x, end_y), (0, 0, 255), thickness=self.rectangle_thickness)
		cv2.imshow(fname, drag)
		enlarged = cv2.resize(drag[start_y + 2:end_y - 1, start_x + 2: end_x - 1], (600,600))
		initenlarged = cv2.resize(initimg[start_y + 2:end_y - 1, start_x + 2: end_x - 1], (600,600))
		initenlarged = cv2.circle(initenlarged, (300, 300),  self.outer_circle, (0, 0, 255), self.circle_thickness)
		if self.center_white == True:
			initenlarged = cv2.circle(initenlarged, (300, 300), 3, (0, 0, 0), -1)
			initenlarged = cv2.circle(initenlarged, (300, 300), 1, (255, 255, 255), -1)
		rightimg = cv2.vconcat([enlarged, initenlarged])
		fullimg = self.hconcat_resize_min([drag,rightimg])
		cv2.imshow(fname, fullimg)
		
	def discriminator(self, initimg, drag, fname, height, width, image_process_check):
		global hist_ul_x, hist_ul_y, hist_br_x, hist_br_y, min_hist_x, max_hist_x, min_hist_y, max_hist_y # for hist partial
		global mask_ul_x, mask_ul_y, mask_br_x, mask_br_y # for mask
		
		## hist partial
		if image_process_check['hist_partial'] == 0:
			hist_ul_x, hist_ul_y = self.dis_x, self.dis_y
		else:
			if image_process_check['hist_partial'] == 1:
				drag = cv2.circle(drag, (hist_ul_x, hist_ul_y), 1, (255, 255, 255), 3)
				hist_br_x, hist_br_y = self.dis_x, self.dis_y
				min_hist_x, max_hist_x = min(hist_br_x, hist_ul_x), max(hist_br_x, hist_ul_x)
				min_hist_y, max_hist_y = min(hist_br_y, hist_ul_y), max(hist_br_y, hist_ul_y)
			for j in range(3):
				drag[min_hist_y:max_hist_y, min_hist_x:max_hist_x, j] = cv2.equalizeHist(drag[min_hist_y:max_hist_y, min_hist_x:max_hist_x, j])  # equalize for each channel
				
		## hist all
		if image_process_check['hist_all'] == True:
			for j in range(3):
				drag[:, :, j] = cv2.equalizeHist(drag[:, :, j])  # equalize for each channel
				
		## mask
		if image_process_check['mask'] == 0:
			mask_ul_x, mask_ul_y = self.dis_x, self.dis_y
		else:
			drag = cv2.circle(drag, (mask_ul_x, mask_ul_y), 1, (255, 255, 255), 3)
			mask_br_x, mask_br_y = self.dis_x, self.dis_y
			self.min_mask_x, self.max_mask_x = min(mask_br_x, mask_ul_x), max(mask_br_x, mask_ul_x)
			self.min_mask_y, self.max_mask_y = min(mask_br_y, mask_ul_y), max(mask_br_y, mask_ul_y)
			drag[self.min_mask_y:self.max_mask_y, self.min_mask_x:self.max_mask_x, :] = np.zeros((self.max_mask_y - self.min_mask_y, self.max_mask_x - self.min_mask_x, 3), np.uint8)
			
		df = pd.read_csv(self.mask_csv_path, index_col=0)
		for i in range(len(df)):
			recov_min_mask_x, recov_max_mask_x = df.loc[i, 'min_mask_x'], df.loc[i, 'max_mask_x']
			recov_min_mask_y, recov_max_mask_y = df.loc[i, 'min_mask_y'], df.loc[i, 'max_mask_y']
			drag[recov_min_mask_y:recov_max_mask_y, recov_min_mask_x:recov_max_mask_x, :] = np.zeros((recov_max_mask_y - recov_min_mask_y, recov_max_mask_x - recov_min_mask_x, 3), np.uint8)
			
		## make it sharp
		if image_process_check['sharp'] == True:
			#kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]], np.float32) # 8 neighbors
			kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]], np.float32) # 4 neighbors
			drag = cv2.filter2D(drag, -1, kernel)
		
		## grid
		if image_process_check['grid_binary'] == True:
			for i in range(0, drag.shape[1], 300):
				drag = cv2.line(drag,(i,0),(i,drag.shape[0]),(102,140,58),thickness=self.grid_thickness)
			for j in range(0, drag.shape[0], 300):
				drag = cv2.line(drag,(0,j),(drag.shape[1],j),(102,140,58),thickness=self.grid_thickness)
		
		drag = cv2.circle(drag, (self.dis_x, self.dis_y),  self.outer_circle, (0, 0, 255), self.circle_thickness)
		if self.center_white == True:
			drag = cv2.line(drag,(self.dis_x,0),(self.dis_x,drag.shape[0]),(0,204,255),thickness=self.grid_thickness)
			drag = cv2.line(drag,(0,self.dis_y),(drag.shape[1],self.dis_y),(0,204,255),thickness=self.grid_thickness)
			drag = cv2.circle(drag, (self.dis_x, self.dis_y), 3, (0, 0, 0), -1)
			drag = cv2.circle(drag, (self.dis_x, self.dis_y), 1, (255, 255, 255), -1)
			
		if self.dis_y-150+self.box_size <= 0 and 0 <= self.dis_x-150+self.box_size and self.dis_x+150-self.box_size <= width: #upper
			self.inside_discriminator(drag, initimg, self.dis_x-150+self.box_size, 0, self.dis_x+150-self.box_size, 300-2*self.box_size, fname)
			
		elif self.dis_x-150+self.box_size <= 0 and 0 <= self.dis_y-150+self.box_size and self.dis_y+150-self.box_size <= height: #left
			self.inside_discriminator(drag, initimg, 0, self.dis_y-150+self.box_size, 300-2*self.box_size, self.dis_y+150-self.box_size, fname)
			
		elif self.dis_y+150-self.box_size >= height and 0 <= self.dis_x-150+self.box_size and self.dis_x+150-self.box_size <= width: #bottom
			self.inside_discriminator(drag, initimg, self.dis_x-150+self.box_size, height-300+2*self.box_size, self.dis_x+150-self.box_size, height, fname)
			
		elif self.dis_x+150-self.box_size >= width and 0 <= self.dis_y-150+self.box_size and self.dis_y+150-self.box_size <= height: #right
			self.inside_discriminator(drag, initimg, width-300+2*self.box_size, self.dis_y-150+self.box_size, width, self.dis_y+150-self.box_size, fname)
			
		elif self.dis_y-150+self.box_size <= 0 and self.dis_x-150+self.box_size <= 0: #upper left
			self.inside_discriminator(drag, initimg, 0, 0, 300-2*self.box_size, 300-2*self.box_size, fname)
			
		elif self.dis_y-150+self.box_size <= 0 and self.dis_x+150-self.box_size >= width: #upper right
			self.inside_discriminator(drag, initimg, width-300+2*self.box_size, 0, width, 300-2*self.box_size, fname)
			
		elif self.dis_y+150-self.box_size >= height and self.dis_x-150+self.box_size <= 0: #bottom left
			self.inside_discriminator(drag, initimg, 0, height-300+2*self.box_size, 300-2*self.box_size, height, fname)
			
		elif self.dis_y+150-self.box_size >= height and self.dis_x+150-self.box_size >= width: #bottom right
			self.inside_discriminator(drag, initimg, width-300+2*self.box_size, height-300+2*self.box_size, width, height, fname)
			
		else:
			self.inside_discriminator(drag, initimg, self.dis_x-150+self.box_size, self.dis_y-150+self.box_size, self.dis_x+150-self.box_size, self.dis_y+150-self.box_size, fname)
			
	def dragging(self, event, x, y, flags, param):
		initimg, img, image_process_check, fname, path, x_fix = param
		height, width = img.shape[0], img.shape[1]
		
		if initimg.shape[0]>1200.0: #shape[0] is height
			self.dis_x = int(x * (initimg.shape[0]/1200.0))
			self.dis_y = int(y * (initimg.shape[0]/1200.0)) if x_fix == False else self.dis_y
		else:
			self.dis_x = x
			self.dis_y = y if x_fix == False else self.dis_y
		
		drag = copy.copy(img)
		drag = cv2.rectangle(drag, (50, 50), (width-50, height-50), (40, 61, 20), thickness=2)
		
		if event == cv2.EVENT_MOUSEMOVE:
			self.discriminator(initimg, drag, fname, height, width, image_process_check)
			
	def initial_frame_setting(self, croppeddir, fname): # only for annotation (not for checker)
		if not os.path.exists(croppeddir):
			os.makedirs(croppeddir)
			os.makedirs(croppeddir + "/LAST/")
			mask_csv = pd.DataFrame(columns=['min_mask_x', 'max_mask_x', 'min_mask_y', 'max_mask_y'])
			mask_csv.to_csv(os.path.join(croppeddir, os.path.basename(fname) + ".csv"))
			
	def read_pt(self, initimg, img, csvpath, path, croppeddir, fname, windowname):
		row_cnt = self.get_row_cnt(csvpath, path, croppeddir)
		img = copy.copy(initimg)
		df = pd.read_csv(csvpath, index_col=0)
		count = 1
		for i in range(len(df)):
			print(os.path.join(path, os.path.basename(fname)))
			if df.loc[i, 'image'] == os.path.join(path, os.path.basename(fname)):
				recov_x, recov_y = df.loc[i, 'x'], df.loc[i, 'y']
				recov_color = df.loc[i, 'color']
				recov_outer_circle = df.loc[i, 'outer_circle']
				
				if recov_color=='g': #green
					img = cv2.circle(img, (recov_x, recov_y), recov_outer_circle, (0, 255, 0), self.circle_thickness)
				elif recov_color=='b': #blue
					img = cv2.circle(img, (recov_x, recov_y), recov_outer_circle, (255, 0, 0), self.circle_thickness)
				elif recov_color=='r': #red
					img = cv2.circle(img, (recov_x, recov_y), recov_outer_circle, (0, 0, 255), self.circle_thickness)
					
				img = cv2.circle(img, (recov_x, recov_y), 1, (255, 255, 255), -1)
				if (self.show_count):
					img = cv2.putText(img, str(count), (recov_x-10,recov_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
					img = cv2.putText(img, str(count), (recov_x-10,recov_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
					count+=1
					
		return img
		
	def check_pnt(self, img, k, resume, csvcurrentimg, croppeddir, csvpath, path, annotation_checker):
		row_cnt = self.get_row_cnt(csvpath, path, croppeddir)
		lastrow = sum(1 for i in open(csvpath))
		
		if k==120: #red
			img = cv2.circle(img, (self.dis_x, self.dis_y), self.outer_circle, (0, 0, 255), self.circle_thickness)
		elif k==99: #green
			img = cv2.circle(img, (self.dis_x, self.dis_y), self.outer_circle, (0, 255, 0), self.circle_thickness)
		elif k==122: #blue
			img = cv2.circle(img, (self.dis_x, self.dis_y), self.outer_circle, (255, 0, 0), self.circle_thickness)
		
		img = cv2.circle(img, (self.dis_x, self.dis_y), 1, (255, 255, 255), -1)
		if (self.show_count):
			img = cv2.putText(img, str(row_cnt+1), (self.dis_x-10,self.dis_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
			img = cv2.putText(img, str(row_cnt+1), (self.dis_x-10,self.dis_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
		img = cv2.rectangle(img, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
		
		print('You have counted {} people in this directory.\nThis time, you have counted {} people. Press B to stop.'.format(lastrow, row_cnt+1))
		
		if not annotation_checker:
			row = 0
			df = pd.read_csv(csvpath, index_col=0)
			for i in range(len(df)):
				if df.loc[i, 'image'] == os.path.join(path, os.path.basename(croppeddir)):
					row=i
					
		df = pd.read_csv(csvpath, index_col=0)
		if k==120:
			if annotation_checker:
				series = pd.Series([croppeddir, self.dis_x, self.dis_y, 'r', self.outer_circle], index=df.columns)
			else:
				df = self.Insert_row(row+1, df, [os.path.join(path, os.path.basename(croppeddir)), self.dis_x, self.dis_y, 'r', self.outer_circle])
		elif k==99:
			if annotation_checker:
				series = pd.Series([croppeddir, self.dis_x, self.dis_y, 'g', self.outer_circle], index=df.columns)
			else:
				df = self.Insert_row(row+1, df, [os.path.join(path, os.path.basename(croppeddir)), self.dis_x, self.dis_y, 'g', self.outer_circle])
		elif k==122:
			if annotation_checker:
				series = pd.Series([croppeddir, self.dis_x, self.dis_y, 'b', self.outer_circle], index=df.columns)
			else:
				df = self.Insert_row(row+1, df, [os.path.join(path, os.path.basename(croppeddir)), self.dis_x, self.dis_y, 'b', self.outer_circle])
				
		if annotation_checker:
			df = df.append(series, ignore_index=True)  # only annotaion
		
		df.to_csv(csvpath)
		
	def delete_nearest_pt(self, initimg, csvpath, path, fname, windowname):
		dist = 999999999999
		df = pd.read_csv(csvpath, index_col=0)
		for i in range(len(df)):
			if df.loc[i, 'image'] == os.path.join(path, os.path.basename(fname)):
				cal_x, cal_y = df.loc[i, 'x'], df.loc[i, 'y']
				if dist > pow(self.dis_x - cal_x, 2) + pow(self.dis_y - cal_y, 2):
					dist = pow(self.dis_x - cal_x, 2) + pow(self.dis_y - cal_y, 2)
					lowest_i = i
		
		df = df.drop(lowest_i, axis = 0)
		df = df.reset_index(drop=True)
		df.to_csv(csvpath)
		
	def delete_nearest_mask(self):
		lowest_i = 0
		dist = 999999999999
		df = pd.read_csv(self.mask_csv_path, index_col=0)
		
		for i in range(len(df)):
			cal_x, cal_y = df.loc[i, 'min_mask_x'], df.loc[i, 'min_mask_y']
			if dist > pow(self.dis_x - cal_x, 2) + pow(self.dis_y - cal_y, 2):
				dist = pow(self.dis_x - cal_x, 2) + pow(self.dis_y - cal_y, 2)
				lowest_i = i
		
		df = df.drop(lowest_i, axis = 0)
		df = df.reset_index(drop=True)
		df.to_csv(self.mask_csv_path)
	
	def move(self, dx, dy, initimg, fname, img, image_process_check):
		self.dis_x, self.dis_y = self.dis_x+dx, self.dis_y+dy
		drag = copy.copy(img)
		drag = cv2.rectangle(drag, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
		self.discriminator(initimg, drag, fname, img.shape[0], img.shape[1], image_process_check)
	
	def pending(self, csvpath, croppeddir):
		df = pd.read_csv(csvpath, index_col=0)
		df = df.replace(croppeddir, croppeddir + "_pending")
		df.to_csv(csvpath)
		os.rename(self.mask_csv_path, self.mask_csv_path[:-4] + "_pending.csv")
		os.rename(croppeddir, croppeddir + "_pending")
		
	def minor_functions(self, k, initimg, img, move_file, image_process_check, x_fix, end, locked):
		### Doesn't matter whether locked below.
		## end annotation
		if k==98: # input 'b'
			print('Exit')
			exit()
			
		## show/remove grid
		elif k==103: #input 'g'
			image_process_check['grid_binary'] = not image_process_check['grid_binary']
			
		## make it sharp (unsharpmasking)
		elif k==116: #input 't'
			image_process_check['sharp'] = not image_process_check['sharp']
			
		## hist partial
		elif k==117: #input 'u'
			image_process_check['hist_partial'] = (image_process_check['hist_partial']+1)%3
			
		## hist all
		elif k==121: #input 'y'
			image_process_check['hist_all'] = not image_process_check['hist_all']
			
		## move position by keyboard 
		elif k==105: #input i
			self.move(0, -1, initimg, move_file, img, image_process_check)
			
		elif k==106: #input j
			self.move(-1, 0, initimg, move_file, img, image_process_check)
			
		elif k==107: #input k
			self.move(1, 0, initimg, move_file, img, image_process_check)
		
		elif k==109: #input m
			self.move(0, 1, initimg, move_file, img, image_process_check)
			
		elif k==97: #input 'a'
			self.outer_circle -= 1
			self.outer_circle = 6 if self.outer_circle == 5 else self.outer_circle
			
		elif k==115: #input 's'
			self.outer_circle += 1
			
		elif k==113: #input 'q'
			self.box_size -= 2
			
		elif k==119: #input 'w'
			self.box_size += 2 if self.box_size < 145 else self.box_size
			
		## fix x-axis
		elif k==104: #input 'h'
			x_fix = not x_fix
			
		elif k==101: # input 'e'
			self.center_white = not self.center_white
			
		## refer to original image or denoise image
		elif k==114: #input 'r'
			locked = not locked
			if locked == True: # when get locked
				self.img_saved = img
				img = initimg
				
				# Non-Local Means Denoising
				if self.denoise == True:
					if isinstance(self.img_denoised, int): # when not defined
						self.img_denoised = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21)
					img = self.img_denoised
				else:
					img = self.img_saved
					
			else: # when get unlocked
				img = self.img_saved
			
		else:
			if end == 1:
				print('Cancelled.')
				end = 0
		
		return img, image_process_check, x_fix, end, locked
