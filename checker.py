### v2 has cover/remove mask functions ###
from utils import *

if __name__ == '__main__':
	folder = "crowd_night_annotation" # must be "OO_output"
	PWD = os.getcwd() + "/" # for linux
	#PWD = os.getcwd() + "\\" # for windows
	path = PWD + folder + "_output"
	files2=glob.glob(path + "/*")
	checkpath = PWD + folder + "_checked"
	croppath = PWD + folder + "_cropped"
	csvpath = os.path.join(path, folder) + ".csv"
	
	resume = 1 # 0 is new, 1 is resume. Don't change this number. this is only for annotation (not for checker)
	successive_new_frame = LAST_item_cnt = 0
	
	######  parameters  ######
	outer_circle = 10
	rectangle_thickness = 2
	circle_thickness = 1
	grid_thickness = 2
	denoise = True
	center_white = False
	show_count = True
	##########################
	
	
	for croppeddir in files2:
		exe = Annotation(outer_circle, rectangle_thickness, circle_thickness, grid_thickness, denoise, center_white, show_count)
		frm_ppl_cnt = 1 #frame people count
		break_check = 0
		image_process_check = {'grid_binary': -1, 'sharp': -1, 'hist_all': -1, 'hist_partial': 0, 'mask': 0}
		locked = -1
		x_fix = 1
		annotation_checker = False
		pending_1st_time = True
		csvcurrentimg = sum(1 for i in open(csvpath)) - 1
		basename = os.path.basename(croppeddir)
		
		### for checker ###
		if basename[-8:] == "_cropped" or basename[-8:] == "_checked" or basename[-4:] == ".csv":
			break_check=1
	
		if not bool(glob.glob(croppeddir + "/*annotated.jpg")):
			break_check=1
		
		if basename[-8:] == "_pending":
			pending_1st_time = False
		###################
		
		if break_check==0:
			end = 0
			initimg = cv2.imread(croppeddir + "/LAST/0.jpg")
			
			exe.mask_csv_path = os.path.join(croppeddir, os.path.basename(croppeddir) + ".csv")
			
			LAST_item_cnt = len(glob.glob(croppeddir + "/LAST/*"))-1 # different from annotation. this is for 'black.jpg'
			img = cv2.imread(croppeddir + "/LAST/" + str(LAST_item_cnt-1) + ".jpg")
			
			cv2.namedWindow(croppeddir, cv2.WINDOW_NORMAL)
			cv2.imshow(croppeddir, img)
			
			cv2.setMouseCallback(croppeddir, exe.dragging, [initimg, img, image_process_check, croppeddir, path, x_fix])
			
			while True:
				k = cv2.waitKey(0) # waiting input
				end-=1 if end > 0 else 0
				
				if locked == -1:
					## check object
					if k==122 or k==120 or k==99: # input 'z', 'x' or 'c'
						exe.check_pnt(img, k, 100, csvcurrentimg, croppeddir, csvpath, path, annotation_checker) # 100 is resume. no need to think about it.
						
					## ask to move to the next image
					elif k==13: #enter key
						print('You are really OK to process current image and move to the next image? If yes, press \'n\'.')
						end = 2
						
					## go next image
					elif k==110 and end > 0: # 'n'
						end = 0
						df = pd.read_csv(exe.mask_csv_path, index_col=0)
						for i in range(len(df)):
							recov_min_mask_x, recov_max_mask_x = df.loc[i, 'min_mask_x'], df.loc[i, 'max_mask_x']
							recov_min_mask_y, recov_max_mask_y = df.loc[i, 'min_mask_y'], df.loc[i, 'max_mask_y']
							img[recov_min_mask_y:recov_max_mask_y, recov_min_mask_x:recov_max_mask_x, :] = np.zeros((recov_max_mask_y - recov_min_mask_y, recov_max_mask_x - recov_min_mask_x, 3), np.uint8)
							
						cv2.imwrite(os.path.join(croppeddir, os.path.basename(croppeddir[:-4])) + "_annotated.jpg", img) #rewrite
						os.rename(croppeddir, croppeddir + "_checked")
						break
						
					## delete nearest point
					elif k==118: #input 'v'
						try:
							img = exe.delete_nearest_pt(img, csvpath, path, os.path.join(path[:-7], os.path.basename(croppeddir)), croppeddir)
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
							df = pd.read_csv(csvpath, index_col=0)
							df = df.replace(croppeddir, croppeddir + "_pending")
							df.to_csv(csvpath)
							os.rename(exe.mask_csv_path, exe.mask_csv_path[:-4] + "_pending.csv")
							os.rename(croppeddir, croppeddir + "_pending")
						break
						
				img, image_process_check, x_fix, end, locked = exe.minor_functions(k, initimg, img, croppeddir, image_process_check, x_fix, end, locked)
				
				cv2.setMouseCallback(croppeddir, exe.dragging, [initimg, img, image_process_check, croppeddir, path, x_fix])
		
			cv2.destroyAllWindows()
