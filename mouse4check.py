
import os
import cv2
import copy
import glob
import numpy as np
import pandas as pd

## https://www.geeksforgeeks.org/insert-row-at-given-position-in-pandas-dataframe/
# Function to insert row in the dataframe 
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
	height, width, img, fname2, csvpath, path, csvcurrentimg, resume = param
	drag = copy.copy(img)
	
	if event == cv2.EVENT_MOUSEMOVE:
		drag = cv2.circle(drag, (x, y),  5, (0, 0, 255), 2)
		drag = cv2.circle(drag, (x, y), 1, (0, 0, 0), -1)
		if y-150 <= 0 and 0 <= x-150 and x+150 <= width: #upper
			drag = cv2.rectangle(drag, (x-150, 0), (x+150, 300), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)		
			cv2.imshow("enlarged", cv2.resize(drag[2:299, x-148:x+149], (600,600)))
		elif x-150 <= 0 and 0 <= y-150 and y+150 <= height: #left
			drag = cv2.rectangle(drag, (0, y-150), (300, y+150), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)
			cv2.imshow("enlarged", cv2.resize(drag[y-148:y+149, 2:299], (600,600)))
		elif y+150 >= height and 0 <= x-150 and x+150 <= width: #bottom
			drag = cv2.rectangle(drag, (x-150, height-300), (x+150, height), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)
			cv2.imshow("enlarged", cv2.resize(drag[height-298:height-1, x-148:x+149], (600,600)))
		elif x+150 >= width and 0 <= y-150 and y+150 <= height: #right
			drag = cv2.rectangle(drag, (width-300, y-150), (width, y+150), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)
			cv2.imshow("enlarged", cv2.resize(drag[y-148:y+149, width-298:width-1], (600,600)))
		elif y-150 <= 0 and x-150 <= 0: #upper left
			drag = cv2.rectangle(drag, (0, 0), (300, 300), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)		
			cv2.imshow("enlarged", cv2.resize(drag[2:299, 2:299], (600,600)))
		elif y-150 <= 0 and x+150 >= width: #upper right
			drag = cv2.rectangle(drag, (width-300, 0), (width, 300), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)		
			cv2.imshow("enlarged", cv2.resize(drag[2:299, width-298:width-1], (600,600)))
		elif y+150 >= height and x-150 <= 0: #bottom left
			drag = cv2.rectangle(drag, (0, height-300), (300, height), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)		
			cv2.imshow("enlarged", cv2.resize(drag[height-298:height-1, 2:299], (600,600)))
		elif y+150 >= height and x+150 >= width: #bottom right
			drag = cv2.rectangle(drag, (width-300, height-300), (width, height), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)		
			cv2.imshow("enlarged", cv2.resize(drag[height-298:height-1, width-298:width-1], (600,600)))
		else:
			drag = cv2.rectangle(drag, (x-150,y-150), (x+150, y+150), (0, 0, 255), thickness=2)
			cv2.imshow(fname2, drag)
			cv2.imshow("enlarged", cv2.resize(drag[y-148:y+149, x-148:x+149], (600,600)))

	if event == cv2.EVENT_LBUTTONDOWN:
		with open(fname2 + "/frame_people_count.txt") as f:
			frm_ppl_cnt = f.read()
		
		print(x, y)
		lastrow = sum(1 for i in open(csvpath))
		img = cv2.circle(img, (x, y), 5, (0, 0, 255), 2)
		img = cv2.circle(img, (x, y), 1, (0, 0, 0), -1)
		img = cv2.putText(img, str(frm_ppl_cnt), (x-10,y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
		img = cv2.putText(img, str(frm_ppl_cnt), (x-10,y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
		
		print('You have counted {} people in this directory.\nThis time, you have counted {} people. Press E to stop.'.format(lastrow, frm_ppl_cnt))
		frm_ppl_cnt = int(frm_ppl_cnt)
		frm_ppl_cnt+=1
		
		with open(fname2 + "/frame_people_count.txt", mode='w') as f:
			f.write(str(frm_ppl_cnt))
			

		row = 0
		df = pd.read_csv(csvpath, index_col=0)
		for i in range(len(df)):
			if df.loc[i, 'image'] == os.path.join(path, os.path.basename(fname2)):
				row=i
		
		df = pd.read_csv(csvpath, index_col=0)
		df = Insert_row(row+1, df, [os.path.join(path, os.path.basename(fname2)), x, y]) 
		df.to_csv(csvpath)
		if resume == 1:
			LAST_item_cnt = 0
			for i in glob.glob(fname2 + "/LAST/*"):
				LAST_item_cnt+=1
			cv2.imwrite(fname2 + "/LAST/" + str(LAST_item_cnt) + ".jpg", img)
		else:
			cv2.imwrite(fname2 + "/LAST/" + str(lastrow - csvcurrentimg) + ".jpg", img)

		
