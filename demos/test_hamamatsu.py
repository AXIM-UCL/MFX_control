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
from source.BTCTDetectors import hamamatsu_functions2 as hf
from source.BTCTMotors import tools_pi
from source.BTCTMotors import tools_xps
import sys

start_time = time.time()

######################## ------------Parameters ------------------#############

#sys.stdout = open("console.txt", "w")

path = r'D:\Data\22_02_16\test_007_debug3\\'
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
#expNum = 100
numTest = 2000

#Start Hamamatsu
print('Starting Hamamatsu')
hf.HM_init()
hf.HM_setExposureTime(expTime)
#hf.HM_SetSequence(expNum)
print('Hamamatsu initialized')

for i in range(numTest):
    print("Acquiring", i)
    file_name = path+'try_'+str(i)
    hf.HM_AcquireWaitSaveTest(file_name, expTime)
    #hf.HM_AcqWaitSaveSequenceTest(file_name, expTime, expNum)
#sys.stdout.close()

