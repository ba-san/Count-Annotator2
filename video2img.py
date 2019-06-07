# https://note.nkmk.me/python-opencv-video-to-still-image/

import os
import cv2
import glob
from tqdm import tqdm

PWD = os.getcwd() + "/"

def save_frame_range(video_path, step_frame, cnt,
                     dir_path, basename, ext='jpg'):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)

    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
    stop_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    pbar = tqdm(total=int((stop_frame/step_frame)))
    pbar.set_description("{}:{}".format(cnt, os.path.basename(video_path)))

    for n in range(0, stop_frame, step_frame):
		
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('{}_{}.{}'.format(base_path, str(n).zfill(digit), ext), frame)
            n += 1
        else:
            return
        
        pbar.update(1)
    pbar.close()
        
            
            
foldername = 'demo'

files=glob.glob(PWD + "videos/" + foldername + "/*")
total = 0
cnt = 1

print('--directories to be processed--')
for fname in files:
	print(os.path.basename(fname))
	total+=1
print('-----------------------------')
print('-----Total:{} directories-----'.format(total))


for fname in files:
	
	vname = os.path.basename(fname)
	prefix = vname.split(".")
	save_frame_range('./videos/' + foldername + '/' + vname, #input video
	30, cnt, # frame interval, counting videos
	'./' + foldername + '_image/' + vname, prefix[0]) #output directory and output images' prefix
	cnt+=1
