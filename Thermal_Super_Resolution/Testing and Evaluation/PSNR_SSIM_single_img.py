import numpy as np
import numpy
import cv2
import glob
import os
from scipy import misc
from skimage.measure import compare_ssim
from skimage.color import rgb2ycbcr,rgb2yuv

from skimage.measure import compare_psnr
from os import listdir
from os.path import isfile, join

def preprocess(lr, hr):
  """Preprocess lr and hr batch"""
  lr = lr / 255.0
  hr = (hr / 255.0) * 2.0 - 1.0
  return lr, hr

def luminance(image):
    # Get luminance
    lum = rgb2ycbcr(image)[:,:,0]
    # Crop off 4 border pixels
    lum = lum[4:lum.shape[0]-4, 4:lum.shape[1]-4]
    #lum = lum.astype(np.float64)
    return lum

def PSNR(gt, pred):
    #gt = gt.astype(np.float64)
    #pred = pred.astype(np.float64)
    #mse = np.mean((pred - gt)**2)
    #psnr = 10*np.log10(255*255/mse)
    #return psnr
    return compare_psnr(gt, pred, data_range=255)
    
def SSIM(gt, pred):
    ssim = compare_ssim(gt, pred, data_range=255, gaussian_weights=True)
    return ssim

#hr image path
mypath='ex_Val_hr/'
#super resoluted output path
mypath1='outputTest/'   
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
images = numpy.empty(len(onlyfiles), dtype=object)
#print(len(onlyfiles))
x=0
y=0
avg_psnr = 0
avg_ssim = 0
individual_psnr = []
individual_ssim = []
for i in range(1387,1387 + len(onlyfiles)):
  gt=mypath1+str(i+1)+'.jpg'
  pred=mypath+str(i+1)+'.jpg'

  # compare to gt
  psnr = PSNR(luminance(misc.imread(gt, mode='RGB').astype(np.uint8)), luminance(misc.imread(pred, mode='RGB').astype(np.uint8)))                                                                                                                                                                                                                                                                       -7
  ssim = SSIM(luminance(misc.imread(gt, mode='RGB').astype(np.uint8)), luminance(misc.imread(pred, mode='RGB').astype(np.uint8)))
      
  print("PSNR Value:",psnr)
  print("SSIM Value:",ssim)
  individual_psnr.append(psnr)
  individual_ssim.append(ssim)
  avg_psnr += psnr
  avg_ssim += ssim
    
#avg_psnr /= i+1 #len(pred)
#avg_ssim /= i+1 #len(pred)

print("PSNR Average value:", avg_psnr)
print("SSIM Average value:", avg_ssim)
