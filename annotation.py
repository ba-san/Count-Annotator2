from utils import *

if __name__ == '__main__':
	#folder = "crowd_night_annotation" #input images in this directory
	folder = "mini" #input images in this directory
	PWD = os.getcwd() + "/" # for linux
	#PWD = os.getcwd() + "\\" # for windows
	files=glob.glob(PWD + folder + "/*")
	path = PWD + folder + "_output"
	csvpath = os.path.join(path, folder) + ".csv"
	
	resume = True # Don't change this. this is only for annotation (not for checker)
	successive_new_frame = False
	
	######  parameters  ######
	outer_circle = 10
	rectangle_thickness = 1
	circle_thickness = 1
	grid_thickness = 1
	denoise = True
	center_white = False
	show_count = False
	##########################
	
	if not os.path.exists(path): # only for annotation (not for checker)
		os.makedirs(path)
		df = pd.DataFrame(columns=['image', 'x', 'y', 'color', 'outer_circle'])
		df.to_csv(csvpath)
		resume = False
		
	for fname in files:
		exe = Annotation(outer_circle, rectangle_thickness, circle_thickness, grid_thickness, denoise, center_white, show_count)
		frm_ppl_cnt = 1 #frame people count
		break_check = locked = x_fix = False
		pending_1st_time = annotation_checker = True
		image_process_check = {'grid_binary': False, 'sharp': False, 'hist_all': False, 'hist_partial': 0, 'mask': 0}
		csvcurrentimg = sum(1 for i in open(csvpath)) - 1
		croppeddir=os.path.join(path, os.path.basename(fname))
		exe.mask_csv_path = os.path.join(croppeddir, os.path.basename(fname) + ".csv")
		
		if bool(glob.glob(croppeddir + "_pending")):
			pending_1st_time = annotation_checker = False
			croppeddir = croppeddir + "_pending"
			fname = fname + "_pending"
			exe.mask_csv_path = os.path.join(croppeddir, os.path.basename(fname) + ".csv")
		
		if resume == True: # too deep nest.
			annotation_checker = False
			if successive_new_frame == False:
				for left in glob.glob(path + '/*'):
					if os.path.basename(left) == os.path.basename(fname) and bool(glob.glob(croppeddir + "/*annotated.jpg")): # already annotated
						break_check = True
						break
					elif os.path.basename(fname) + "_cropped" == os.path.basename(left) or os.path.basename(fname) + "_checked" == os.path.basename(left):
						break_check = True
						break
				
			successive_new_frame = False
			num_of_files_in_LAST_dir = len(glob.glob(croppeddir + "/LAST/*"))
			img = cv2.imread(croppeddir + "/LAST/" + str(num_of_files_in_LAST_dir-1) + ".jpg")
		else:
			if os.path.exists(croppeddir):# already exist
				annotation_checker = False
				if ("_pending" in croppeddir) and (bool(glob.glob(croppeddir + "/*annotated.jpg"))==False): # when pending(not finished)
					pending_1st_time = False
					num_of_files_in_LAST_dir = len(glob.glob(croppeddir + "/LAST/*"))
					img = cv2.imread(croppeddir + "/LAST/" + str(num_of_files_in_LAST_dir-1) + ".jpg")
				elif (bool(glob.glob(croppeddir + "/*annotated.jpg"))==True): # finished
					break_check = True
				else: # last time, ended 'b' img
					num_of_files_in_LAST_dir = len(glob.glob(croppeddir + "/LAST/*"))
					img = cv2.imread(croppeddir + "/LAST/" + str(num_of_files_in_LAST_dir-1) + ".jpg")
			else: # new annotation image
				img = cv2.imread(fname)
				exe.initial_frame_setting(croppeddir, fname, img)
		
		if break_check==False:
			end_flag = 0
			exe.initial_frame_setting(croppeddir, fname, img) if (successive_new_frame == True and not os.path.exists(croppeddir)) else None
			initimg = cv2.imread(croppeddir + "/LAST/0.jpg")
			
			cv2.namedWindow(fname, cv2.WINDOW_NORMAL)
			cv2.imshow(fname, img)
			
			cv2.setMouseCallback(fname, exe.dragging, [initimg, img, image_process_check, fname, path, x_fix])
			
			while True:
				k = cv2.waitKey(0) # waiting input
				end_flag-=1 if end_flag > 0 else 0
				
				if locked == False:
					## check object
					if k == 99 or k==120 or k==122: # input 'z', 'x' or 'c'
						exe.check_pnt(img, k, resume, csvcurrentimg, croppeddir, csvpath, path, annotation_checker)
						
					## ask to move to the next image
					elif k==13: #enter key
						print('You are really OK to process current image and move to the next image? If yes, press \'n\'.')
						end_flag = 2
						
					## go next image
					elif k==110 and end_flag > 0: # 'n'
						end_flag = 0
						df = pd.read_csv(exe.mask_csv_path, index_col=0)
						for i in range(len(df)):
							recov_min_mask_x, recov_max_mask_x = df.loc[i, 'min_mask_x'], df.loc[i, 'max_mask_x']
							recov_min_mask_y, recov_max_mask_y = df.loc[i, 'min_mask_y'], df.loc[i, 'max_mask_y']
							img[recov_min_mask_y:recov_max_mask_y, recov_min_mask_x:recov_max_mask_x, :] = np.zeros((recov_max_mask_y - recov_min_mask_y, recov_max_mask_x - recov_min_mask_x, 3), np.uint8)
						
						if "_pending" in fname:
							cv2.imwrite(os.path.join(croppeddir, os.path.basename(fname)) + "_annotated.jpg", img) 
						else:
							cv2.imwrite(os.path.join(croppeddir, os.path.basename(fname[:-4])) + "_annotated.jpg", img)
						
						cv2.imwrite(croppeddir + "/LAST/black.jpg", img)
						break
						
					## delete nearest point
					elif k==118: #input 'v'
						try:
							img = exe.delete_nearest_pt(img, csvpath, path, fname, fname)
						except:
							pass
						
					## black mask
					elif k==100: # input 'd'
						image_process_check['mask'] = (image_process_check['mask']+1)%2
						
						if image_process_check['mask']==0:
							mask_csv = pd.read_csv(exe.mask_csv_path, index_col=0)
							series = pd.Series([exe.min_mask_x, exe.max_mask_x, exe.min_mask_y, exe.max_mask_y], index=mask_csv.columns)
							mask_csv = mask_csv.append(series, ignore_index=True)
							mask_csv.to_csv(exe.mask_csv_path)
							
					elif k==102: #input 'f'
						try:
							exe.delete_nearest_mask()
						except:
							pass
							
					elif k==112: #input 'p'
						if pending_1st_time:
							print(csvpath)
							print(croppeddir)
							exe.pending(csvpath, croppeddir)
						break
						
				img, image_process_check, x_fix, end_flag, locked = exe.minor_functions(k, initimg, img, fname, image_process_check, x_fix, end_flag, locked)
				
				cv2.setMouseCallback(fname, exe.dragging, [initimg, img, image_process_check, fname, path, x_fix])
		
			## for annotation (not for checker)
			successive_new_frame = True
			resume = False
			cv2.destroyAllWindows()
