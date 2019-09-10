# Count-Annotator2

This repository is a successor of [Count-Annotator](https://github.com/ba-san/Count-Annotator).  

You can prepare annotated images for object counting and csv file which contains each point's location.  
The programs can be worked on both Linux and Windows.  

From a big single frame, this program will create a myriad of cropped images.  
To do this, 1.input original images.  
<img src="https://user-images.githubusercontent.com/44015510/59644900-02dcbf80-91aa-11e9-8e96-0847db5d2e67.jpg" width="300">  
2.count objects.  
<img src="https://user-images.githubusercontent.com/44015510/59645630-e478c300-91ad-11e9-9406-835be1d12c07.jpg" width="300">  
3.crop images by sliding window (red boxes below).   
<img src="https://user-images.githubusercontent.com/44015510/59646557-6c60cc00-91b2-11e9-81a4-dfa8adba1004.png" width="300">  
You can get annotated images for object counting and csv file which contains each point's location. One directory for one frame.  
<img src="https://user-images.githubusercontent.com/44015510/56486513-c75ba700-6512-11e9-9ca0-ba1e890ccd2a.png" width="400">

## Workflow

video2img.py --> copy created img folder to root directory(pocari-cm.mp4) --> annotation2.py --> checker.py  
--> cropping4classification_parallel2.py --> inside output folder(pocari-cm.mp4_output), integrate_img4dataset3.py  
--> move created folder to lessen --> lessen.py --> image_resize_LANCZOS.py

## Directory transition  
<img src="https://user-images.githubusercontent.com/44015510/56487112-04c13400-6515-11e9-823e-ff84472e5774.png" width="400">  

Count-Annotator2 is useful for team annotaion also. Each member can create training data using annotaion2.py and a leader can check each data quality by checker.py.    

When you annotate data by annotation2.py, directories for each frame will be created (Blue box).     
After that, a leader can check each annotated frame by checker.py.  The name of directory checked by him/her will be changed to "OO_checked" (Green box).      
Finally, you can crop checked frames by running cropping.py exclusively. Directory's name will be changed to "OO_cropped" again (Red box). This is the final deliverable.   

## Set up
It is recommended to use Python3.7.  
1.download this repository.  
``` 
git clone https://github.com/ba-san/Count-Annotator2.git  
``` 
2.install packages.  
``` 
pip install -r requirements.txt    
``` 

## How to use
### 0. Converting videos into images
If you won't use video as input, you can skip here.  
Most of this script is owe to [this page](https://note.nkmk.me/python-opencv-video-to-still-image/).   

1. setting path and frame of video2img.py  

``` 
foldername = 'demo'
``` 
You can change interval of frames here.  
Just change the number below.  
``` 
	30, cnt, # frame interval, counting videos
``` 
2. run by ``` python video2img.py```  

### 1. Annotation
1. setting path of annotation2.py
``` 
folder = "test" #input images in this directory
``` 
2.run by ``` python annotation2.py```

X,C,V   -- count object(Red, Green, Blue respectiveley)  
&nbsp;&nbsp;&nbsp;E&nbsp;&nbsp;&nbsp;   -- stop annotation. **DO NOT END IT BY TYPING 'Ctrl + C' OR ANY OTHER WAYS!!**  
&nbsp;&nbsp;&nbsp;F&nbsp;&nbsp;&nbsp;   -- delete nearest point  
&nbsp;&nbsp;&nbsp;G&nbsp;&nbsp;&nbsp;   -- show/remove grid  
&nbsp;&nbsp;&nbsp;U&nbsp;&nbsp;&nbsp;   -- fix y-cordinate of red box  
I,J,K,N-- move pointer up, left, right, down respectively  
&nbsp;&nbsp;&nbsp;S,D  -- make circle smaller/bigger  
Enter(and Y)-- go to next image  

### 2. Double checking
You must go through this section to crop image.  
If you are annotating as a team, it is reccomended only a team leader use this script to ensure the quality.  
If you will run checker.py at different env from "OO_output" was originally created, **change images' path inside
OO.csv to match to your env!!**  (You can use path_changer.py for this purpose.)  

1. setting path of checker.py
``` 
folder = "test" #input images in this directory
``` 

2. run by ``` python checker.py```  

X,C,V   -- count object(Red, Green, Blue respectiveley)  
&nbsp;&nbsp;&nbsp;E&nbsp;&nbsp;&nbsp;   -- stop annotation. **DO NOT END IT BY TYPING 'Ctrl + C' OR ANY OTHER WAYS!!**  
&nbsp;&nbsp;&nbsp;F&nbsp;&nbsp;&nbsp;   -- delete nearest point  
&nbsp;&nbsp;&nbsp;G&nbsp;&nbsp;&nbsp;   -- show/remove grid  
&nbsp;&nbsp;&nbsp;U&nbsp;&nbsp;&nbsp;   -- fix y-cordinate of red box  
I,J,K,N-- move pointer up, left, right, down respectively  
&nbsp;&nbsp;&nbsp;S,D  -- make circle smaller/bigger  
Enter(and Y)-- go to next image (directory's name will be changed.)   

### 3. Cropping
0.check each img's path inside csv is correct.  
(You need to use path_changer.py beforehand if the cropping directory is different from annotation or double checking directory. )  

1.set cropped image size and the intervals of sliding window.  
You don't need to care thorn. Keep it to 0.  
``` 
width = 256
height = 256
x_gap = 30
y_gap = 30
thorn = 0
``` 
In this case, cropped image size is 256px x 256px  
and interval of slidng window is 30px for both x and y.  

2.run by ``` python cropping.py```  
Program will automatically detect "OO_checked" files and crops them all at once.  

#### cropping4classification.py
If you crop images by this script, you will get cropped images classified by number of containing object.  

## Output
You can get both csv file and annotated images for each frame.  

