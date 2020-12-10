# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 16:36:21 2020

@author: XPCI_BT
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import tools_pi
import tools_pixirad
import time

start_time = time.time()


dir_date=r'C:\Data'
folder = '\\08_12_20\\CT_360proj_3\\'
path=dir_date+folder

try:
    out=os.mkdir(path)
except OSError:
    print ("Directory %s already exists" % path)
    
expTime = 1 #integration time for the detector
expNum = 1 #number of images to be acquired
expDelay = 0.1 #time interval between frames$
Loth = 5.0 #low energy threshold (keV)
Hith = 50.0 #high energy threshold (keV)
modeTh = '1COL0'  #must be '1COL0', '1COL1', '2COL'
pixelMode = 'NONPI' # must be 'NONPI' or 'NPI' or 'NPISUM'

flatNum=10
flatInterval=50

#Piezo motors
angles=np.arange(0,361,1)
angle0=0.0
sample_xin=-10.0
sample_xout=10.0

#position in XPS is 54


piezo=tools_pi.connect_piezo()
print('Moving sample to starting point')
tools_pi.move_theta_abs(piezo, angle0)
tools_pi.move_x_abs(piezo, sample_xin)
print('Done')

for angle in angles:
    if(angle%flatInterval==0):
         tools_pi.move_x_abs(piezo, sample_xout)
         file_name = path+'ff_000'+str(angle)+'.dat'
         tools_pixirad.pixirad_acquire_new(file_name, flatNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
         tools_pi.move_x_abs(piezo, sample_xin)
         print('Acquiring FlatField')
    file_name = path+'proj_000'+str(angle)+'.dat'
    tools_pixirad.pixirad_acquire_new(file_name, expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
    tools_pi.move_theta_abs(piezo, angle)


elapsed_time = time.time() - start_time
print('Elapsed time: '+ str(elapsed_time)+ ' s')