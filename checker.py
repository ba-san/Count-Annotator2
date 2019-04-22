import os
import cv2
import glob
import csv
import pandas as pd
import mouse4check
import copy
from tqdm import tqdm
import linecache, shutil

folder = "test" # must be "OO_output"
PWD = os.getcwd() + "/"
path = PWD + folder + "_output"
files2=glob.glob(path + "/*")
checkpath = PWD + folder + "_checked"
croppath = PWD + folder + "_cropped"
csvpath = os.path.join(path, folder) + ".csv"

resume = 1
LAST_item_cnt = 0


for fname2 in files2:
	frm_ppl_cnt = 1 #frame people count
	break_check=0
	csvcurrentimg = sum(1 for i in open(csvpath)) - 1
	basename = os.path.basename(fname2)

	#if not bool(glob.glob(fname2 + "/*annotated.jpg")):
		#print('continue')
		#break_check=1
		
	if basename[-8:] == "_cropped" or basename[-8:] == "_checked" or basename[-4:] == ".csv":
		break_check=1
		
	
	if break_check==0:
		fx = 0
		fy = 0
		end = 0

		LAST_item_cnt = 0
		for i in glob.glob(fname2 + "/LAST/*"):
			LAST_item_cnt+=1
		img = cv2.imread(fname2 + "/LAST/" + str(LAST_item_cnt-1) + ".jpg")			
		cv2.imshow(fname2, img)	
		cv2.setMouseCallback(fname2, mouse4check.dragging, [img.shape[0], img.shape[1], img, fname2, csvpath, path, csvcurrentimg, resume])
		
		while True:
			k = cv2.waitKey(0) # waiting input
			if end > 0:
				end-=1
					
			## ask to move to the next image	
			if k==13: #enter key
				print('You are really OK to process current image and move to the next image? If yes, press \'y\'.')
				end = 2
			
			## go next image
			elif k==121 and end > 0: # 'y'
				end = 0
				cv2.imwrite(os.path.join(fname2, os.path.basename(fname2[:-4])) + "_annotated.jpg", img) #rewrite
				os.rename(fname2, fname2 + "_checked")
				break
										
			## end annotation
			elif k==101: # input 'e'
				print('Exit')
				exit()
			
			## delete point
			elif k==100: # input 'd'
				num = input('Input the number of point you wanna delete:')			
				csvimgcnt=0
				
				row = 0
				start_of_newimg_index = 0
				df = pd.read_csv(csvpath, index_col=0)
				for i in range(len(df)):
					if df.loc[i, 'image'] == os.path.join(path, os.path.basename(fname2)):
						csvimgcnt+=1
						row=i
				start_of_newimg_index = row - csvimgcnt + 1

				df = df.drop(start_of_newimg_index+int(num) - 1, axis=0)
				df = df.reset_index(drop=True)
				df.to_csv(csvpath)		
					
				os.remove(fname2 + "/LAST/" + str(csvimgcnt) + ".jpg")
				iteration = csvimgcnt-int(num)
				
				for i in range(1, iteration+1, 1):
					recov = cv2.imread(fname2 + "/LAST/"+str(int(num)-1)+".jpg")
					df = pd.read_csv(csvpath, index_col=0)
					for j in range(1, i+1, 1):
						recov_x = df.loc[start_of_newimg_index+j+int(num)-2, 'x']	
						recov_y = df.loc[start_of_newimg_index+j+int(num)-2, 'y']					
						recov = cv2.circle(recov, (recov_x, recov_y),  5, (0, 0, 255), 2)
						recov = cv2.circle(recov, (recov_x, recov_y), 1, (0, 0, 0), -1)
						recov = cv2.putText(recov, str(j+int(num)-1), (recov_x-10,recov_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
						recov = cv2.putText(recov, str(j+int(num)-1), (recov_x-10,recov_y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)	
					cv2.imwrite(fname2+ "/LAST/" + str(i+int(num)-1) +".jpg", recov)	
					
				img = cv2.imread(fname2 + "/LAST/" + str(csvimgcnt-1) + ".jpg")
				cv2.imshow(fname2, img)
				
				with open(fname2 + "/frame_people_count.txt") as f:
					frm_ppl_cnt = f.read()
				frm_ppl_cnt = int(frm_ppl_cnt)	
				with open(fname2 + "/frame_people_count.txt", mode='w') as f:
					f.write(str(frm_ppl_cnt-1))
			
			else:
				if end == 1:
					print('Cancelled.')
					end = 0
					
			cv2.setMouseCallback(fname2, mouse4check.dragging, [img.shape[0], img.shape[1], img, fname2, csvpath, path, csvcurrentimg, resume])
	

		cv2.destroyAllWindows()	
	
