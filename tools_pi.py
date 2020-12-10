# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 13:58:03 2020

@author: XPCI_BT
"""

from pipython import GCSDevice, pitools
import numpy as np
import time
import os

def connect_piezo():
    pidevice = GCSDevice ()
    #id is 
    pidevice.ConnectUSB ('119026998')
    pitools.startup(pidevice)
    print('connected and started: {}'.format(pidevice.qIDN().strip()))
    return pidevice

def get_x_sample(pidevice):
    s_out=pidevice.qPOS('3')
    pos=s_out['3']*1000
    print('Sample is at ' +str(pos)+ ' um on x' )
    return pos
    
def get_y_sample(pidevice):
    s_out=pidevice.qPOS('5')
    pos=s_out['5']*1000
    print('Sample is at ' +str(pos)+ ' um on y' )
    return pos
    
def get_z_sample(pidevice):
    s_out=pidevice.qPOS('1')
    pos=s_out['1']*1000
    print('Sample is at ' +str(pos)+ ' um on z' )    
    return pos
    
def get_theta_sample(pidevice):
    s_out=pidevice.qPOS('7')
    pos=s_out['7']
    print('Sample is at ' +str(pos)+ 'deg' )  
    return pos
    
def get_all_sample(pidevice):
    s_out=pidevice.qPOS()
    print(s_out)
    return s_out
    
def move_x_abs(pidevice, x):
    pidevice.MOV('3', x)
    moving=pidevice.IsMoving()['3']
    while moving:
        time.sleep(0.1)
        moving=pidevice.IsMoving()['3']   
    pos=get_x_sample(pidevice)       
    print('Movement done ---- Sample is at ' +str(pos)+ ' um on x')

def move_y_abs(pidevice, y):
    pidevice.MOV('5', y)
    moving=pidevice.IsMoving()['5']
    while moving:
        time.sleep(0.1)
        moving=pidevice.IsMoving()['5']   
    pos=get_y_sample(pidevice)        
    print('Movement done ---- Sample is at ' +str(pos)+ ' um on y')

def move_z_abs(pidevice, z):
    pidevice.MOV('1', z)
    moving=pidevice.IsMoving()['1']
    while moving:
        time.sleep(0.1)
        moving=pidevice.IsMoving()['1']   
    pos=get_z_sample(pidevice)       
    print('Movement done ---- Sample is at ' +str(pos)+ ' um on z')

def move_theta_abs(pidevice, theta):
    pidevice.MOV('7', theta)
    moving=pidevice.IsMoving()['7']
    while moving:
        time.sleep(0.1)
        moving=pidevice.IsMoving()['7']   
    pos=get_theta_sample(pidevice)
    print('Movement done ---- Sample is at ' +str(pos)+ ' deg')

