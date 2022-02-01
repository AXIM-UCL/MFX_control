# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 12:57:47 2021

@author: Carlos Navarrete-Leon
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2
from scipy import ndimage


def correct_rings(image, N_lp, N_hp):
    #image=reconstruction[170,:,:]
    rows, cols=image.shape
    #N_lp=121
    
    center=cols/2
    #im_polar=cv2.linearPolar(image, (center, center), 300, cv2.WARP_POLAR_LINEAR)
    im_polar=cv2.warpPolar(image, (rows, cols), (center, center), center, cv2.WARP_POLAR_LINEAR)
    #plt.figure();plt.imshow(im_polar);plt.colorbar()
    lp_filter=ndimage.median_filter(im_polar, size=(N_lp, 1))
    
    #N_hp=25
    hp_kernel=-np.ones((1, N_hp))
    hp_kernel[0,int((N_hp-1)/2)]=N_hp-1
    hp_kernel=hp_kernel/N_hp
    
    hp_filter=cv2.filter2D(src=lp_filter, ddepth=-1, kernel=hp_kernel)
    #print(hp_kernel)
    #hp_filter=
    #iltered2=ndimage.median_filter(filtered, size=(1,31))
    #plt.figure();plt.imshow(hp_filter);plt.colorbar()
    
    polar_corrected=im_polar-hp_filter
    
    im_corrected=cv2.warpPolar(polar_corrected, (rows, cols), (center, center), center, cv2.WARP_POLAR_LINEAR + cv2. WARP_INVERSE_MAP)
    return im_corrected


# plt.figure(figsize=(13, 11));
# plt.subplot(221);plt.imshow(im_polar, vmin=0, vmax=0.35);plt.colorbar();plt.title('Original Polar Image')
# plt.subplot(222);plt.imshow(lp_filter, vmin=0, vmax=0.35);plt.colorbar();plt.title('Low pass vertical filter')
# plt.subplot(223);plt.imshow(hp_filter, vmin=0, vmax=0.35);plt.colorbar();plt.title('Low pass vertical + High pass horizontal filter')
# plt.subplot(224);plt.imshow(polar_corrected, vmin=0, vmax=0.35);plt.colorbar();plt.title('Corrected Polar Image')
# plt.figure(figsize=(10,5))
# plt.subplot(121);plt.imshow(image[240:650, 300:750], vmin=0, vmax=0.35);plt.colorbar();plt.title('Original Image')
# plt.subplot(122);plt.imshow(im_corrected[240:650, 300:750], vmin=0, vmax=0.35);plt.colorbar();plt.title('Corrected Image')
