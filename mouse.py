import os
import cv2
import copy
import glob
import numpy as np
import pandas as pd
		
def dragging(event, x, y, flags, param):
	height, width, img, fname, csvpath, path, croppeddir, csvcurrentimg, resume = param
	drag = copy.copy(img)
	drag = cv2.rectangle(drag, (50, 50), (width-50, height-50), (0, 255, 0), thickness=1)
	
	if event == cv2.EVENT_MOUSEMOVE:
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

	if event == cv2.EVENT_LBUTTONDOWN:
		with open(croppeddir + "/frame_people_count.txt") as f:
			frm_ppl_cnt = f.read()
		
		print(x, y)
		lastrow = sum(1 for i in open(csvpath))
		img = cv2.circle(img, (x, y), 5, (0, 0, 255), 2)
		img = cv2.circle(img, (x, y), 1, (0, 0, 0), -1)
		img = cv2.putText(img, str(frm_ppl_cnt), (x-10,y+20), cv2.FONT_HERSHEY_PLAIN, 1, (30,53,76), thickness=4)
		img = cv2.putText(img, str(frm_ppl_cnt), (x-10,y+20), cv2.FONT_HERSHEY_PLAIN, 1, (42,185,237), thickness=1)
		img = cv2.rectangle(img, (50, 50), (width-50, height-50), (0, 255, 0), thickness=1)
		
		print('You have counted {} people in this directory.\nThis time, you have counted {} people. Press E to stop.'.format(lastrow, frm_ppl_cnt))
		frm_ppl_cnt = int(frm_ppl_cnt)
		frm_ppl_cnt+=1
		
		with open(croppeddir + "/frame_people_count.txt", mode='w') as f:
			f.write(str(frm_ppl_cnt))
		
		df = pd.read_csv(csvpath, index_col=0)
		series = pd.Series([os.path.join(path, os.path.basename(fname)), x, y], index=df.columns)
		df = df.append(series, ignore_index=True)
		df.to_csv(csvpath)
		if resume == 1:
			LAST_item_cnt = 0
			for i in glob.glob(croppeddir + "/LAST/*"):
				LAST_item_cnt+=1
			cv2.imwrite(croppeddir + "/LAST/" + str(LAST_item_cnt) + ".jpg", img)
		else:
			cv2.imwrite(croppeddir + "/LAST/" + str(lastrow - csvcurrentimg) + ".jpg", img)

