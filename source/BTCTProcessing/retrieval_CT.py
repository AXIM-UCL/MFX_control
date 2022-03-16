# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 16:05:41 2021

@author: Carlos Navarrete-Leon
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
#import multiprocessing as mp
import os
import tifffile

def phase_retrieval(sample_name, ff_start, ff_end, fraction, x_step, y_step, xs, ys, N_frames, N_ff):
    
    sample=tifffile.imread(sample_name)
    
    ff=fraction*ff_start+(1-fraction)*ff_end

    pad=4
    pix_size=62e-3
    ys, xs = (ys+y_step/pix_size, xs+x_step/pix_size)
    
    x_shifts=np.zeros((len(ys), len(xs)))
    y_shifts=np.zeros((len(ys), len(xs)))
    abs_img=np.zeros((len(ys), len(xs)))
    
    for i in range(len(ys)):
        for j in range(len(xs)):
            beam_sample=sample[int(ys[i])-pad:int(ys[i])+pad+1, int(xs[j])-pad:int(xs[j])+pad+1]
            beam_ff=ff[int(ys[i])-pad:int(ys[i])+pad+1, int(xs[j])-pad:int(xs[j])+pad+1]
            out=phase_cross_correlation(beam_ff, beam_sample, upsample_factor=100, space='real')
            if(ys[i]==244 and xs[j]==247):
                a=1
            y_shift, x_shift = out[0] 
            absorp=np.sum(beam_sample)/np.sum(beam_ff)
            x_shifts[i, j]=x_shift
            y_shifts[i,j]=y_shift
            abs_img[i,j]=absorp
        
    return x_shifts, y_shifts, abs_img


#To average the 10 flat field images    
def FF_image(path, prefix, N_ff):
    out=tifffile.imread(path+prefix+str(0)+'.tif')
    for i in range(1,N_ff):
        file_name = path+prefix+str(i)+'.tif'
        out+=tifffile.imread(file_name)
    out=out/N_ff
    return out
    

def retrieval_save_steps(proj, folder, folder_out, xs, ys, Nproj):
    N_frames=1
    N_ff=10
    num_dith_y=8
    num_dith_x=8
    
    M_mask=5.6
    
    y_step=100e-3/num_dith_y
    x_step=100e-3/num_dith_x
      
    n_ap_x=len(xs)
    n_ap_y=len(ys)
    
    abs_imgs=np.zeros((n_ap_y, n_ap_x, num_dith_y, num_dith_x))
    x_grad_imgs=np.zeros((n_ap_y, n_ap_x, num_dith_y, num_dith_x))
    y_grad_imgs=np.zeros((n_ap_y, n_ap_x, num_dith_y, num_dith_x))
    
    out_name='retrieval_proj_000'+str(proj)
    
    print('Retrieving proj. Num', proj)
    start_ret_time = time.time()

    for i in range(num_dith_y):
        for j in range(num_dith_x):
            folder_in = folder + 'dith_x_'+str(j)+'dith_y_'+str(i)+'\\'
            sub_start_time = time.time()
            sample_name = folder_in+'proj_000'+str(proj)+'.tif'
            ff_start=FF_image(folder_in, 'ff_pre_', N_ff) #only left tile
            ff_end=FF_image(folder_in, 'ff_post_', N_ff)#only left tile
            refx_img, refy_img, abs_img=phase_retrieval(sample_name, ff_start, ff_end, proj/Nproj, j*x_step*M_mask, i*y_step*M_mask, xs, ys, N_frames, N_ff)
            abs_imgs[:,:,num_dith_y-1-i, num_dith_x-1-j]=abs_img
            x_grad_imgs[:,:,num_dith_y-1-i, num_dith_x-1-j]=refx_img
            y_grad_imgs[:,:,num_dith_y-1-i, num_dith_x-1-j]=refy_img
            print('Dith step: '+ str(i) + ' - ' + str(j)+ ', time=', time.time()-sub_start_time)
    print('Total retrieval time', time.time()-start_ret_time)
    #Save images
    #np.savez(folder_out+out_name, abs_imgs=abs_imgs, x_grad_imgs=x_grad_imgs, y_grad_imgs=y_grad_imgs)


##-------------------Main----------------##
folder=r'C:\Data\21_10_29\2BTCT_900proj_aesophagaeus_native20\RAW\\'
beamlet_name='dith_x_0dith_y_0\\ff_pre_0.tif'
folder_out=folder+'retrieval\\'
#beamlet_name='sample_xpos_0.0_ypos_0.0.dat'

ff_beamlet=tifffile.imread(folder+beamlet_name)
ff_beamlet=ff_beamlet.astype(np.float32)
ff_blur = cv2.GaussianBlur(ff_beamlet,(5,5),0)
mean_x=np.mean(ff_blur, axis=0)
mean_y=np.mean(ff_blur, axis=1)
    
ys,_=find_peaks(mean_y, distance=7);ys=ys[1:-1]
xs,_=find_peaks(mean_x, distance=7);xs=xs[1:55]

try:
    out=os.mkdir(folder_out)
except OSError:
    print ("Directory %s already exists" % folder_out)

Nproj=900

# if __name__ == '__main__':

#     pool = mp.Pool(mp.cpu_count())
    
#     for i in range(Nproj):
#         print('Processing projection: ', i)
#         pool.apply_async(retrieval_save_steps, args=(i, folder, folder_out, xs, ys, Nproj))
#     pool.close()

#retrieval_save_steps(5, folder, folder_out, xs, ys, Nproj)


#if __name__ == '__main__':
    #pool = mp.Pool(5)
    
    




 