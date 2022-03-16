# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 17:40:41 2021
@author: Carlos Navarrete-Leon

This script acquires a simple CT sequence of images in which only the sample
is rotating.
"""

import numpy as np
import os
import time
from source.BTCTDetectors import hamamatsu_functions
from source.BTCTMotors import tools_pi
from source.BTCTMotors import tools_xps

start_time = time.time()


######################## ------------Parameters ------------------#############

path = r'D:\Data\22_02_04\test2\\'
try:
    out=os.mkdir(path)
except OSError:
    print ("Can't create directory %s" % path)
path=path+'RAW\\'
try:
    out=os.mkdir(path)
except OSError:
    print ("Can't create directory %s" % path)
    

expTime = 1 #integration time for the detector
numFrames = 1
numTest = 1000


#Start Hamamatsu
print('Starting Hamamatsu')
hamamatsu_functions.HM_init()
hamamatsu_functions.HM_setExposureTime(expTime)
hamamatsu_functions.HM_SetSequence(numFrames)
print('Hamamatsu initialized')

for i in range(numTest):
    print("Acquiring", i)
    file_name = path+'try_'+str(i)
    hamamatsu_functions.HM_AcquireWaitSave(file_name, save_format=1)
