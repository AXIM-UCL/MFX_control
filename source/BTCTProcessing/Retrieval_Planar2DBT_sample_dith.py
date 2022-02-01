import sys
sys.path.insert(1, r'C:\Users\XPCI_BT\Documents\GitHub\MFX_control')
import numpy as np
import matplotlib.pyplot as plt
from skimage.registration import phase_cross_correlation
import time
from scipy.signal import find_peaks
import cv2
import os
import tifffile

#### Important functions

#To average the 10 flat field images. Flat field images are in separate tiff files    
def FF_image(path, prefix, N_ff):
    out=tifffile.imread(path+prefix+str(0)+'.tif')
    for i in range(1,N_ff):
        file_name = path+prefix+str(i)+'.tif'
        out+=tifffile.imread(file_name)
    out=out/N_ff
    return out


## Function for phase retrieval.
## Usually flat fields are acquired before and after (the fraction is given by the frame being corrected)
# xs and ys are the beamlet positions (assuming no movement)
# The pad depends on the mask period in pixels (currently is about 9). Odd numbers are preferred.
# This retrieval uses subpixel cross-correlation
def phase_retrieval(sample_name, ff_start, ff_end, fraction, xs, ys, pad=4):
    
    sample=tifffile.imread(sample_name)#.astype(np.float32)
        
    ff=fraction*ff_end+(1-fraction)*ff_start
    
    x_shifts=np.zeros((len(ys), len(xs)))
    y_shifts=np.zeros((len(ys), len(xs)))
    abs_img=np.zeros((len(ys), len(xs)))
    
    for i in range(len(ys)):
        for j in range(len(xs)):
            beam_sample=sample[int(ys[i])-pad:int(ys[i])+pad+1, int(xs[j])-pad:int(xs[j])+pad+1]
            beam_ff=ff[int(ys[i])-pad:int(ys[i])+pad+1, int(xs[j])-pad:int(xs[j])+pad+1]
            
            out=phase_cross_correlation(beam_ff, beam_sample, upsample_factor=100, space='real')
            y_shift, x_shift = out[0] 
            absorp=np.sum(beam_sample)/np.sum(beam_ff)
            
            x_shifts[i, j]=x_shift
            y_shifts[i,j]=y_shift
            abs_img[i,j]=absorp
    
    plt.figure()
    plt.imshow(sample[int(ys[10])-pad:int(ys[10])+pad+1, int(xs[10])-pad:int(xs[10])+pad+1])
    plt.show()

    return x_shifts, y_shifts, abs_img

##Function to stitch the dithering steps
# Takes different images and reorganizes them to create a full image.
#The code changes a bit depending on sample/mask relative movement.
# Dithering steps are normalized with a background region.
def stitch_dith_steps(abs_imgs, x_grad_imgs, y_grad_imgs, n_ap_y, num_dith_y, n_ap_x, num_dith_x, tot_dith_steps):

    full_abs_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    full_x_grad_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    full_y_grad_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    
    sub_i=0
    for i in range(0, tot_dith_steps,int(tot_dith_steps/num_dith_y)):
        sub_j=0
        for j in range(0, tot_dith_steps, int(tot_dith_steps/num_dith_x)):
            sub_abs_img=abs_imgs[:,:,i,j]#/np.mean(abs_imgs[6:10,44:48,i,j])
            sub_x_grad_img=x_grad_imgs[:,:,i,j]-np.mean(x_grad_imgs[6:10,44:48,i,j])
            sub_y_grad_img=y_grad_imgs[:,:,i,j]-np.mean(y_grad_imgs[6:10,44:48,i,j])
            ind_sub_row=sub_i
            for row in range(n_ap_y-1, -1, -1):
            #for row in range(n_ap_y):
                ind_sub_col=sub_j
                for col in range(n_ap_x-1, -1, -1):
                #for col in range(n_ap_x):
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


## Functionfor phase integration using the Fourier integration method.
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
    background=integral[1*num_dith_y:4*num_dith_y, 1*num_dith_x:4*num_dith_x]
    
    integral-=np.mean(background)
      
    return integral

####--------------Main------------------####


#### Parameters

folder=r'D:\Data\21_12_09\Pixirad_DirectionalDF_X_40kVp_250uA_100umpitch_medfoc\\'
folder_out=folder+'processed\\'
try:
    out=os.mkdir(folder_out)
except OSError:
    print ("Can't create directory %s" % folder_out)


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

abs_imgs=np.zeros((n_ap_y, n_ap_x, num_dith_y, num_dith_x))
x_grad_imgs=np.zeros((n_ap_y, n_ap_x, num_dith_y, num_dith_x))
y_grad_imgs=np.zeros((n_ap_y, n_ap_x, num_dith_y, num_dith_x))

out_name='retrieval_images.npz'
save=1 #Save full images and dithering steps.


## To find the coordinates of the beamlets:
ff_beamlet=FF_image(folder, 'ff_post_', N_ff).astype(np.float32)
ff_blur = cv2.GaussianBlur(ff_beamlet,(5,5),0)

ys,_=find_peaks(np.mean(ff_blur, axis=1), distance=7);
ys=ys[1:-1]
xs,_=find_peaks(np.mean(ff_blur, axis=0), distance=7);
xs=xs[1:55]

start_ret_time = time.time()

if(save==1):
    d_frac=1/(num_dith_x*num_dith_y)
    frac=0
    for i in range(num_dith_y):
        for j in range(num_dith_x):
            sub_start_time = time.time()
            sample_name = folder+'sample_xpos_'+str(round(j*x_step, 4))+'_ypos_'+str(round(i*y_step,4))+'.tif'
            ff_start=FF_image(folder, 'ff_pre_', N_ff) #only left tile
            ff_end=FF_image(folder, 'ff_post_', N_ff)#only left tile
            refx_img, refy_img, abs_img=phase_retrieval(sample_name, ff_start, ff_end, frac, xs, ys)
            abs_imgs[:,:,num_dith_y-1-i, num_dith_x-1-j]=abs_img
            x_grad_imgs[:,:,num_dith_y-1-i, num_dith_x-1-j]=refx_img
            y_grad_imgs[:,:,num_dith_y-1-i, num_dith_x-1-j]=refy_img
            frac+=d_frac
            print('Dith step: '+ str(i) + ' - ' + str(j)+ ', time=', time.time()-sub_start_time)
    print('Total retrieval time', time.time()-start_ret_time)
    #Save images
    np.savez(folder_out+out_name, abs_imgs=abs_imgs, x_grad_imgs=x_grad_imgs, y_grad_imgs=y_grad_imgs)


npzfile=np.load(folder_out+out_name)
abs_imgs=npzfile['abs_imgs'];x_grad_imgs=npzfile['x_grad_imgs'];y_grad_imgs=npzfile['y_grad_imgs']

im_abs, im_xgrad, im_ygrad = stitch_dith_steps(abs_imgs, x_grad_imgs, y_grad_imgs, n_ap_y, num_dith_y, n_ap_x, num_dith_x, tot_dith_steps)

refx_img=np.arctan(detector_pixel_size*im_xgrad/distance_origin_detector)
refy_img=np.arctan(detector_pixel_size*im_ygrad/distance_origin_detector)


im_phase = phase_integration(im_xgrad, im_ygrad, sample_period, num_dith_x, num_dith_y, detector_pixel_size, distance_origin_detector)


## Save images and show them
tifffile.imwrite(folder_out+'attenuation.tif', im_abs.astype(np.float32), photometric='minisblack')
tifffile.imwrite(folder_out+'refx_img.tif', refx_img.astype(np.float32), photometric='minisblack')
tifffile.imwrite(folder_out+'refy_img.tif', refy_img.astype(np.float32), photometric='minisblack')
tifffile.imwrite(folder_out+'phase.tif', im_phase.astype(np.float32), photometric='minisblack')


plt.figure();plt.imshow(im_abs, vmin=0.75, vmax=1.1);plt.colorbar()

plt.figure();plt.imshow(im_ygrad, vmin=-0.5, vmax=0.5);plt.colorbar()
plt.figure();plt.imshow(im_xgrad, vmin=-0.5, vmax=0.5);plt.colorbar()

plt.figure();plt.imshow(im_phase, vmin=-0.2e-6, vmax=1e-6);plt.colorbar()

