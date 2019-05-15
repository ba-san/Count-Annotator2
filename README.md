# Count-Annotator2

This repository is a successor of [Count-Annotator](https://github.com/ba-san/Count-Annotator).  

You can prepare annotated images for object counting and csv file which contains each point's location.  
The programs can be worked on both Linux and Windows.  

From a big single frame, program will create a myriad of training data.  
To do this, images are cropped by sliding window (red boxes below).   
<img src="https://user-images.githubusercontent.com/44015510/56486649-4a7cfd00-6513-11e9-850c-fe96eddf8929.png" width="300">

You can count object like this.  
<img src="https://user-images.githubusercontent.com/44015510/56487430-253dbe00-6516-11e9-9778-5107ec43b058.jpg" width="300">

You can get annotated images for object counting and csv file which contains each point's location. One directory for one frame.  
<img src="https://user-images.githubusercontent.com/44015510/56486513-c75ba700-6512-11e9-9ca0-ba1e890ccd2a.png" width="400">

You can get good amount of training data from single frame.  
<table>
  <tr>
    <th>number of people</th>
　　<th>number of cropped images (more than one object)</th>
　　<th>number of cumulative points</th>
  </tr>
  <tr>
    <td>155</td>
    <td>4587</td>
    <td>14579</td>
  </tr>
  <tr>
    <td>117</td>
    <td>4050</td>
    <td>10240</td>
  </tr>
  <tr>
    <td>38</td>
    <td>1541</td>
    <td>3280</td>
  </tr>
</table>
This data is gained from a single 4K(3840×2160) image for each row.  

Cropping setting (explained below) was width = 300, height = 300, x_gap = 30, y_gap = 30.  

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
### making videos to images
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

### annotation
1. setting path of annotation2.py
``` 
folder = "test" #input images in this directory
``` 
2.run by ``` python annotation2.py```

   C   -- count object  
   E   -- stop annotation. **DO NOT END IT BY TYPING 'Ctrl + C' OR ANY OTHER WAYS!!**  
   F   -- delete nearest point  
   B   -- delete latest point  
I,J,K,N-- move pointer up, left, right, down respectively  
 Enter -- go to next image  

### double checking
You must go through this section to crop image.  
If you are annotating as a team, it is reccomended only a team leader use this script to ensure the quality.  
If you will run checker.py at different env from "OO_output" was originally created, **change images' path inside
OO.csv to match to your env!!**   

1. setting path of checker.py
``` 
folder = "test" #input images in this directory
``` 

2. run by ``` python checker.py```  

   C   -- count object  
   E   -- stop annotation. **DO NOT END IT BY TYPING 'Ctrl + C' OR ANY OTHER WAYS!!**  
   F   -- delete nearest point   
I,J,K,N-- move pointer up, left, right, down respectively  
 Enter -- go to next image (directory's name will be changed.)   

### cropping

1.set cropped image size and the intervals of sliding window.  
You don't need to care thorn as long as using cropping.py.  
Keep it to 0.  
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
If you set thorn above to 0, you will get good no-object data.  
Bigger this number is, the better object-contained data you'll get.  

## Output
You can get both csv file and annotated images for each frame.  

