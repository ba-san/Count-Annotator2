# Count-Annotator2

This repository is a successor of [Count-Annotator](https://github.com/ba-san/Count-Annotator).  

You can prepare annotated images for object counting and csv file which contains each point's location.  
This can be worked on both Linux and Windows.  

## Set up
It is recommended to use Python3.7.  
1.download this repository.  
``` 
git clone https://github.com/ba-san/Count-Annotator.git  
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

Right button click - counting object  
b                  - go back to the previous image  
Enter              - go to the next image  
d                  - delete point  

### double checking
You must go through this section to crop.  

1. setting path of checker.py
``` 
folder = "test" #input images in this directory
``` 

2. run by ``` python checker.py```  

Right button click - counting object  
Enter - go to the next image  
d - delete point  

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



