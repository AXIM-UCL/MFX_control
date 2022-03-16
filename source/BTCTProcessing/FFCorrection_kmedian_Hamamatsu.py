# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 08:41:28 2022

@author: Carlos Navarrete-Leon
"""

import numpy as np 
import os
import tifffile
import statistics
import time

# Flat Field corrections. This script implements a k-median filter to correct
# for weird pixels in the RAW and FF images and then implements the flat field correction
#It is implemented for the left tile of the detector (the right one is not workint at the time)
# but it can be adapted to full detector

def k_median_filter(image, patchsize=3, k=3):
    out=np.ones(image.shape)
    bads=0
    for i in range(patchsize, 2340-patchsize):
        for j in range(patchsize, 2368-patchsize):
            window=image[i-patchsize:i+patchsize+1,j-patchsize:j+patchsize+1].ravel()
            window.astype(float)
            cent_pix=image[i,j]
            median=statistics.median(window)
            sigma=np.sqrt(np.var(window))
            if(abs(cent_pix-median)<(k*sigma)):
                out[i,j]=cent_pix
            else:
                goods=[]
                bads+=1
                for z in range(len(window)):
                    if(abs(window[z]-median)<(k*sigma)):
                        goods.append(window[z])
                if(len(goods)!=0):
                    out[i,j]=statistics.median(np.array(goods))
                else:
                    out[i,j]=cent_pix
    print('Bad pixels:', bads)
    return out
    

#To average the 10 flat field images    
def FF_image(path, prefix, N_ff):
    out=tifffile.imread(path+prefix+str(0)+'.tif')
    for i in range(1,N_ff):
        file_name = path+prefix+str(i)+'.tif'
        out+=tifffile.imread(file_name)
    out=out/N_ff
    return out
    
#Flat field correction with post k-median folder
def FlatField(img_raw, ff_start, ff_end, dark_start, dark_end, proj_no, N_proj, patchsize=2):
    weight=proj_no/N_proj
    ff_mean=(1-weight)*ff_start + weight*ff_end
    dark_mean=(1-weight)*dark_start + weight*dark_end
    ffc_raw=(img_raw-dark_mean)/(ff_mean-dark_mean)
    ffc_raw=np.nan_to_num(ffc_raw)
    ffc=ffc_raw#k_median_filter(ffc_raw)
    ffc=np.where(ffc>1.1, 1.1, ffc)
    ffc=np.where(ffc<=0.0, 0.05, ffc)
    ffc=ffc/np.amax(ffc)
    ffc = np.round(ffc * 65535).astype(np.uint16)
    return ffc

st_time=time.time()

#######-------------- Parameters -------------###########

in_folder=r'D:\Data\22_02_28\CT_2000proj_abs_calib_phantom_big\RAW\\'
out_folder=r'D:\Data\22_02_28\CT_2000proj_abs_calib_phantom_big\FFC\\'

N_proj=2000
proj0=0
angles=np.linspace(proj0*360/N_proj,360,N_proj-proj0+1)
#angles=[343]

N_ff=10
ff_freq=2000 #(in terms of the projection angle)

try:
    out=os.mkdir(out_folder)
except OSError:
    print ("Can't create directory %s" % out_folder)

##########------------- Main ------------############

for angle in angles:
    #proj0=int(angle*N_proj/360)
    name='proj_000'+str(proj0)+'.tif'
    ff_start=FF_image(in_folder, 'ff_post_', N_ff) #only left tile
    ff_end=FF_image(in_folder, 'ff_post_', N_ff)#only left tile
    
    dark_start=FF_image(in_folder, 'dark_post_', N_ff)
    dark_end=FF_image(in_folder, 'dark_post_', N_ff)
    
    raw_proj=tifffile.imread(in_folder+name)#only left tile
    print('Projection: ', proj0)
    ffc=FlatField(raw_proj, ff_start, ff_end, dark_start, dark_end, proj0, N_proj)#.astype('uint16')
    tifffile.imwrite(out_folder+'ffc_000'+str(proj0)+'.tif', ffc, photometric='minisblack')
    print('Ellapsed time = ', time.time()-st_time)
    proj0+=1