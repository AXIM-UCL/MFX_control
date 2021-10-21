# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 17:09:37 2021

@author: Carlos Navarrete-Leon
"""

import newport_functions
import time
import os

def connect_XPS():
    sockets = newport_functions.NP_init(5)
    #id is 
    print('XPS connected and started')
    return sockets

def get_x_sample_XPS():
    pos=newport_functions.NP_gp(1)    
    pos=pos*1000
    print('Sample is at ' +str(pos)+ ' um on x - XPS' )
    return pos

def get_rot_mask():
    pos=newport_functions.NP_gp(2)    
    print('Mask is at ' +str(pos)+ ' degrees' )
    return pos

def get_x_mask():
    pos=newport_functions.NP_gp(3)    
    pos=pos*1000
    print('Mask is at ' +str(pos)+ ' um on x' )
    return pos

def get_z_mask():
    pos=newport_functions.NP_gp(4)    
    pos=pos*1000
    print('Mask is at ' +str(pos)+ ' um on z' )
    return pos

def get_y_mask():
    pos=newport_functions.NP_gp(5)    
    pos=pos*1000
    print('Mask is at ' +str(pos)+ ' um on y' )
    return pos
    
def get_y_sample(pidevice):
    s_out=pidevice.qPOS('5')
    pos=s_out['5']*1000
    print('Sample is at ' +str(pos)+ ' um on y' )
    return pos
        
def move_xsample_abs(xsample):
    out=newport_functions.NP_ma(1, xsample, wait=1)
    pos=newport_functions.NP_gp(1)*1000
    if(out==1):
        print('Movement done ---- Sample is at ' +str(pos)+ ' um on x - XPS')
    else:
        print('There was an error ---- movement not completed')
    
def move_rotmask_abs(angle):
    out=newport_functions.NP_ma(2, angle, wait=1)
    pos=newport_functions.NP_gp(2) 
    if(out==1):
        print('Movement done ---- Mask is at ' +str(pos)+ ' degrees')
    else:
        print('There was an error ---- movement not completed')

def move_xmask_abs(xmask):
    out=newport_functions.NP_ma(3, xmask, wait=1)
    pos=newport_functions.NP_gp(3)*1000
    if(out==1):
        print('Movement done ---- Mask is at ' +str(pos)+ ' um on x')
    else:
        print('There was an error ---- movement not completed')

def move_zmask_abs(zmask):
    out=newport_functions.NP_ma(4, zmask, wait=1)
    pos=newport_functions.NP_gp(4)*1000
    if(out==1):    
        print('Movement done ---- Mask is at ' +str(pos)+ ' um on z')
    else:
        print('There was an error ---- movement not completed')
    
def move_ymask_abs(ymask):
    out=newport_functions.NP_ma(5, ymask, wait=1)
    pos=newport_functions.NP_gp(5)*1000
    if(out==1):
        print('Movement done ---- Mask is at ' +str(pos)+ ' um on y')
    else:
        print('There was an error ---- movement not completed')
    