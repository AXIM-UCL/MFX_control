# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 18:31:07 2021

@author: XPCI_BT
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import tools_pi
import newport_functions
import tools_pixirad
import time
import os
import sys

start_time = time.time()

path=r'C:\Data\\21_06_24\Source_movement_long\\'

# Detector acquisition parameters.

expTime = 1 #integration time for the detector
expNum = 1 #number of images to be acquired
expDelay = 0.1 #time interval between frames$
Loth = 7.0 #low energy threshold (keV)
Hith = 50.0 #high energy threshold (keV)
modeTh = '1COL0'  #must be '1COL0', '1COL1', '2COL'
pixelMode = 'NONPI' # must be 'NONPI' or 'NPI' or 'NPISUM'

#Start pixirad server
print('Starting Pixirad server')
os.chdir("C:\PXRD\PX\PXRD2")
os.system(r"start cmd /k pxrd_server.exe")
    
times=[]

for i in range(587, 18000):
    file_name = path+'ff_000'+str(i)+'.dat'
    tools_pixirad.pixirad_acquire_new(file_name, expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
    times.append(time.time()-start_time)
    time.sleep(20)
    
times=np.array(times)
np.save(path+'times.npy', times)
    
    
