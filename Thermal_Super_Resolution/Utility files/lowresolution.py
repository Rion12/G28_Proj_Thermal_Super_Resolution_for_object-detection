#Preparing low resolution files
import cv2
import os
path = '/content/drive/MyDrive/Thermal_Super_Resolution/train_thermal_hr' #change this to source folder you just downloaded from drive
factor = 4
#def prepare_images(path,factor):
    #loop thru the files in a dir
for file in os.listdir(path):
        #opoen th
        img = cv2.imread(path + '/' + file)
        #find old new img dimensions
        h,w,c=img.shape
        new_height= int(h/factor)
        new_width =int(w/factor)
        #resize the image down
        img = cv2.resize(img,(new_width,new_height),interpolation =cv2.INTER_LINEAR)
        #resize the img back up
        #img=cv2.resize(img,(w,h), interpolation = cv2.INTER_LINEAR)
        #save the img
        print('saving {}'.format(path))
        cv2.imwrite('/content/drive/MyDrive/Thermal_Super_Resolution/train_thermal_lr/{}'.format(file),img) #please make folder with name train_thermal_lr #change this to destination folder 