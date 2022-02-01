# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 14:15:12 2021

@author: XPCI_BT
"""


import sys
sys.path.insert(1, r'C:\Users\XPCI_BT\Documents\GitHub\MFX_control')
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import match_template
from skimage.feature import peak_local_max
from skimage.registration import phase_cross_correlation
from scipy.interpolate import NearestNDInterpolator
import time
from scipy.signal import find_peaks
import cv2
import multiprocessing as mp
import os
import tifffile

#To average the 10 flat field images    
def FF_image(path, prefix, N_ff):
    out=tifffile.imread(path+prefix+str(0)+'.tif')
    for i in range(1,N_ff):
        file_name = path+prefix+str(i)+'.tif'
        out+=tifffile.imread(file_name)
    out=out/N_ff
    return out


##Main##
folder=r'C:\Data\21_11_04\Sensitivity_110umsph_foam_40kVp_500uA\\'
folder_out=folder+'processed\\'
try:
    out=os.mkdir(folder_out)
except OSError:
    print ("Can't create directory %s" % folder_out)


beamlet_name='ff_pre_0.tif'
#beamlet_name='sample_xpos_0.0_ypos_0.0.dat'

ff_beamlet=tifffile.imread(folder+beamlet_name)
ff_beamlet=ff_beamlet.astype(np.float32)
ff_blur = cv2.GaussianBlur(ff_beamlet,(5,5),0)

ys,_=find_peaks(np.mean(ff_blur, axis=1), distance=7);
ys=ys[1:-1]
xs,_=find_peaks(np.mean(ff_blur, axis=0), distance=7);
xs=xs[1:55]

distance_source_origin = 187 # [mm]
distance_source_detector= 866 # [mm]//
distance_origin_detector = distance_source_detector-distance_source_origin

detector_pixel_size = 0.062

N_frames=1
N_ff=10
num_dith_y=8
num_dith_x=8
tot_dith_steps=8

M_mask=5.6
M_sample=4.8
M_mask_sample=1.17
period=100e-3
sample_period=period*M_mask_sample

y_step=100e-3/num_dith_y*M_mask_sample
x_step=100e-3/num_dith_x*M_mask_sample
  
n_ap_x=54
n_ap_y=42

plt.figure(figsize=(20,20))
ind=1
for i in range(num_dith_y):
        for j in range(num_dith_x):
            sub_start_time = time.time()
            sample_name = folder+'sample_xpos_'+str(round(j*x_step, 4))+'_ypos_'+str(round(i*y_step,4))+'.tif'
            ff_start=FF_image(folder, 'ff_pre_', N_ff) #only left tile
            ff_end=FF_image(folder, 'ff_post_', N_ff)#only left tile
            sample=tifffile.imread(sample_name)
            plt.subplot(8,8,ind);plt.imshow(sample[20:30, 25:35]-ff_start[20:30, 25:35], vmin=-100, vmax=100)#;plt.colorbar()
            
            ind+=1
            print('Dith step: '+ str(i) + ' - ' + str(j)+ ', time=', time.time()-sub_start_time)