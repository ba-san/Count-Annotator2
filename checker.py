from utils import *

def main():
	folder = "mini" # must be "OO_output"
	PWD = os.getcwd() + "/" # for linux
	#PWD = os.getcwd() + "\\" # for windows
	path = PWD + folder + "_output"
	files2=glob.glob(path + "/*")
	checkpath = PWD + folder + "_checked"
	croppath = PWD + folder + "_cropped"
	csvpath = os.path.join(path, folder) + ".csv"
	resume = True # Don't change this. this is only for annotation
	
	######  parameters  ######
	outer_circle = 10
	rectangle_thickness = 2
	circle_thickness = 1
	grid_thickness = 2
	denoise = True
	center_white = False
	show_count = False
	##########################
	
	for croppeddir in files2:
		exe = Annotation(outer_circle, rectangle_thickness, circle_thickness, grid_thickness, denoise, center_white, show_count)
		break_check = locked = x_fix = False
		annotation_checker = False
		pending_1st_time = True
		image_process_check = {'grid_binary': False, 'sharp': False, 'hist_all': False, 'hist_partial': 0, 'mask': 0}
		csvcurrentimg = sum(1 for i in open(csvpath)) - 1
		basename = os.path.basename(croppeddir)
		
		### for checker ###
		if basename[-8:] == "_cropped" or basename[-8:] == "_checked" or basename[-4:] == ".csv":
			break_check=True
		
		if not bool(glob.glob(croppeddir + "/*annotated.jpg")):
			break_check=True
		
		if basename[-8:] == "_pending":
			pending_1st_time = False
		###################
		
		if break_check==False:
			end_flag = 0
			initimg = cv2.imread(croppeddir + "/LAST/0.jpg")
			exe.mask_csv_path = os.path.join(croppeddir, os.path.basename(croppeddir) + ".csv")
			img = initimg
			img = exe.read_pt(initimg, img, csvpath, path, croppeddir, os.path.join(path[:-7], os.path.basename(croppeddir)), croppeddir)
			
			cv2.namedWindow(croppeddir, cv2.WINDOW_NORMAL)
			cv2.imshow(croppeddir, img)
			cv2.setMouseCallback(croppeddir, exe.dragging, [initimg, img, image_process_check, croppeddir, path, x_fix])
			
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
							
						cv2.imwrite(os.path.join(croppeddir, os.path.basename(croppeddir[:-4])) + "_annotated.jpg", img) #rewrite
						os.rename(croppeddir, croppeddir + "_checked")
						break
						
					## delete nearest point
					elif k==118: #input 'v'
						try:
							exe.delete_nearest_pt(initimg, csvpath, path, os.path.join(path[:-7], os.path.basename(croppeddir)), croppeddir)
							img = exe.read_pt(initimg, img, csvpath, path, croppeddir, os.path.join(path[:-7], os.path.basename(croppeddir)), croppeddir)
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
							exe.pending(csvpath, croppeddir)
						break
						
				img, image_process_check, x_fix, end_flag, locked = exe.minor_functions(k, initimg, img, croppeddir, image_process_check, x_fix, end_flag, locked)
				
				cv2.setMouseCallback(croppeddir, exe.dragging, [initimg, img, image_process_check, croppeddir, path, x_fix])
		
			cv2.destroyAllWindows()

if __name__ == '__main__':
	main()
