# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 15:36:29 2021

@author: Carlos Navarrete-Leon
"""
import sys
sys.path.insert(1, r'C:\Users\XPCI_BT\Documents\GitHub\MFX_control')
import numpy as np
import matplotlib.pyplot as plt
import cv2
#import tools_pixirad
#from skimage.feature import match_template
#from skimage.feature import peak_local_max
#from skimage.registration import phase_cross_correlation
#from scipy.interpolate import NearestNDInterpolator
#import time

#%% To upload the data and set the parameters

def get_images(folder, fname, num_dith_x, num_dith_y):
    tot_dith_steps=16
    #num_dith_y=1
    #num_dith_x=1
    n_ap_x=111
    n_ap_y=42
    
    npzfile=np.load(folder+fname)
    abs_imgs=npzfile['abs_imgs']
    x_grad_imgs=npzfile['x_grad_imgs']
    y_grad_imgs=npzfile['y_grad_imgs']
    
    # =============================================================================
    # Stick dithered images
    # =============================================================================
    
    full_abs_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    full_x_grad_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    full_y_grad_img=np.zeros((n_ap_y*num_dith_y, n_ap_x*num_dith_x))
    
    sub_i=0
    for i in range(0, tot_dith_steps,int(tot_dith_steps/num_dith_y)):
        sub_j=0
        for j in range(0, tot_dith_steps, int(tot_dith_steps/num_dith_x)):
            sub_abs_img=abs_imgs[:,:,i,j]
            sub_x_grad_img=x_grad_imgs[:,:,i,j]
            sub_y_grad_img=y_grad_imgs[:,:,i,j]
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
 
    # =============================================================================
    # Phase integration and calculate thickness
    # =============================================================================
   
def theoretical_thickness(material_data, spec_data, sph_radius, x0, y0, x_grid, y_grid, loth_att, loth_phase):
    
    dist=np.sqrt((x_grid-x0)**2+(y_grid-y0)**2)
    thickness=np.nan_to_num(2*np.sqrt(sph_radius**2-dist**2))
    
    
    energies, e_weights = spec_data[:,0], spec_data[:,1]
    energies, deltas, betas =material_data[:,0], material_data[:,1], material_data[:,2]
    e_weights_att=np.where(energies<loth_att, 0, e_weights)
    e_weights_phase=np.where(energies<loth_phase, 0, e_weights)
    e_weights_att=e_weights_att/np.sum(e_weights_att)
    e_weights_phase=e_weights_phase/np.sum(e_weights_phase)
    poly_opt_thick=np.zeros(x_grid.shape)
    poly_ref_x=np.zeros(x_grid.shape)
    poly_ref_y=np.zeros(x_grid.shape)
    #poly_phase_int=np.zeros(x_grid.shape)
    
    for i in range(len(e_weights)):
        lamb=1.2398/(energies[i]*1000)/1000
        poly_opt_thick+=e_weights_att[i]*(4*np.pi*betas[i]/lamb)*thickness
        poly_ref_x+=e_weights_phase[i]*np.gradient(thickness, x_grid[0,1]-x_grid[0,0], axis=1)*deltas[i]*np.exp(-4*np.pi/lamb*betas[i]*thickness)
        poly_ref_y+=e_weights_phase[i]*np.gradient(thickness, y_grid[1,0]-y_grid[0,0], axis=0)*deltas[i]*np.exp(-4*np.pi/lamb*betas[i]*thickness)
        #poly_phase_int+=e_weights_phase[i]*deltas[i]*thickness*np.exp(-4*np.pi/lamb*betas[i]*thickness)
        
    return poly_opt_thick, poly_ref_x, poly_ref_y
        
def phase_integration(x_grad, y_grad, period, num_dith_x, num_dith_y):
    
    complex_grad=x_grad+ 1j*y_grad
    
    ny, nx = x_grad.shape
    
    kx = (np.arange(nx) - nx /2.) / (nx*period/num_dith_x)
    ky = (np.arange(ny) - ny /2.) / (ny*period/num_dith_y)
    
    kxs, kys = np.meshgrid(kx, ky)
    
    Fys=np.fft.fft2(complex_grad)
    
    with np.errstate(divide="ignore", invalid="ignore"):
        modFys = np.fft.ifftshift(1./ (2. * np.pi * 1j * (kxs+1j*kys)) * np.fft.fftshift(Fys))
    modFys=np.nan_to_num(modFys)
    integral = np.fft.ifft2(modFys).real
    background=integral[35*num_dith_y:40*num_dith_y, 1*num_dith_x:4*num_dith_x]
    
    integral-=np.mean(background)
    
    return integral
    
#%%
folder=r'C:\Data\21_07_15\Sample16x16_PXcooled\\'
fname='retrieved_sample_integration2.npz'

mat_name=r'C:\Data\21_07_15\\PMMA_short.txt'
pmma_data=np.loadtxt(mat_name)

spec_name=r'C:\Data\21_07_15\\W_40kVp_TASMICS.txt'
spec_data=np.loadtxt(spec_name)

num_dith_x, num_dith_y = (16,16)
pix_size=62e-3
z_sd=680
period=100e-3

full_abs_img, full_x_grad_img, full_y_grad_img = get_images(folder, fname, num_dith_x, num_dith_y)

x_grad=np.arctan(pix_size*full_x_grad_img/z_sd)[4*num_dith_y:(4+36)*num_dith_y,61*num_dith_x:(61+36)*num_dith_x]
y_grad=np.arctan(pix_size*full_y_grad_img/z_sd)[4*num_dith_y:(4+36)*num_dith_y,61*num_dith_x:(61+36)*num_dith_x]
tr_img=-np.log(full_abs_img)[4*num_dith_y:(4+36)*num_dith_y,61*num_dith_x:(61+36)*num_dith_x]
    
M_mask_sample=1.16
sample_period=period*M_mask_sample

M_sample = 4.59

#integrated_phase = phase_integration(x_grad, y_grad, sample_period, num_dith_x, num_dith_y)


xs = (np.arange(36*num_dith_x)) * sample_period/num_dith_x# / M_sample
ys = (np.arange(36*num_dith_y)) * sample_period/num_dith_y# / M_sample
x_grid, y_grid = np.meshgrid(xs, ys)
    
radius=1.59

im_blur=cv2.GaussianBlur(tr_img,(5,5),0)
_,th = cv2.threshold(im_blur,0.1,0, cv2.THRESH_TOZERO)

eff_x0, eff_y0 = (np.sum(x_grid*th)/np.sum(th), np.sum(y_grid*th)/np.sum(th))

poly_att_theo, poly_ref_x, poly_ref_y=theoretical_thickness(material_data=pmma_data, spec_data=spec_data, sph_radius=radius, x0=eff_x0, y0=eff_y0, x_grid=x_grid, y_grid=y_grid, loth_att=12, loth_phase=12)

diff_abs=tr_img-poly_att_theo
diff_ref_x=x_grad-poly_ref_x
diff_ref_y=y_grad-poly_ref_y

poly_phase_exp = phase_integration(x_grad, y_grad, sample_period, num_dith_x, num_dith_y)
poly_phase_theo = phase_integration(poly_ref_x, poly_ref_y, sample_period, num_dith_x, num_dith_y)


#diff_phase=integrated_phase-poly_phase_theo
#diff_phase=thickness_phase-thickness_theo
    
#rmse_abs=np.sqrt(np.mean(thickness_abs-thickness_theo)**2/len(thickness_abs))
#rmse_phase=np.sqrt(np.mean(thickness_phase-thickness_theo)**2/len(thickness_phase))

plt.figure(figsize=(12,4))
plt.subplot(231)
plt.imshow(poly_att_theo);plt.colorbar()
plt.title('Att image')
plt.subplot(232)
plt.imshow(poly_ref_x);plt.colorbar()
plt.title('x-grad image')
plt.subplot(233)
plt.imshow(poly_ref_y);plt.colorbar()
plt.title('y-grad image')

plt.figure(figsize=(12,7))
plt.subplot(231)
plt.imshow(tr_img, vmin=0, vmax=0.35);plt.colorbar()
plt.title('Att image')
plt.subplot(232)
plt.imshow(x_grad, vmin=-3e-5, vmax=3e-5);plt.colorbar()
plt.title('x-grad image')
plt.subplot(233)
plt.imshow(y_grad, vmin=-3e-5, vmax=3e-5);plt.colorbar()
plt.title('y-grad image')
plt.subplot(234)
plt.imshow(diff_abs, vmin=0, vmax=0.1);plt.colorbar()
plt.title('Att Difference')
plt.subplot(235)
plt.imshow(diff_ref_x, vmin=-0.5e-5, vmax=0.5e-5);plt.colorbar()
plt.title('x-grad image difference')
plt.subplot(236)
plt.imshow(diff_ref_y, vmin=-0.5e-5, vmax=0.5e-5);plt.colorbar()
plt.title('y-grad image difference')

plt.figure(figsize=(12,12))
plt.subplot(221)
plt.scatter(xs, np.mean(tr_img[18*num_dith_y-3:18*num_dith_x+3,:], axis=0), c='r', s=3, label='Exp')
plt.plot(xs, np.mean(poly_att_theo[18*num_dith_y-3:18*num_dith_x+3,:], axis=0), label='Theo')
plt.legend()
plt.title(r'$-ln(I/I_0)(x)$')
plt.subplot(222)
plt.scatter(xs, np.mean(poly_phase_exp[18*num_dith_y-3:18*num_dith_x+3,:], axis=0), c='r', s=3, label='Exp')
plt.plot(xs, np.mean(poly_phase_theo[18*num_dith_y-3:18*num_dith_x+3,:], axis=0), label='Theo')
plt.legend()
plt.title(r'$\Phi(x)$')
plt.subplot(223)
plt.scatter(xs, np.mean(x_grad[18*num_dith_y-3:18*num_dith_x+3,:], axis=0), c='r', s=3, label='Exp')
plt.plot(xs, np.mean(poly_ref_x[18*num_dith_y-3:18*num_dith_x+3,:], axis=0), label='Theo')
plt.legend()
plt.title(r'$d\Phi(x,y)/dx$')
plt.subplot(224)
plt.scatter(ys, np.mean(y_grad[:,18*num_dith_y-3:18*num_dith_x+3], axis=1), c='r', s=3, label='Exp')
plt.plot(ys, np.mean(poly_ref_y[:,18*num_dith_y-3:18*num_dith_x+3], axis=1), label='Theo')
plt.legend()
plt.title(r'$d\Phi(x,y)/dy$')


#%%
fig = plt.figure(figsize=(12,12))
ax1 = fig.add_subplot(221)
im1=ax1.imshow(x_grad, cmap='gray', vmin=-4e-5, vmax=4e-5)
fig.colorbar(im1,ax=ax1)
ax1.set_title(r'$\alpha_x$ image')
ax2 = fig.add_subplot(222)
im2=ax2.imshow(y_grad, cmap='gray', vmin=-4e-5, vmax=4e-5)
fig.colorbar(im2,ax=ax2)
ax2.set_title(r'$\alpha_y$ image')
ax3 = fig.add_subplot(223)
im3=ax3.imshow(tr_img, cmap='gray')
ax3.set_title(r'$-ln(I/I_0)$')
fig.colorbar(im3,ax=ax3)
ax4 = fig.add_subplot(224)
im4=ax4.imshow(poly_phase_exp, cmap='gray')#, vmin=-10, vmax=4)
ax4.set_title(r'Integrated phase image')
fig.colorbar(im4,ax=ax4)

plt.figure(figsize=(12,4))
plt.subplot(231)
plt.imshow(tr_img);plt.colorbar()
plt.subplot(232)
plt.imshow(poly_att_theo);plt.colorbar()
plt.subplot(233)
plt.imshow(diff_abs);plt.colorbar()
plt.subplot(234)
plt.imshow(integrated_phase);plt.colorbar()
plt.subplot(235)
plt.imshow(poly_phase_theo);plt.colorbar()
plt.subplot(236)
plt.imshow(diff_phase);plt.colorbar()

plt.figure(figsize=(12,4))
plt.subplot(121)
plt.scatter(xs, np.mean(tr_img[18*num_dith_y-2:18*num_dith_x+2,:], axis=0), c='r', s=3)
plt.plot(xs, np.mean(poly_att_theo[18*num_dith_y-2:18*num_dith_x+2,:], axis=0))
plt.subplot(122)
plt.scatter(xs, np.mean(integrated_phase[18*num_dith_y-2:18*num_dith_x+2,:], axis=0), c='r', s=3)
plt.plot(xs, np.mean(poly_phase_theo[18*num_dith_y-2:18*num_dith_x+2,:], axis=0))


        

#%%
# =============================================================================
# Plot results
# =============================================================================

fig = plt.figure(figsize=(15,10))
ax1 = fig.add_subplot(231)
im1=ax1.imshow(thickness_abs, cmap='gray', vmin=0, vmax=3)
ax1.set_title(r'$T_{att}(x,y) - E_{eff}= 18.5 keV$')
fig.colorbar(im1,ax=ax1)
ax2 = fig.add_subplot(232)
im2 = ax2.imshow(thickness_phase, cmap='gray', vmin=0, vmax=3)
ax2.set_title(r'$T_{phase}(x,y) - E_{eff}= 20.5 keV$')
fig.colorbar(im2,ax=ax2)
ax3 = fig.add_subplot(233)
im3=ax3.imshow(thickness_theo, cmap='gray', vmin=0, vmax=3)
ax3.set_title(r'$T_{theo}(x,y)$')
fig.colorbar(im3,ax=ax3)
ax4 = fig.add_subplot(234)
im4=ax4.imshow(thickness_abs-thickness_theo, cmap='hot', vmin=-0.8, vmax=0.8)#, vmin=-10, vmax=4)
ax4.set_title(r'$T_{att}(x,y) - T_{theo}(x,y)$')
fig.colorbar(im4,ax=ax4)
ax5 = fig.add_subplot(235)
im5=ax5.imshow(thickness_phase - thickness_theo, cmap='hot', vmin=-0.8, vmax=0.8)#, vmin=-10, vmax=4)
ax5.set_title(r'$T_{phase}(x,y) - T_{theo}(x,y)$')
fig.colorbar(im5,ax=ax5)
ax6 = fig.add_subplot(236)
ax6.plot(np.mean(thickness_theo[int((299/16)*num_dith_x)-2:int((299/16)*num_dith_x)+3,:], 0), '-k', label='Theo', lw=4)
ax6.plot(np.mean(thickness_phase[int((299/16)*num_dith_x)-2:int((299/16)*num_dith_x)+3,:], 0),  'oc', label='Phase', ms=3)
ax6.plot(np.mean(thickness_abs[int((299/16)*num_dith_x)-2:int((299/16)*num_dith_x)+3,:], 0),  'oy', label='Atten', ms=3)
ax6.set_title('Horizontal profile')
ax6.legend()
        
#%%

t16a, t16p, t16t, x16 = calculate_thickness(16, 16)
t8a, t8p, t8t, x8 = calculate_thickness(8, 8)
t4a, t4p, t4t, x4 = calculate_thickness(4, 4)
t2a, t2p, t2t, x2 = calculate_thickness(2, 2)
t1a, t1p, t1t, x1 = calculate_thickness(1, 1)




#%%
plt.figure()
plt.plot(x16, np.mean(t16t[int((299/16)*num_dith_x)-2:int((299/16)*num_dith_x)+3,:], 0), '-k', label='Theo', lw=2)
plt.scatter(x16, np.mean(t16p[int((299/16)*num_dith_x)-2:int((299/16)*num_dith_x)+3,:], 0), label='16x16', s=3)
plt.scatter(x8, np.mean(t8p[int((299/16)*8)-2:int((299/16)*8)+3,:], 0), label='8x8', s=3)
plt.scatter(x4, np.mean(t4p[int((299/16)*4)-2:int((299/16)*4)+3,:], 0), label='4x4', s=3)
plt.scatter(x2, np.mean(t2p[int((299/16)*2)-2:int((299/16)*2)+3,:], 0), label='2x2', s=3)
plt.scatter(x1, np.mean(t1p[int((299/16)*1)-2:int((299/16)*1)+3,:], 0), label='1x1', s=3)
plt.xlabel('Distance (mm)')
plt.ylabel('Thickness (mm)')
plt.title('Sampling comparison - $T_{phase}(x,y)$')
plt.legend()

plt.figure()
plt.plot(x16, np.mean(t16t[int((299/16)*num_dith_x)-2:int((299/16)*num_dith_x)+3,:], 0), '-k', label='Theo', lw=2)
plt.scatter(x16, np.mean(t16a[int((299/16)*num_dith_x)-2:int((299/16)*num_dith_x)+3,:], 0), label='16x16', s=3)
plt.scatter(x8, np.mean(t8a[int((299/16)*8)-2:int((299/16)*8)+3,:], 0), label='8x8', s=3)
plt.scatter(x4, np.mean(t4a[int((299/16)*4)-2:int((299/16)*4)+3,:], 0), label='4x4', s=3)
plt.scatter(x2, np.mean(t2a[int((299/16)*2)-2:int((299/16)*2)+3,:], 0), label='2x2', s=3)
plt.scatter(x1, np.mean(t1a[int((299/16)*1)-2:int((299/16)*1)+3,:], 0), label='1x1', s=3)
plt.xlabel('Distance (mm)')
plt.ylabel('Thickness (mm)')
plt.title('Sampling comparison - $T_{att}(x,y)$')
plt.legend()


fig = plt.figure(figsize=(20,8))
ax1 = fig.add_subplot(251)
im1=ax1.imshow(t16a, cmap='gray', vmin=0, vmax=3)
ax1.set_title(r'$T_{att}(x,y)$ - 16x16')
fig.colorbar(im1,ax=ax1)
ax2 = fig.add_subplot(252)
im2 = ax2.imshow(t8a, cmap='gray', vmin=0, vmax=3)
ax2.set_title(r'$T_{att}(x,y)$ - 8x8')
fig.colorbar(im2,ax=ax2)
ax3 = fig.add_subplot(253)
im3=ax3.imshow(t4a, cmap='gray', vmin=0, vmax=3)
ax3.set_title(r'$T_{att}(x,y)$ - 4x4')
fig.colorbar(im3,ax=ax3)
ax4 = fig.add_subplot(254)
im4=ax4.imshow(t2a, cmap='gray', vmin=0, vmax=3)#, vmin=-10, vmax=4)
ax4.set_title(r'$T_{att}(x,y)$ - 2x2')
fig.colorbar(im4,ax=ax4)
ax5 = fig.add_subplot(255)
im5=ax5.imshow(t1a, cmap='gray', vmin=0, vmax=3)#, vmin=-10, vmax=4)
ax5.set_title(r'$T_{att}(x,y)$ - 1x1')
fig.colorbar(im5,ax=ax5)
ax6 = fig.add_subplot(256)
im6=ax6.imshow(t16a-t16t, cmap='hot', vmin=-0.8, vmax=0.8)
ax6.set_title(r'$T_{att}(x,y) - T_{theo}(x,y)$ - 16x16')
fig.colorbar(im6,ax=ax6)
ax7 = fig.add_subplot(257)
im7 = ax7.imshow(t8a-t8t, cmap='hot', vmin=-0.8, vmax=0.8)
ax7.set_title(r'$T_{att}(x,y) - T_{theo}(x,y)$ - 8x8')
fig.colorbar(im7,ax=ax7)
ax8 = fig.add_subplot(258)
im8=ax8.imshow(t4a-t4t, cmap='hot', vmin=-0.8, vmax=0.8)
ax8.set_title(r'$T_{att}(x,y) - T_{theo}(x,y)$ - 4x4')
fig.colorbar(im8,ax=ax8)
ax9 = fig.add_subplot(259)
im9=ax9.imshow(t2a-t2t, cmap='hot', vmin=-0.8, vmax=0.8)#, vmin=-10, vmax=4)
ax9.set_title(r'$T_{att}(x,y) - T_{theo}(x,y)$ - 2x2')
fig.colorbar(im9,ax=ax9)
ax10 = fig.add_subplot(2,5,10)
im10=ax10.imshow(t1a-t1t, cmap='hot', vmin=-0.8, vmax=0.8)#, vmin=-10, vmax=4)
ax10.set_title(r'$T_{att}(x,y) - T_{theo}(x,y)$ - 1x1')
fig.colorbar(im10,ax=ax10)

fig = plt.figure(figsize=(24,8))
ax1 = fig.add_subplot(251)
im1=ax1.imshow(t16p, cmap='gray', vmin=0, vmax=3)
ax1.set_title(r'$T_{phase}(x,y)$ - 16x16')
fig.colorbar(im1,ax=ax1)
ax2 = fig.add_subplot(252)
im2 = ax2.imshow(t8p, cmap='gray', vmin=0, vmax=3)
ax2.set_title(r'$T_{phase}(x,y)$ - 8x8')
fig.colorbar(im2,ax=ax2)
ax3 = fig.add_subplot(253)
im3=ax3.imshow(t4p, cmap='gray', vmin=0, vmax=3)
ax3.set_title(r'$T_{phase}(x,y)$ - 4x4')
fig.colorbar(im3,ax=ax3)
ax4 = fig.add_subplot(254)
im4=ax4.imshow(t2p, cmap='gray', vmin=0, vmax=3)#, vmin=-10, vmax=4)
ax4.set_title(r'$T_{phase}(x,y)$ - 2x2')
fig.colorbar(im4,ax=ax4)
ax5 = fig.add_subplot(255)
im5=ax5.imshow(t1p, cmap='gray', vmin=0, vmax=3)#, vmin=-10, vmax=4)
ax5.set_title(r'$T_{phase}(x,y)$ - 1x1')
fig.colorbar(im5,ax=ax5)
ax6 = fig.add_subplot(256)
im6=ax6.imshow(t16p-t16t, cmap='hot', vmin=-0.8, vmax=0.8)
ax6.set_title(r'$T_{phase}(x,y) - T_{theo}(x,y)$ - 16x16')
fig.colorbar(im6,ax=ax6)
ax7 = fig.add_subplot(257)
im7 = ax7.imshow(t8p-t8t, cmap='hot', vmin=-0.8, vmax=0.8)
ax7.set_title(r'$T_{phase}(x,y) - T_{theo}(x,y)$ - 8x8')
fig.colorbar(im7,ax=ax7)
ax8 = fig.add_subplot(258)
im8=ax8.imshow(t4p-t4t, cmap='hot', vmin=-0.8, vmax=0.8)
ax8.set_title(r'$T_{phase}(x,y) - T_{theo}(x,y)$ - 4x4')
fig.colorbar(im8,ax=ax8)
ax9 = fig.add_subplot(259)
im9=ax9.imshow(t2p-t2t, cmap='hot', vmin=-0.8, vmax=0.8)#, vmin=-10, vmax=4)
ax9.set_title(r'$T_{phase}(x,y) - T_{theo}(x,y)$ - 2x2')
fig.colorbar(im9,ax=ax9)
ax10 = fig.add_subplot(2,5,10)
im10=ax10.imshow(t1p-t1t, cmap='hot', vmin=-0.8, vmax=0.8)#, vmin=-10, vmax=4)
ax10.set_title(r'$T_{phase}(x,y) - T_{theo}(x,y)$ - 1x1')
fig.colorbar(im10,ax=ax10)

    
#plt.figure()
#plt.subplot(121);plt.plot(thickness_abs[19*num_dith_y, :]);plt.title('Thickness (abs)')
#plt.subplot(122);plt.plot(thickness_phase[19*num_dith_y, :]);plt.title('Thickness (phase)')

#x16x16 = (np.arange(nx) * period/num_dith_x)
#th16x16_abs=thickness_abs
#th16x16_phase=thickness_phase
#


#%%

# plt.figure();
# plt.title('Thickness (phase)')
# plt.scatter(x1x1, th1x1_phase[19*1, :], s=4, label='1x1');
# plt.scatter(x2x2, th2x2_phase[19*2, :], s=4, label='2x2');
# plt.scatter(x4x4, th4x4_phase[19*4, :], s=4, label='4x4');
# plt.scatter(x8x8, th8x8_phase[19*8, :], s=4, label='8x8');
# plt.scatter(x16x16, th16x16_phase[19*16, :], s=4, label='16x16')
# plt.legend()

# plt.figure();
# plt.title('Thickness (attenuation)')
# plt.scatter(x1x1, th1x1_abs[19*1, :], s=4, label='1x1');
# plt.scatter(x2x2, th2x2_abs[19*2, :], s=4, label='2x2');
# plt.scatter(x4x4, th4x4_abs[19*4, :], s=4, label='4x4');
# plt.scatter(x8x8, th8x8_abs[19*8, :], s=4, label='8x8');
# plt.scatter(x16x16, th16x16_abs[19*16, :], s=4, label='16x16')
# plt.legend()


# #%%
# a=[]
# for i in range(576):
#     a.append(np.sum(thickness_phase[:,i]))
    
# print(np.argmax(a))
