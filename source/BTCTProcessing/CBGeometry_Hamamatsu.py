# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 11:09:26 2022

@author: Carlos Navarrete-Leon
"""

import numpy as np
import cv2 
import matplotlib.pyplot as plt
from skimage.feature import match_template
import tifffile
from source.BTCTProcessing import tools_geometry
from sklearn.linear_model import LinearRegression


# =============================================================================
# This script calculates the geometry of a cone-beam system. For such purpose,
# it tracks small ball bearings along different projections. The ball is tracked 
# by template matching first, then thresholding is used in a
# window around the pixel with greatest cross correlation. And then the center
# of the sphere is found with the center of mass.
# After the trajectory is reconstructed (ellipses), the method developed by 
# K. Yang et al. A geometric calibration method for cone beam CT systems. 
# Medical Physics. 33, 1695–1706 (2006) is used. It is modified by fitting an
# ellipse, instead of taking only the data from the projections (see reference).
# =============================================================================

# =============================================================================
# First select the ball window from one of the images, try one in which the
# ball can be clearly seen. Then tracks the ball for a single image to check
# everything is working.
# =============================================================================

path=r'D:\Data\22_02_28\CT_1000proj_abs_calib_phantom_35\FFC\\'

save=0

n_sphs=8

full_img=np.zeros((2340,2368))

file_name=path+'ffc_000250.tif'
ffc=np.flipud(tifffile.imread(file_name))
ffc_blur=cv2.GaussianBlur(ffc,(5,5),0)
sz=49;sty=1218;stx=1274 #angle10_2 aft crash

ball_window = ffc_blur[sty:sty+sz, stx:stx+sz] 
h, w = ball_window.shape
pad_h, pad_w = (int((h-1)/2), int((w-1)/2))


plt.imshow(ball_window)

win_size=25
N_proj=1000
angle=250
file_name=path+'ffc_000'+str(angle)+'.tif'
ffc=np.flipud(tifffile.imread(file_name))
ffc_blur=cv2.GaussianBlur(ffc,(5,5),0)
#ffc_blur = cv2.warpAffine(ffc_blur, M_rot, (1024, 402))

ny, nx = ffc.shape
x = np.linspace(0, nx-1, nx)
y = np.linspace(0, ny-1, ny)
xv, yv = np.meshgrid(x, y)

#ylims is to separate the images according to the number of spheres
ylims=[500, 700, 843, 990, 1140, 1325, 1520, 1680, 1900]

#ylims=[980, 1150, 1330, 1520]
yloc=[];xloc=[];rs=[]
for i in range(n_sphs):
    sub_ffc=ffc_blur[ylims[i]:ylims[i+1],:]
    ffc_padded=np.pad(sub_ffc, (pad_h, pad_w), constant_values=np.mean(ffc_blur[10:30, 10:30]), mode='constant')
    result = cv2.matchTemplate(ffc_padded, ball_window, method=cv2.TM_CCORR_NORMED)
    result=np.nan_to_num(result, 0)
    plt.imshow(result)

    #result=cv2.GaussianBlur(result,(5,5),0)
    indmax=np.argmax(result)
    ymax, xmax=np.unravel_index(indmax, result.shape)
    ymax=ymax+ylims[i]
    xmax=xmax
    window=ffc_blur[ymax-win_size:ymax+win_size, xmax-win_size:xmax+win_size]
    window=-np.log(window).astype(np.float32)
    sub_xv, sub_yv = (xv[ymax-win_size:ymax+win_size, xmax-win_size:xmax+win_size], yv[ymax-win_size:ymax+win_size, xmax-win_size:xmax+win_size])
    #window=(255*window/np.amax(window)).astype(np.uint8)
    _,th = cv2.threshold(window,0.3,0, cv2.THRESH_TOZERO)
    x_cen=np.sum(sub_xv*th)/np.sum(th)
    y_cen=np.sum(sub_yv*th)/np.sum(th)
    xloc.append(x_cen)
    yloc.append(y_cen)

#Plots the result
fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure
ax.imshow(ffc, vmin=0)#, vmax=20000)
ax.autoscale(False)
ax.plot(xloc, yloc, 'r.')
#%%
# =============================================================================
# Now do the same tracking process but with all projections to construct the
# ellipses. 
# =============================================================================

angles=np.linspace(0, N_proj, N_proj, endpoint=False).astype('int')
x_pos=np.zeros((len(angles), n_sphs))
y_pos=np.zeros((len(angles), n_sphs))
full_img=np.zeros((2340,2368))
ind=0
for angle in angles:
    file_name=path+'ffc_000'+str(angle)+'.tif'
    ffc=np.flipud(tifffile.imread(file_name))
    #T = np.float32([[1, 0, -x_disp[ind]], [0, 1, -y_disp[ind]]])
    #ffc = cv2.warpAffine(ffc, T, (1024, 402))
    ffc_blur=cv2.GaussianBlur(ffc,(7,7),0)
    #ffc_blur = cv2.warpAffine(ffc_blur, M_rot, (1024, 402))
    full_img+=ffc_blur
    yloc=[];xloc=[]
    
    for i in range(n_sphs):
        sub_ffc=ffc_blur[ylims[i]:ylims[i+1],:]
        result = match_template(sub_ffc, ball_window, pad_input=True)
        indmax=np.argmax(result)
        ymax, xmax=np.unravel_index(indmax, sub_ffc.shape)
        ymax=ymax+ylims[i]
        xmax=xmax
        window=ffc_blur[ymax-win_size:ymax+win_size, xmax-win_size:xmax+win_size]
        window=-np.log(window).astype(np.float32)
        sub_xv, sub_yv = (xv[ymax-win_size:ymax+win_size, xmax-win_size:xmax+win_size], yv[ymax-win_size:ymax+win_size, xmax-win_size:xmax+win_size])
        #window=(255*window/np.amax(window)).astype(np.uint8)
        _,th = cv2.threshold(window,0.3,0, cv2.THRESH_TOZERO)
        x_cen=np.sum(sub_xv*th)/np.sum(th)
        y_cen=np.sum(sub_yv*th)/np.sum(th)
        yloc.append(y_cen)
        xloc.append(x_cen)
    
    yloc=np.array(yloc);xloc=np.array(xloc)
    x_pos[ind,:]=xloc
    y_pos[ind,:]=yloc
    ind+=1

xtop=x_pos[:,0]; ytop=y_pos[:,0]
xmed=x_pos[:,3]; ymed=y_pos[:,3]
xbot=x_pos[:,6]; ybot=y_pos[:,6]


#=============================================================================
# Get the key points and the geometry parameters 
#=============================================================================

## Get the centers of the ellipses
us_dist_stack=np.zeros((n_sphs, 5))
vs_dist_stack=np.zeros((n_sphs, 5))

types=[0,0,0,1,1,1,1,1]

## Shows the tracking of the three spheres
fig = plt.figure(figsize=(8,30))

for i in range(n_sphs):
    us, vs, ang = tools_geometry.get_points_dists(x_pos[:,i], y_pos[:,i], N_proj, type=types[i])
    us_dist_stack[i,:]=us
    vs_dist_stack[i,:]=vs
    if(i==1):
        angle1=ang
    if(i==6):
        angle2=ang

    ax = fig.add_subplot(n_sphs, 1, i+1)
    sc=ax.scatter(x_pos[:,i], y_pos[:,i], c=angles, cmap='winter', label='Data', zorder=1,edgecolors='k')
    cbar=plt.colorbar(sc)
    cbar.ax.set_ylabel('Angle')
    ax.plot(us, vs, 'ro', markeredgecolor='k', label='Key points')
    ax.invert_yaxis()
    
    
param_dist=tools_geometry.calculate_parameters_Yang(us_dist_stack, vs_dist_stack, angle1, angle2, l=12.29, pix_size=0.05)

print('(n (deg), u0, v0, R_fd (mm), R_fi (mm))' , param_dist)

# =============================================================================
# Now show the results
# =============================================================================

# All projections added
fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure
ax.imshow(full_img, vmin=80)
ax.autoscale(False)
ax.set_title('All projections added')
    
    
# #Shows the tracking of the three spheres
# fig = plt.figure(figsize=(8,15))
# ax1 = fig.add_subplot(311);ax1.set_title('Top ellipse')
# sc1=ax1.scatter(xtop, ytop, c=angles, cmap='winter', label='Data', zorder=1,edgecolors='k')
# cbar=plt.colorbar(sc1)
# cbar.ax.set_ylabel('Angle')
# ax1.plot(us_top_dist, vs_top_dist, 'ro', markeredgecolor='k', label='Key points')
# ax1.invert_yaxis()
# #plt.xlim(80, 420)
# #plt.ylim(55.5, 60.5)
# plt.legend(loc=1)
# ax2 = fig.add_subplot(312);ax2.set_title('Central ellipse')
# sc2=ax2.scatter(xmed, ymed, c=angles, cmap='winter', label='Data', zorder=1, edgecolors='k')
# #plt.xlim(80, 420)
# #plt.ylim(214, 219)
# cbar2=plt.colorbar(sc2)
# cbar2.ax.set_ylabel('Angle')
# ax2.plot(us_med_dist, vs_med_dist, 'ro', markeredgecolor='k', label='Key points')
# ax2.invert_yaxis()
# plt.legend(loc=1)
# ax3 = fig.add_subplot(313);ax3.set_title('Central ellipse')
# sc3=ax3.scatter(xbot, ybot, c=angles, cmap='winter', label='Data', zorder=1, edgecolors='k')
# cbar3=plt.colorbar(sc3)
# cbar3.ax.set_ylabel('Angle')
# ax3.plot(us_bot_dist, vs_bot_dist, 'ro', markeredgecolor='k', label='Key points')
# ax3.invert_yaxis()
# plt.legend(loc=1)
# #plt.xlim(80, 420)
#plt.ylim(331, 336)
