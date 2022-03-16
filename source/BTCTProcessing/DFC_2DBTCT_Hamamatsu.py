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
from scipy import interpolate
import matplotlib.pyplot as plt
import multiprocessing as mp

#To average the 10 flat field images    
def Dark_Flat_image(path, prefix, N_ff):
    out=tifffile.imread(path+prefix+str(0)+'.tif')
    for i in range(1,N_ff):
        out+=tifffile.imread(path+prefix+str(i)+'.tif')
    out=out/N_ff
    return out
    
#Flat field correction with post k-median folder
def DarkField(img_raw, dark_start, dark_end, proj_no, N_proj, out_folder, file_name):
    weight=proj_no/N_proj
    dark_mean=(1-weight)*dark_start + weight*dark_end
    dfc=img_raw-dark_mean
    dfc=np.nan_to_num(dfc)
    #dfc=dfc/np.amax(dfc)
    dfc = np.round(dfc).astype(np.uint16)
    tifffile.imwrite(out_folder+file_name, dfc, photometric='minisblack')

def read_flip_crop_interpolate(im, min_int, max_int, center, xsize, ysize):
    array=np.flipud(im)[center-ysize:center+ysize,center-xsize:center+xsize]
    out=np.zeros(array.shape)
    x = np.arange(0, array.shape[1])
    for i in range(array.shape[0]):
        y=array[i,:]
        cond=[y<min_int] or [y>max_int]
        ym = np.where(cond, True, False)[0]
        x1=x[~ym]
        y1=y[~ym]
        f = interpolate.interp1d(x1, y1, 'cubic')
        ynew=f(x)
        out[i,:]=ynew
     
    out=np.where(out>max_int, max_int, out)
    #out=out/np.amax(out)*65535
    #out=out.astype(np.uint16)

    return out

st_time=time.time()

#######-------------- Parameters -------------###########

in_folder=r'D:\Data\22_03_03\2BTCT_2000proj_4x4_RatHeart_2s\RAW\\'
out_folder=r'D:\Data\22_03_03\2BTCT_2000proj_4x4_RatHeart_2s\DFC\\'

try:
    out=os.mkdir(out_folder)
except OSError:
    print ("Directory %s already exists" % out_folder)

N_proj=2000
proj0=0
num_dith_y=1
num_dith_x=1
N_ff=10



for i in range(num_dith_y):
        for j in range(num_dith_x):
            print('Processing dithering step x: '+str(j)+'and dithering step y: '+str(i))
            folder_in_name = in_folder+'dith_x_'+str(j)+'dith_y_'+str(i)+'\\'
            folder_out_name = out_folder+'dith_x_'+str(j)+'dith_y_'+str(i)+'\\'
            try:
                file=os.mkdir(folder_out_name)
            except OSError:
                print ("Couldn't create directory %s already exists" % folder_out_name)
            dark_pre=read_flip_crop_interpolate(Dark_Flat_image(folder_in_name, 'dark_pre_', N_ff), 40, 400, 1253, 800, 1000)
            dark_post=read_flip_crop_interpolate(Dark_Flat_image(folder_in_name, 'dark_post_', N_ff), 40, 400, 1253, 800, 1000)
            #pool = mp.Pool(mp.cpu_count())
            flat_pre=read_flip_crop_interpolate(Dark_Flat_image(folder_in_name, 'ff_pre_', N_ff), 200, 1000, 1253, 800, 1000)
            DarkField(flat_pre, dark_pre, dark_pre, 1, 2000, folder_out_name, 'ff_pre.tif')
            for z in range(138,139):
                print('Processing projection: ', z)
                file_name='proj_000'+str(z)+'.tif'
                im=tifffile.imread(folder_in_name+file_name)
                raw=read_flip_crop_interpolate(im, 200, 1000, 1253, 800, 1000)
                DarkField(raw, dark_pre, dark_post, z, 2000, folder_out_name, 'dfc_000'+str(z)+'.tif')
            
            flat_post=read_flip_crop_interpolate(Dark_Flat_image(folder_in_name, 'ff_post_', N_ff), 200, 1000, 1253, 800, 1000)
            DarkField(flat_post, dark_post, dark_post, 1, 2000, folder_out_name, 'ff_post.tif')
                #pool.apply_async(DarkField, args=(raw, dark_pre, dark_post, z, 2000, folder_out_name))
            #pool.close()

#name='dark_post_0.tif'

#im=read_flip_crop_interpolate(in_folder, name, 50, 400, 1253, 800, 1000)

#plt.imshow(im)

##########------------- Main ------------############

# c
# ff_start=FF_image(in_folder, 'ff_post_', N_ff) #only left tile
# ff_end=FF_image(in_folder, 'ff_post_', N_ff)#only left tile

# dark_start=FF_image(in_folder, 'dark_post_', N_ff)
# dark_end=FF_image(in_folder, 'dark_post_', N_ff)

# raw_proj=tifffile.imread(in_folder+name)#only left tile
# print('Projection: ', proj0)
# ffc=FlatField(raw_proj, ff_start, ff_end, dark_start, dark_end, proj0, N_proj)#.astype('uint16')
# #tifffile.imwrite(out_folder+'ffc_000'+str(proj0)+'.tif', ffc, photometric='minisblack')


