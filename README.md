# Count-Annotator2

This repository is a successor of [Count-Annotator](https://github.com/ba-san/Count-Annotator).  

You can prepare annotated images for object counting and csv file which contains each point's location.  
This can be worked on both Linux and Windows.  

From big single frame, programme will create a myriad of training data with sliding window (red boxes below).   
<img src="https://user-images.githubusercontent.com/44015510/56486649-4a7cfd00-6513-11e9-850c-fe96eddf8929.png" width="300">

You can count object like this.  
<img src="https://user-images.githubusercontent.com/44015510/56487430-253dbe00-6516-11e9-9778-5107ec43b058.jpg" width="300">

You can get annotated images for object counting and csv file which contains each point's location.
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
This data is gained from single 4K image for each row.  

Cropping setting (explained below) was width = 300, height = 300, x_gap = 30, y_gap = 30.  

## Directory transition  
<img src="https://user-images.githubusercontent.com/44015510/56487112-04c13400-6515-11e9-823e-ff84472e5774.png" width="400">  

Count-Annotator2 is useful for team annotaion also. Members can create training data using annotaion2.py and person in charge can check each data quality by checker.py.    

If you annotate by annotation2.py, directories for each frame will be created (Blue box).     
After that, person in charge can check each created data by checker.py.  The directory checked by him/her will be changed to "OO_checked" (Green box).      
Finally, you can crop only checked frames by running cropping.py. Directory's name will be changed to "OO_cropped" again (Red box).    

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
save_frame_range('./videos/pocari_cm.mp4', #input video
                 0, 10000000000, 100, # start, end, frame
                 './images/', 'pocari_cm') #output directory and output images' prefix
``` 
2. run by ``` python video2img.py```  

### annotation
1. setting path of annotation2.py
``` 
folder = "test" #input images in this directory
``` 
2.run by ``` python annotation.py```

Right button click -- counting object  
  E   -- stop annotating. **DO NOT END IT BY TYPING 'Ctrl + C' OR ANY OTHER WAYS!!**  
  D   -- delete point  
  B   -- delete latest point  
Enter -- go to next image  

### double checking
You must go through this section to crop.  
If you are annotating as a team, it is reccomended only a team leader use this script to ensure the quality.  

1. setting path of checker.py
``` 
folder = "test" #input images in this directory
``` 

2. run by ``` python checker.py```  

Right button click -- counting object  
  E   -- stop annotating. **DO NOT END IT BY TYPING 'Ctrl + C' OR ANY OTHER WAYS!!**  
  D   -- delete point  
Enter -- go to next image   

### cropping

1.set cropping image size and the interval of sliding window.  
``` 
width = 256
height = 256
x_gap = 30
y_gap = 30
``` 
In this case, cropped image size is 256px x 256px  
and interval of slidng window is 30px for both x and y.  

2.run by ``` python cropping.py```  
Programme automatically detect "OO_checked" files and crops them all at once.  

## Output
You can get both csv file and annotated images as shown on the top of this page. 

