# https://note.nkmk.me/python-opencv-video-to-still-image/

import os
import cv2
import glob

def save_frame_range(video_path, start_frame, stop_frame, step_frame,
                     dir_path, basename, ext='jpg'):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)

    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    for n in range(start_frame, stop_frame, step_frame):
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('{}_{}.{}'.format(base_path, str(n).zfill(digit), ext), frame)
            n += 1
        else:
            return
            
videoname = 'C0006'
foldername = '0413'

#save_frame_range('./survey/' + foldername + '/' + videoname + '.MP4',
#                 0, 1000000000000, 30,
#                 './' + foldername + '_image/', videoname)


# process multiple videos
files=glob.glob("/home/daisuke/Workplace/Count-Annotator2/videos/" + foldername + "/*")

for fname in files:
	vname = os.path.basename(fname)
	prefix = vname.split(".")
	print(vname)
	save_frame_range('./videos/' + foldername + '/' + vname,
	0, 1000000000000, 30,
	'./' + foldername + '_image/', prefix[0])
