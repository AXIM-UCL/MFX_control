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
import multiprocessing as mp
import os
import tifffile

def phase_retrieval(sample, ff_start, ff_end, fraction, x_step, y_step, xs, ys):
    
    ff=fraction*ff_start+(1-fraction)*ff_end

    pad=2
    pix_size=50e-3
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

def retrieval_save_steps(proj, folder, folder_out, xs, ys, Nproj):
    num_dith_y=4
    num_dith_x=4
    
    M_mask=5
    
    y_step=50e-3/num_dith_y
    x_step=50e-3/num_dith_x
      
    n_ap_x=len(xs)
    n_ap_y=len(ys)
    
    abs_imgs=np.zeros((num_dith_y* num_dith_x, n_ap_y, n_ap_x))
    x_grad_imgs=np.zeros((num_dith_y* num_dith_x, n_ap_y, n_ap_x))
    y_grad_imgs=np.zeros((num_dith_y* num_dith_x, n_ap_y, n_ap_x))

    
    #out_name='retrieval_proj_000'+str(proj)
    
    print('Retrieving proj. Num', proj)
    start_ret_time = time.time()
    ind=0
    for i in range(num_dith_y):
        for j in range(num_dith_x):
            folder_in = os.path.join( folder, 'dith_x_'+str(j)+'dith_y_'+str(i))
            sub_start_time = time.time()
            sample=tifffile.imread(os.path.join(folder_in,'dfc_000'+str(proj)+'.tif')) 
            ff_start=tifffile.imread(os.path.join(folder_in, 'ff_pre.tif')) #only left tile
            ff_end=tifffile.imread(os.path.join(folder_in, 'ff_post.tif'))#only left tile
            refx_img, refy_img, abs_img=phase_retrieval(sample, ff_start, ff_end, proj/Nproj, j*x_step*M_mask, i*y_step*M_mask, xs, ys)
            abs_imgs[ind, :,:]=abs_img
            x_grad_imgs[ind,:,:]=refx_img
            y_grad_imgs[ind,:,:]=refy_img
            ind+=1
            print('Dith step: '+ str(i) + ' - ' + str(j)+ ', time=', time.time()-sub_start_time)
    
    print('Total retrieval time', time.time()-start_ret_time)
    #Save images
    tifffile.imwrite(folder_out+'proj_000'+str(proj)+'_dith_steps_att.tif', abs_imgs.astype(np.float32), photometric='minisblack')
    tifffile.imwrite(folder_out+'proj_000'+str(proj)+'_dith_steps_xgrad.tif', x_grad_imgs.astype(np.float32), photometric='minisblack')
    tifffile.imwrite(folder_out+'proj_000'+str(proj)+'_dith_steps_ygrad.tif', y_grad_imgs.astype(np.float32), photometric='minisblack')

    #np.savez(folder_out+out_name, abs_imgs=abs_imgs, x_grad_imgs=x_grad_imgs, y_grad_imgs=y_grad_imgs)


##-------------------Main----------------##
folder=r'\home\cleon\RDSS_Carlos\DATA\22_03_03\2BTCT_2000proj_4x4_RatHeart_2s\\'
folder_data=r'\home\cleon\RDSS_Carlos\DATA\22_03_03\2BTCT_2000proj_4x4_RatHeart_2s\DFC'
beamlet_name=r'\home\cleon\RDSS_Carlos\DATA\22_03_03\2BTCT_2000proj_4x4_RatHeart_2s\DFC\dith_x_0dith_y_0\\ff_pre.tif'
folder_out=folder+'Retrieved\\'
#beamlet_name='sample_xpos_0.0_ypos_0.0.dat'

ff_beamlet=tifffile.imread(beamlet_name)
ff_beamlet=ff_beamlet.astype(np.float32)
ff_blur = cv2.GaussianBlur(ff_beamlet,(3,3),0)
mean_x=np.mean(ff_blur, axis=0)
mean_y=np.mean(ff_blur, axis=1)
    
ys,_=find_peaks(mean_y, distance=4);ys=ys[1:-1]
xs,_=find_peaks(mean_x, distance=4);xs=xs[1:-1]

try:
    out=os.mkdir(folder_out)
except OSError:
    print ("Directory %s already exists" % folder_out)

Nproj=2000

# if __name__ == '__main__':

#     pool = mp.Pool(mp.cpu_count())
    
#     for i in range(Nproj):
#         print('Processing projection: ', i)
#         pool.apply_async(retrieval_save_steps, args=(i, folder_data, folder_out, xs, ys, Nproj))
#     pool.close()

retrieval_save_steps(10, folder_data, folder_out, xs, ys, Nproj)


#if __name__ == '__main__':
    #pool = mp.Pool(5)
    
    




 