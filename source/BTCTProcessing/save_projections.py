# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 15:07:36 2021

@author: Carlos Navarrete-Leon
"""

import numpy as np
import tifffile
from os import mkdir
from os.path import join, isdir

import time
import tifffile

def stick_dith_steps(fname, n_ap_y, num_dith_y, n_ap_x, num_dith_x, tot_dith_steps, projN):
    npzfile=np.load(fname)
    abs_imgs=npzfile['abs_imgs']
    x_grad_imgs=npzfile['x_grad_imgs']
    y_grad_imgs=npzfile['y_grad_imgs']
    
    if(projN<450):
        str_back, end_back=(50,52)
        #str_back, end_back=(15,20)
    else:
        str_back, end_back=(1,3)
        #str_back, end_back=(15,20)

    full_abs_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    full_x_grad_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    full_y_grad_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    
    sub_i=0
    for i in range(0, tot_dith_steps,int(tot_dith_steps/num_dith_y)):
        sub_j=0

        for j in range(0, tot_dith_steps, int(tot_dith_steps/num_dith_x)):
            sub_abs_img=abs_imgs[:,:,i,j]/np.mean(abs_imgs[5:35,str_back:end_back,i,j])
            sub_x_grad_img=x_grad_imgs[:,:,i,j]-np.mean(x_grad_imgs[5:35,str_back:end_back,i,j])
            sub_y_grad_img=y_grad_imgs[:,:,i,j]-np.mean(y_grad_imgs[5:35,str_back:end_back,i,j])
            ind_sub_row=sub_i
            for row in range(n_ap_y-1, -1, -1):
                ind_sub_col=sub_j
                for col in range(n_ap_x-1, -1, -1):
                    #print(i,j,row,col, ind_sub_row, ind_sub_col)
                    full_abs_img[ind_sub_row,ind_sub_col]=sub_abs_img[row,col]
                    full_x_grad_img[ind_sub_row,ind_sub_col]=sub_x_grad_img[row,col]
                    full_y_grad_img[ind_sub_row,ind_sub_col]=sub_y_grad_img[row,col]
                    ind_sub_col+=num_dith_x   
                ind_sub_row+=num_dith_y
            sub_j+=1
        sub_i+=1
    
    full_abs_img=np.flipud(np.fliplr(full_abs_img))
    full_x_grad_img=np.flipud(np.fliplr(full_x_grad_img))
    full_y_grad_img=np.flipud(np.fliplr(full_y_grad_img))
        
    return full_abs_img, full_x_grad_img, full_y_grad_img

def phase_integration(full_x_grad_img, full_y_grad_img, sample_period, num_dith_x, num_dith_y, pix_size, z_sd):

    x_grad=np.arctan(pix_size*full_x_grad_img/z_sd)#[10*num_dith_y:-2*num_dith_y,69*num_dith_x:-12*num_dith_x]
    y_grad=np.arctan(pix_size*full_y_grad_img/z_sd)#[10*num_dith_y:-2*num_dith_y,69*num_dith_x:-12*num_dith_x]

    complex_grad=x_grad+ 1j*y_grad

    ny, nx = x_grad.shape

    kx = (np.arange(nx) - nx /2.) / (nx*sample_period/num_dith_x)
    ky = (np.arange(ny) - ny /2.) / (ny*sample_period/num_dith_y)

    kxs, kys = np.meshgrid(kx, ky)

    Fys=np.fft.fft2(complex_grad)

    with np.errstate(divide="ignore", invalid="ignore"):
        modFys = np.fft.ifftshift(1./ (2. * np.pi * 1j * (kxs+1j*kys)) * np.fft.fftshift(Fys))
    modFys=np.nan_to_num(modFys)
    integral = np.fft.ifft2(modFys).real
    #background=integral[1*num_dith_y:6*num_dith_y, 32*num_dith_x:37*num_dith_x]
    background=integral[1*num_dith_y:30*num_dith_y, 1*num_dith_x:5*num_dith_x]
    
    integral-=np.mean(background)
       
    #lamb=1.2398/(14*1000*100)
    
    #integrated_phase=(2*np.pi)/lamb*integral

    return integral

st_time=time.time()

distance_source_origin = 187 # [mm]
distance_source_detector= 866 # [mm]//
distance_origin_detector = distance_source_detector-distance_source_origin

M=distance_source_detector/distance_source_origin

detector_pixel_size = 0.062  # [mm]

tot_dith_steps=8
num_dith_y=8
num_dith_x=8
n_ap_x=54
n_ap_y=42
period=100e-3

M_mask=5.6
sample_period=period*M_mask/M
eff_pix_size=period/num_dith_x*(M_mask/M)#detector_pixel_size/M

num_of_projections = 900
angles = np.linspace(0, 2 * np.pi, num=num_of_projections, endpoint=False)
in_dir=r'C:\Data\21_10_29\2BTCT_900proj_aesophagaeus_native20\RAW\retrieval\\'
out_dir = r'C:\Data\21_10_29\2BTCT_900proj_aesophagaeus_native20\Projections\\'

if not isdir(out_dir):
    mkdir(out_dir)

for i in range(num_of_projections):
    file_name='retrieval_proj_000'+str(i)+'.npz'
    im_abs, im_xgrad, im_ygrad = stick_dith_steps(in_dir+file_name, n_ap_y, num_dith_y, n_ap_x, num_dith_x, tot_dith_steps, projN=i)
    im_abs=np.where(im_abs<0, 0, im_abs)
    im_abs=np.where(im_abs>1, 1, im_abs)
    
    im_phase = phase_integration(im_xgrad, im_ygrad, sample_period, num_dith_x, num_dith_y, detector_pixel_size, distance_origin_detector)
    im_phase=np.where(im_phase<0, 0, im_phase)
    
    tifffile.imwrite(out_dir+'proj_abs_000'+str(i)+'.tif', im_abs.astype(np.float32), photometric='minisblack')
    tifffile.imwrite(out_dir+'proj_phase_000'+str(i)+'.tif', im_phase.astype(np.float32), photometric='minisblack')
    
    print('Projection: ', i)
    print('Ellapsed time = ', time.time()-st_time)



