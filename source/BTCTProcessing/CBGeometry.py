
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 16:26:20 2021

@author: Carlos Navarrete-Leon
"""

import numpy as np
import cv2 
import matplotlib.pyplot as plt
from skimage.feature import match_template
import tifffile
from source.BTCTProcessing import fit_ellipse
from sklearn.linear_model import LinearRegression

# =============================================================================
# This script calculates the geometry of a cone-beam system. For such purpose,
# it tracks small ball bearings along different projections. The ball is tracked 
# by template matching first, then the otsu threshold is determined in a
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

path=r'C:\Data\21_10_25\CT_100proj_abs_calib_phantom\FFC\\'

save=0

n_sphs=3

full_img=np.zeros((402,512))

file_name=path+'ffc_00025.tif'
ffc=tifffile.imread(file_name)
ffc_blur=cv2.GaussianBlur(ffc,(5,5),0)
#sz=43;sty=138;stx=264 #angle0 
#sz=43;sty=156;stx=314 #angle40
#sz=43;sty=159;stx=321 #angle45
#sz=43;sty=161;stx=329 #angle0_2
#sz=43;sty=164;stx=335 #angle5_2
#sz=43;sty=222;stx=266 #angle10_2
sz=43;sty=195;stx=269 #angle10_2 aft crash

ball_window = ffc_blur[sty:sty+sz, stx:stx+sz] 
h, w = ball_window.shape
pad_h, pad_w = (int((h-1)/2), int((w-1)/2))

win_size=25
N_proj=100
angle=25
file_name=path+'ffc_000'+str(angle)+'.tif'
ffc=tifffile.imread(file_name)
ffc_blur=cv2.GaussianBlur(ffc,(5,5),0)
#ffc_blur = cv2.warpAffine(ffc_blur, M_rot, (1024, 402))

ny, nx = ffc.shape
x = np.linspace(0, nx-1, nx)
y = np.linspace(0, ny-1, ny)
xv, yv = np.meshgrid(x, y)

#ylims is to separate the images according to the number of spheres
ylims=[0, 150, 300, 402]
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
full_img=np.zeros((402,512))
ind=0
for angle in angles:
    file_name=path+'ffc_000'+str(angle)+'.tif'
    ffc=tifffile.imread(file_name)
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
xmed=x_pos[:,1]; ymed=y_pos[:,1]
xbot=x_pos[:,2]; ybot=y_pos[:,2]
#ybot[343]=(ybot[344]+ybot[342])/2

# =============================================================================
# Now show the tracking of the sphere and save the results
# =============================================================================

fig=plt.figure(figsize=(10,7))
ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure
ax.imshow(full_img)#, vmin=750, vmax=900)
ax.autoscale(False)
# ax.plot(xtop, ytop, 'w.', markersize=3)
# ax.plot(xmed, ymed, 'b.', markersize=3)
# ax.plot(xbot, ybot, 'r.', markersize=3)
ax.set_title('Spheres trajectory')

fig = plt.figure(figsize=(8,14))
ax1 = fig.add_subplot(311);ax1.set_title('Top ellipse')
sc1=ax1.scatter(xtop, ytop, c=angles, cmap='winter', label='Data', zorder=1,edgecolors='k')
cbar=plt.colorbar(sc1)
cbar.ax.set_ylabel('Angle')
ax1.invert_yaxis()
#ax1.set_ylim((73, 78))
plt.legend()
ax2 = fig.add_subplot(312);ax2.set_title('Central ellipse')
sc2=ax2.scatter(xmed, ymed, c=angles, cmap='winter', label='Data', zorder=1, edgecolors='k')
cbar2=plt.colorbar(sc2)
cbar2.ax.set_ylabel('Angle')
ax2.invert_yaxis()
#ax2.set_ylim((233, 235))
plt.legend()
ax3 = fig.add_subplot(313);ax3.set_title('Central ellipse')
sc3=ax3.scatter(xbot, ybot, c=angles, cmap='winter', label='Data', zorder=1, edgecolors='k')
cbar3=plt.colorbar(sc3)
cbar3.ax.set_ylabel('Angle')
ax3.invert_yaxis()
#ax3.set_ylim((349, 355))
plt.legend()

#%%
def calculate_center(us, vs):
    u11n = np.linalg.det(np.array([[us[1],vs[1]], [us[2],vs[2]]]))
    u12n=us[1]-us[2]
    u21n = np.linalg.det(np.array([[us[3],vs[3]], [us[4],vs[4]]]))
    u22n=us[3]-us[4]
    
    den=np.array([[us[1]-us[2], vs[1]-vs[2]],[us[3]-us[4], vs[3]-vs[4]]])
    
    us0=np.linalg.det(np.array([[u11n, u12n],[u21n, u22n]]))/np.linalg.det(den)
    
    v11n=u11n
    v12n=vs[1]-vs[2]
    v21n=u21n
    v22n=vs[3]-vs[4]
    
    vs0=np.linalg.det(np.array([[v11n, v12n],[v21n, v22n]]))/np.linalg.det(den)
    
    return us0, vs0

def calculate_center_mean(xs, ys, N_proj):
    Yi=[];Xi=[]
    
    for i in range(int(N_proj/2)):
        Yi.append((ys[i]*xs[i+int(N_proj/2)]-ys[i+int(N_proj/2)]*xs[i])/(xs[i+int(N_proj/2)]-xs[i]))
        Xi.append((ys[i]-ys[i+int(N_proj/2)])/(xs[i+int(N_proj/2)]-xs[i]))
        
    Xi=np.array(Xi).reshape(-1,1)
    Yi=np.array(Yi).reshape(-1,1)

    reg = LinearRegression().fit(Xi, Yi)
    v0=reg.intercept_[0]
    u0=reg.coef_[0][0]
    
    return u0,v0
        
     
def get_points_dists(xs, ys, N_proj, type=0):
    angles=np.arange(1, N_proj, 1)
    dist_top=[]
    
    half=int(N_proj/2)
    
    for i in range(half):
        x0=xs[i];y0=ys[i]
        x180=xs[i+half];y180=ys[i+half]
        dist_top.append(np.sqrt((y180-y0)**2+(x180-x0)**2))
        
    dist_top=np.array(dist_top)
    armax=np.argmax(dist_top)
    armin=np.argmin(dist_top)
    
    us=[0]; vs=[0]
    if(type==0):
        if(ys[armin+half]<ys[armin]):
            us.append(xs[armin+half])
            us.append(xs[armin])
            vs.append(ys[armin+half])
            vs.append(ys[armin])
        else:
            us.append(xs[armin])
            us.append(xs[armin+half])
            vs.append(ys[armin])
            vs.append(ys[armin+half])
        if(xs[armax+half]<xs[armax]):
            us.append(xs[armax+half])
            us.append(xs[armax])
            vs.append(ys[armax+half])
            vs.append(ys[armax])
        else:
            us.append(xs[armax])
            us.append(xs[armax+half])
            vs.append(ys[armax])
            vs.append(ys[armax+half])    
            
    elif(type==1):
        if(ys[armin+half]>ys[armin]):
            us.append(xs[armin+half])
            us.append(xs[armin])
            vs.append(ys[armin+half])
            vs.append(ys[armin])
        else:
            us.append(xs[armin])
            us.append(xs[armin+half])
            vs.append(ys[armin])
            vs.append(ys[armin+half])
        if(xs[armax+half]<xs[armax]):
            us.append(xs[armax+half])
            us.append(xs[armax])
            vs.append(ys[armax+half])
            vs.append(ys[armax])
        else:
            us.append(xs[armax])
            us.append(xs[armax+half])
            vs.append(ys[armax])
            vs.append(ys[armax+half]) 
    
    #us=[0, xs[armin+half], xs[armin], xs[armax+half], xs[armax]]
    #vs=[0, ys[armin+half], ys[armin], ys[armax+half], ys[armax]]
    #us[0], vs[0]=calculate_center(us, vs)
    us[0], vs[0]=calculate_center_mean(xs, ys, N_proj)
    ang = np.argwhere(xs==us[4])[0][0]
    return us, vs, np.deg2rad(ang)

def get_points_fit(xs, ys, type=0):
    
    # Fit ellipse
    width1, height1, cx1, cy1, phi1 = fit_ellipse.fit_ellipse(xs, ys)
    
    # This has to be checked visually because it depends on location of the sphere.
    # It depends if it is up or down the estimated center. The angles represent the
    # vertex coordinates 
    if(type==0):
        ts1=np.array([np.pi/2, 3*np.pi/2, np.pi, 0]) #A1, A2, A3, A4 (see Figure 7)
    else:
        ts1=np.array([3*np.pi/2, np.pi/2, np.pi, 0]) #A1, A2, A3, A4 (see Figure 7)

    
    # Calculate the 5 key coordinates for the method.
    us=width1*np.cos(ts1)*np.cos(phi1)-height1*np.sin(ts1)*np.sin(phi1)+cx1
    us=np.concatenate((np.array([cx1]), us))
    vs=width1*np.cos(ts1)*np.sin(phi1)+height1*np.sin(ts1)*np.cos(phi1)+cy1
    vs=np.concatenate((np.array([cy1]), vs))
    
    return us, vs

def calculate_parameters_Yang(us_stack, vs_stack, angle1, angle2, l, pix_size=0.062):
    # Fit to extract v0 and R_fd
    Yi=(vs_stack[:,1]-vs_stack[:,2])/(np.sqrt((us_stack[:,3]-us_stack[:,4])**2+(vs_stack[:,3]-vs_stack[:,4])**2))
    Yi=Yi.reshape(-1,1)
    Xi=(vs_stack[:,1]+vs_stack[:,2])/2
    Xi=Xi.reshape(-1,1)
    
    reg = LinearRegression().fit(Yi, Xi)
    v0=reg.intercept_[0]
    R_fd=reg.coef_[0][0]
    
    # fit to extract u0 and the axis rotation around the propagation axis.
    U0=us_stack[:,0].reshape(-1,1)
    V0=vs_stack[:,0].reshape(-1,1)
    
    reg2 = LinearRegression().fit(V0, U0)
    u0=reg2.intercept_[0]+reg2.coef_[0][0]*v0
    n=np.arctan(reg2.coef_[0][0])
    
    d10_20= np.sqrt((us_stack[0,0]-us_stack[2,0])**2+(vs_stack[0,0]-vs_stack[2,0])**2)
    d13_14= np.sqrt((us_stack[0,3]-us_stack[0,4])**2+(vs_stack[0,3]-vs_stack[0,4])**2)
    d23_24= np.sqrt((us_stack[2,3]-us_stack[2,4])**2+(vs_stack[2,3]-vs_stack[2,4])**2)
    
    den=np.sqrt(d10_20**2+(d13_14/2)**2+(d23_24/2)**2-(d13_14*d23_24*np.cos(angle1-angle2)/2))
    l=l/pix_size
    R_fi=l*R_fd/den
    
    return np.rad2deg(n), u0, v0, R_fd*pix_size, R_fi*pix_size

def calculate_parameters_Noo(xs_top, ys_top, xs_bot, ys_bot, N_proj):
    u1,v1=calculate_center_mean(xs_top, ys_top, N_proj)
    u2, v2=calculate_center_mean(xs_bot, ys_bot, N_proj)
    n=np.arctan((u1-u2)/(v1-v2))
    us_top=xs_top*np.cos(n)-ys_top*np.sin(n); us_bot=xs_bot*np.cos(n)-ys_bot*np.sin(n)
    vs_top=xs_top*np.sin(n)+ys_top*np.cos(n); vs_bot=xs_bot*np.sin(n)+ys_bot*np.cos(n)
    
    us=np.stack((us_top, us_bot))
    vs=np.stack((vs_top, vs_bot))
    
    a=1
    
#     print(np.sqrt((us_stack[:,1]-us_stack[:,2])**2+(vs_stack[:,3]-vs_stack[:,4])**2))
    
#     up_top=xs_top*np.cos(n) - ys_top*np.sin(n); vp_top=xs_top*np.sin(n) + ys_top*np.cos(n)
#     up_bot=xs_bot*np.cos(n) - ys_bot*np.sin(n); vp_bot=xs_bot*np.sin(n) + ys_bot*np.cos(n)
    
    
    
    
#%%

us_top_dist, vs_top_dist, angle1=get_points_dists(xtop, ytop, N_proj, type=0)
#us_top_fit, vs_top_fit=get_points_fit(x_top, y_top, type=0)

us_med_dist, vs_med_dist, an=get_points_dists(xmed, ymed, N_proj, type=0)
#us_med_fit, vs_med_fit=get_points_fit(x_med, y_med, type=0)

us_bot_dist, vs_bot_dist, angle2=get_points_dists(xbot, ybot, N_proj, type=1)
#us_bot_fit, vs_bot_fit=get_points_fit(x_bot, y_bot, type=1)

us_dist_stack=np.stack((us_top_dist, us_med_dist, us_bot_dist))
vs_dist_stack=np.stack((vs_top_dist, vs_med_dist, vs_bot_dist))


param_dist=calculate_parameters_Yang(us_dist_stack, vs_dist_stack, angle1, angle2, l=3.72)
param_Noo=calculate_parameters_Noo(xtop, ytop, xbot, ybot, N_proj)

print('(n, u0, v0, R_fd (mm), R_fi (mm))' , param_dist)
#print('(n, u0, v0, R_fd (mm))', param_fit)

fig = plt.figure(figsize=(8,15))
ax1 = fig.add_subplot(311);ax1.set_title('Top ellipse')
sc1=ax1.scatter(xtop, ytop, c=angles, cmap='winter', label='Data', zorder=1,edgecolors='k')
cbar=plt.colorbar(sc1)
cbar.ax.set_ylabel('Angle')
ax1.plot(us_top_dist, vs_top_dist, 'ro', markeredgecolor='k', label='Key points')
#ax1.plot(us_top_fit, vs_top_fit, 'yo', markeredgecolor='k', label='Fit method')
ax1.invert_yaxis()
plt.legend(loc=1)
ax2 = fig.add_subplot(312);ax2.set_title('Central ellipse')
sc2=ax2.scatter(xmed, ymed, c=angles, cmap='winter', label='Data', zorder=1, edgecolors='k')
cbar2=plt.colorbar(sc2)
cbar2.ax.set_ylabel('Angle')
ax2.plot(us_med_dist, vs_med_dist, 'ro', markeredgecolor='k', label='Key points')
#ax2.plot(us_med_fit, vs_med_fit, 'yo', markeredgecolor='k', label='Fit method')
ax2.invert_yaxis()
plt.legend(loc=1)
ax3 = fig.add_subplot(313);ax3.set_title('Central ellipse')
sc3=ax3.scatter(xbot, ybot, c=angles, cmap='winter', label='Data', zorder=1, edgecolors='k')
cbar3=plt.colorbar(sc3)
cbar3.ax.set_ylabel('Angle')
ax3.plot(us_bot_dist, vs_bot_dist, 'ro', markeredgecolor='k', label='Key points')
#ax3.plot(us_bot_fit, vs_bot_fit, 'yo', markeredgecolor='k', label='Fit method')
ax3.invert_yaxis()
plt.legend(loc=1)

fig = plt.figure(figsize=(8,10))
ax1 = fig.add_subplot(211);ax1.set_title('Top ellipse')
sc1=ax1.scatter(xtop, ytop, c=angles, cmap='winter', label='Data', zorder=1,edgecolors='k')
cbar=plt.colorbar(sc1)
cbar.ax.set_ylabel('Angle')
#ellipse = Ellipse(xy=(cx1, cy1), width=2*width1, height=2*height1, angle=np.rad2deg(phi1),
 #               edgecolor='gray', fc='None', lw=2, label='Fit', zorder = 2)
#ax1.add_patch(ellipse)
ax1.plot(us_top_dist, vs_top_dist, 'ro', markeredgecolor='k', label='Dist method')
#ax1.plot(us_top_fit, vs_top_fit, 'yo', markeredgecolor='k', label='Fit method')

ax1.invert_yaxis()
plt.legend(loc=1)
ax2 = fig.add_subplot(212);ax2.set_title('Bottom ellipse')
sc2=ax2.scatter(xbot, ybot, c=angles, cmap='winter', label='Data', zorder=1, edgecolors='k')
cbar2=plt.colorbar(sc2)
cbar2.ax.set_ylabel('Angle')
#ellipse2 = Ellipse(xy=(cx2, cy2), width=2*width2, height=2*height2, angle=np.rad2deg(phi2),
 #               edgecolor='gray', fc='None', lw=2, label='Fit', zorder = 2)
#ax2.add_patch(ellipse2)
ax2.plot(us_bot_dist, vs_bot_dist, 'ro', markeredgecolor='k', label='Dist method')
#ax2.plot(us_bot_fit, vs_bot_fit, 'yo', markeredgecolor='k', label='Fit method')
ax2.invert_yaxis()
plt.legend(loc=1)