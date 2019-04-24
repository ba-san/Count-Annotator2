import os
import cv2
import glob
import csv
import pandas as pd
import copy
from tqdm import tqdm
import linecache, shutil

folder = "test" #input images in this directory
PWD = os.getcwd() + "/"
files=glob.glob(PWD + folder + "/*")
path = PWD + folder + "_output"
csvpath = os.path.join(path, folder) + ".csv"

resume = 1 # 0 is new, 1 is resume
successive_new_frame = 0
LAST_item_cnt = 0


def discriminator(x, y, drag, fname, height, width):
	drag = cv2.circle(drag, (x, y),  5, (0, 0, 255), 2)
	drag = cv2.circle(drag, (x, y), 1, (0, 0, 0), -1)
	if y-150 <= 0 and 0 <= x-150 and x+150 <= width: #upper
		drag = cv2.rectangle(drag, (x-150, 0), (x+150, 300), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)		
		cv2.imshow("enlarged", cv2.resize(drag[2:299, x-148:x+149], (600,600)))
	elif x-150 <= 0 and 0 <= y-150 and y+150 <= height: #left
		drag = cv2.rectangle(drag, (0, y-150), (300, y+150), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)
		cv2.imshow("enlarged", cv2.resize(drag[y-148:y+149, 2:299], (600,600)))
	elif y+150 >= height and 0 <= x-150 and x+150 <= width: #bottom
		drag = cv2.rectangle(drag, (x-150, height-300), (x+150, height), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)
		cv2.imshow("enlarged", cv2.resize(drag[height-298:height-1, x-148:x+149], (600,600)))
	elif x+150 >= width and 0 <= y-150 and y+150 <= height: #right
		drag = cv2.rectangle(drag, (width-300, y-150), (width, y+150), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)
		cv2.imshow("enlarged", cv2.resize(drag[y-148:y+149, width-298:width-1], (600,600)))
	elif y-150 <= 0 and x-150 <= 0: #upper left
		drag = cv2.rectangle(drag, (0, 0), (300, 300), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)		
		cv2.imshow("enlarged", cv2.resize(drag[2:299, 2:299], (600,600)))
	elif y-150 <= 0 and x+150 >= width: #upper right
		drag = cv2.rectangle(drag, (width-300, 0), (width, 300), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)		
		cv2.imshow("enlarged", cv2.resize(drag[2:299, width-298:width-1], (600,600)))
	elif y+150 >= height and x-150 <= 0: #bottom left
		drag = cv2.rectangle(drag, (0, height-300), (300, height), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)		
		cv2.imshow("enlarged", cv2.resize(drag[height-298:height-1, 2:299], (600,600)))
	elif y+150 >= height and x+150 >= width: #bottom right
		drag = cv2.rectangle(drag, (width-300, height-300), (width, height), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)		
		cv2.imshow("enlarged", cv2.resize(drag[height-298:height-1, width-298:width-1], (600,600)))
	else:
		drag = cv2.rectangle(drag, (x-150,y-150), (x+150, y+150), (0, 0, 255), thickness=2)
		cv2.imshow(fname, drag)
		cv2.imshow("enlarged", cv2.resize(drag[y-148:y+149, x-148:x+149], (600,600)))
	

def dragging(event, x, y, flags, param):
	height, width, img, fname, csvpath, path, croppeddir, csvcurrentimg, resume = param
	global xi, yi
	xi = x
	yi = y
	
	drag = copy.copy(img)
	drag = cv2.rectangle(drag, (50, 50), (width-50, height-50), (0, 255, 0), thickness=1)
	
	if event == cv2.EVENT_MOUSEMOVE:
		discriminator(x, y, drag, fname, height, width)




if not os.path.exists(path):
	os.makedirs(path)
	df = pd.DataFrame(columns=['image', 'x', 'y'])
	df.to_csv(csvpath)
	resume = 0
	

for fname in files:
	frm_ppl_cnt = 1 #frame people count
	break_check=0
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
		if not os.path.exists(croppeddir):
			os.makedirs(croppeddir)
			os.makedirs(croppeddir + "/LAST/")
			with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
				f.write('1')
			crpdcsv = pd.DataFrame(columns=['image', 'x', 'y'])
			crpdcsv.to_csv(os.path.join(croppeddir, os.path.basename(fname) + ".csv"))
		cv2.imwrite(croppeddir + "/LAST/0.jpg", img)
	
	
	if break_check==0:
		fx = 0
		fy = 0
		end = 0
		
		if successive_new_frame == 1:
			if not os.path.exists(croppeddir):
				os.makedirs(croppeddir)
				os.makedirs(croppeddir + "/LAST/")
				with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
					f.write('1')
				crpdcsv = pd.DataFrame(columns=['image', 'x', 'y'])
				crpdcsv.to_csv(os.path.join(croppeddir, os.path.basename(fname) + ".csv"))
			cv2.imwrite(croppeddir + "/LAST/0.jpg", img)
			
		cv2.namedWindow(fname, cv2.WINDOW_NORMAL)	
		cv2.imshow(fname, img)	
		
		cv2.setMouseCallback(fname, dragging, [img.shape[0], img.shape[1], img, fname, csvpath, path, croppeddir, csvcurrentimg, resume])
		
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
			elif k==99: # input 'c'
				with open(croppeddir + "/frame_people_count.txt") as f:
					frm_ppl_cnt = f.read()
				
				print(xi, yi)
				lastrow = sum(1 for i in open(csvpath))
				img = cv2.circle(img, (xi, yi), 5, (0, 0, 255), 2)
				img = cv2.circle(img, (xi, yi), 1, (0, 0, 0), -1)
				img = cv2.putText(img, str(frm_ppl_cnt), (xi-10,yi+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
				img = cv2.putText(img, str(frm_ppl_cnt), (xi-10,yi+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
				img = cv2.rectangle(img, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
				
				print('You have counted {} people in this directory.\nThis time, you have counted {} people. Press E to stop.'.format(lastrow, frm_ppl_cnt))
				frm_ppl_cnt = int(frm_ppl_cnt)
				frm_ppl_cnt+=1
				
				with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
					f.write(str(frm_ppl_cnt))
				
				df = pd.read_csv(csvpath, index_col=0)
				series = pd.Series([os.path.join(path, os.path.basename(fname)), xi, yi], index=df.columns)
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
						
				csvimgcnt=0
				row = 0
				start_of_newimg_index = 0
				lowest_i = 0
				dist = 99999999999999
				df = pd.read_csv(csvpath, index_col=0)
				for i in range(len(df)):
					if df.loc[i, 'image'] == os.path.join(path, os.path.basename(fname)):
						cal_x = df.loc[i, 'x']
						cal_y = df.loc[i, 'y']
						if dist > pow(abs(xi - cal_x), 2) + pow(abs(yi - cal_y), 2):
							dist = pow(abs(xi - cal_x), 2) + pow(abs(yi - cal_y), 2)
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
						recov = cv2.circle(recov, (recov_x, recov_y),  5, (0, 0, 255), 2)
						recov = cv2.circle(recov, (recov_x, recov_y), 1, (0, 0, 0), -1)
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
					
			## move position by keyboard 
			elif k==105: #input i	
				yi=yi-1	
				drag = copy.copy(img)
				drag = cv2.rectangle(drag, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
				discriminator(xi, yi, drag, fname, img.shape[0], img.shape[1])
				
			elif k==106: #input j	
				xi=xi-1	
				drag = copy.copy(img)
				drag = cv2.rectangle(drag, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
				discriminator(xi, yi, drag, fname, img.shape[0], img.shape[1])
				
			elif k==107: #input k
				xi=xi+1	
				drag = copy.copy(img)
				drag = cv2.rectangle(drag, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
				discriminator(xi, yi, drag, fname, img.shape[0], img.shape[1])
			
			elif k==109: #input m
				yi=yi+1
				drag = copy.copy(img)
				drag = cv2.rectangle(drag, (50, 50), (img.shape[1]-50, img.shape[0]-50), (0, 255, 0), thickness=1)
				discriminator(xi, yi, drag, fname, img.shape[0], img.shape[1])
						
			else:
				if end == 1:
					print('Cancelled.')
					end = 0
					
			cv2.setMouseCallback(fname, dragging, [img.shape[0], img.shape[1], img, fname, csvpath, path, croppeddir, csvcurrentimg, resume])
	
					
		successive_new_frame = 1
		resume = 0
		cv2.destroyAllWindows()	
	
