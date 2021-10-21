# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 11:55:37 2021

@author: XPCI_BT
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
    for i in range(patchsize, 402-patchsize):
        for j in range(patchsize, 512-patchsize):
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
        out+=tifffile.imread(path+prefix+str(0)+'.tif')
    out=out/N_ff
    return out
    
#Flat field correction with post k-median folder
def FlatField(img_raw, ff_start, ff_end, proj_no, N_proj, patchsize=2):
    weight=proj_no/N_proj
    ff_mean=(1-weight)*ff_start + weight*ff_end
    ffc_raw=img_raw/ff_mean
    ffc_raw=np.nan_to_num(ffc_raw)
    ffc=k_median_filter(ffc_raw)
    ffc=np.where(ffc>1.1, 1.0, ffc)
    ffc=np.where(ffc<=0.0, 0.05, ffc)
    return ffc.astype(np.float32)

st_time=time.time()

#######-------------- Parameters -------------###########

in_folder=r'C:\Data\21_10_20\CT_900proj_abs_calib_phantom\RAW\\'
out_folder=r'C:\Data\21_10_20\CT_900proj_abs_calib_phantom\FFC\\'
  
   
N_proj=900
proj0=0
angles=np.linspace(proj0*360/N_proj,360,N_proj-proj0+1)
#angles=[343]

N_ff=10
ff_freq=900 #(in terms of the projection angle)

try:
    out=os.mkdir(out_folder)
except OSError:
    print ("Can't create directory %s" % out_folder)

##########------------- Main ------------############

for angle in angles:
    #proj0=int(angle*N_proj/360)
    name='proj_000'+str(proj0)+'.tif'
    ff_start=FF_image(in_folder, 'ff_pre_', N_ff)[:,:512] #only left tile
    ff_end=FF_image(in_folder, 'ff_post_', N_ff)[:,:512]#only left tile
    raw_proj=tifffile.imread(in_folder+name)[:,:512]#only left tile
    print('Projection: ', proj0)
    ffc=FlatField(raw_proj, ff_start, ff_end, proj0, N_proj)#.astype('uint16')
    tifffile.imwrite(out_folder+'ffc_000'+str(proj0)+'.tif', ffc, photometric='minisblack')
    print('Ellapsed time = ', time.time()-st_time)
    proj0+=1


