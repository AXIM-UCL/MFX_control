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

path = r'D:\Data\22_01_27\test\\'
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
numTest = 1000


#Start Hamamatsu
print('Starting Hamamatsu')
hamamatsu_functions.HM_init()
hamamatsu_functions.HM_setExposureTime(expTime)
print('Hamamatsu initialized')

for i in range(numTest):
    print("Acquiring", i)
    file_name = path+'try_'+str(i)
    hamamatsu_functions.HM_AcquireWaitSave(file_name)
