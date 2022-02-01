# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:20:40 2021

@author: Carlos Navarrete-Leon
"""
import numpy as np
from source.BTCTProcessing import fit_ellipse
from sklearn.linear_model import LinearRegression
from numpy.linalg import eig, inv, svd
from math import atan2

# Calculates the centers of the ellipse using the determinant method.
# For this, it needs the four key points in the ellipse (us and vs).
# See K. Yang et al. A geometric calibration method for cone beam CT systems. 
# Medical Physics. 33, 1695–1706 (2006) Section D page 1699.

def calculate_centers(us, vs):
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

# Calculates the centers of the ellipse by using points 180 degrees apart.
# It calculates some quantities and then performs a linear fit which gives the 
# center of the ellipse.
# See Frédéric Noo et al 2000 Phys. Med. Biol. 45 3489. Section 3.2 page 3495.

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
        
# This function builds a vector with the 5 key points needed for Yang's method to estimate 
# geometry paramters. For that, it estimates the maximum and minimum distances
# between points 180 degrees apart. The center point could be obtained through the 
# determinant or the fit method (see methods above).
# See Fig 6, page 1698 for info on the '5 key points' .
# K. Yang et al. A geometric calibration method for cone beam CT systems. 
# Medical Physics. 33, 1695–1706 (2006)  
    
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

# This function builds a vector with the 5 key points needed for Yang's method to estimate 
# geometry paramters. For that, it fits an ellipse and finds the mayor and minor axes.
# See Fig 6, page 1698 for info on the '5 key points' .
# K. Yang et al. A geometric calibration method for cone beam CT systems. 
# Medical Physics. 33, 1695–1706 (2006)  

def get_points_fit(xs, ys, type=0):
    
    # Fit ellipse
    width1, height1, cx1, cy1, phi1 = fit_ellipse(xs, ys)
    
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

# This function finds the parameters, see:
# K. Yang et al. A geometric calibration method for cone beam CT systems. 
# Medical Physics. 33, 1695–1706 (2006) 

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
    
#######-------- Stuff to fit the ellipse -----------############
    
def __fit_ellipse(x, y):
    x, y = x[:, np.newaxis], y[:, np.newaxis]
    D = np.hstack((x * x, x * y, y * y, x, y, np.ones_like(x)))
    S, C = np.dot(D.T, D), np.zeros([6, 6])
    C[0, 2], C[2, 0], C[1, 1] = 2, 2, -1
    U, s, V = svd(np.dot(inv(S), C))
    a = U[:, 0]
    return a

def ellipse_center(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    num = b * b - a * c
    x0 = (c * d - b * f) / num
    y0 = (a * f - b * d) / num
    return np.array([x0, y0])

def ellipse_axis_length(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    up = 2 * (a * f * f + c * d * d + g * b * b - 2 * b * d * f - a * c * g)
    down1 = (b * b - a * c) * (
        (c - a) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a)
    )
    down2 = (b * b - a * c) * (
        (a - c) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a)
    )
    res1 = np.sqrt(up / down1)
    res2 = np.sqrt(up / down2)
    return np.array([res1, res2])

def ellipse_angle_of_rotation(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    return atan2(2 * b, (a - c)) / 2

def fit_ellipse(x, y):
    """@brief fit an ellipse to supplied data points: the 5 params
        returned are:
        M - major axis length
        m - minor axis length
        cx - ellipse centre (x coord.)
        cy - ellipse centre (y coord.)
        phi - rotation angle of ellipse bounding box
    @param x first coordinate of points to fit (array)
    @param y second coord. of points to fit (array)
    """
    a = __fit_ellipse(x, y)
    centre = ellipse_center(a)
    phi = ellipse_angle_of_rotation(a)
    M, m = ellipse_axis_length(a)
    # assert that the major axix M > minor axis m
    if m > M:
        M, m = m, M
    # ensure the angle is betwen 0 and 2*pi
    phi -= 2 * np.pi * int(phi / (2 * np.pi))
    return [M, m, centre[0], centre[1], phi]
