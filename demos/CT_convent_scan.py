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
from source.BTCTDetectors.PEPIPixirad import PEPIPixieIII
from source.BTCTProcessing.PEPITIFFIO import PEPITIFFWriter
from source.BTCTMotors import tools_pi
from source.BTCTMotors import tools_xps

start_time = time.time()

######################## ------------Parameters ------------------#############

path = r'C:\Data\21_10_25\CT_900proj_abs_calib_phantom\\'
try:
    out=os.mkdir(path)
except OSError:
    print ("Can't create directory %s" % path)
path=path+'RAW\\'  
try:
    out=os.mkdir(path)
except OSError:
    print ("Can't create directory %s" % path)

#Source parameters
voltage=40
current=250
focus_mode='Medium'

# Detector acquisition parameters.

expTime = 1 #integration time for the detector
expNum = 1 #number of images to be acquired
expDelay = 0.1 #time interval between frames$
Loth = 7.0 #low energy threshold (keV)
Hith = 100.0 #high energy threshold (keV)
modeTh = '1COL0'  #must be '1COL0', '1COL1', '2COL'
pixelMode = 'NONPI' # must be 'NONPI' or 'NPI' or 'NPISUM'

#Number of flat field images annd interval (every how many hprojections)
flatNum=10
flatInterval=900

N_proj=900
proj0=0


#Piezo motors initial positions (will only move rotator)
angle0=-360

#Sample x-position
sample_xin_xps=64.5                            
#Position for flat field measurement
sample_xout_xps=50
sample_z_pi=0 #move yourself
sample_x_pi=0 #move yourself
sample_y_pi=-7.5 #move yourself

########## ---------- Information file -----------###############
try:       
    file = open(path+"info.txt","a")
except OSError:
    print ("Can't creat file: %s" % path+"info.txt")


file.write("Source Voltage: "); file.write(str(voltage)+"\n")
file.write("Source Current: "); file.write(str(current)+"\n")
file.write("Source Focus Mode: "); file.write(str(focus_mode)+"\n")
file.write("Exposure time: "); file.write(str(expTime)+"\n")
file.write("No. of frames: "); file.write(str(expNum)+"\n")
file.write("Time between frames: "); file.write(str(expDelay)+"\n")
file.write("Low TH: "); file.write(str(Loth)+"\n")
file.write("High TH: "); file.write(str(Hith)+"\n")
file.write("TH mode: "); file.write(str(modeTh)+"\n")
file.write("Pixel mode: "); file.write(str(pixelMode)+"\n")

file.write("No. flat frames: "); file.write(str(flatNum)+"\n")
file.write("Flat field interval: "); file.write(str(flatInterval)+"\n")
file.write("No. of projections: "); file.write(str(N_proj)+"\n")
file.write("Starting projection: "); file.write(str(proj0)+"\n")
file.write("Starting angle: "); file.write(str(angle0)+"\n")

file.write("XPS sample x_in_pos: "); file.write(str(sample_xin_xps)+"\n")
file.write("XPS sample x_out_pos: "); file.write(str(sample_xout_xps)+"\n")
file.write("PI sample x: "); file.write(str(sample_z_pi)+"\n")
file.write("PI sample y: "); file.write(str(sample_x_pi)+"\n")
file.write("PI sample z: "); file.write(str(sample_y_pi)+"\n")

file.close()

######### ------ Acquisition ------- ############

proj0=0
angles=angle0+np.linspace(proj0*360/N_proj,360,N_proj-proj0+1)#, endpoint=False) #Angles for the projections

#Start Pixirad
print('Starting Pixirad')
det = PEPIPixieIII()
out = PEPITIFFWriter(asynchronous=False)

det.set_param("E0_KEV",Loth)
det.set_param("E1_KEV",Hith)
det.set_param("MODE",pixelMode)
det.set_param("COL", modeTh)
det.set_param("SHOTS", expNum)
det.set_param("EXP_TIME_MILLISEC",expTime*1000)

det.initialize()
print('Pixirad initialized')

#Connect the motors and move to starting point
print('Conecting motors')
piezo=tools_pi.connect_piezo()
tools_xps.connect_XPS()

print('Moving sample to starting point')
tools_pi.move_theta_abs(piezo, angle0)
tools_xps.move_xsample_abs(sample_xin_xps-0.1)
tools_xps.move_xsample_abs(sample_xin_xps)
print('Sample at starting point')

#Acquire first flat field
print('Acquiring FlatField')
tools_xps.move_xsample_abs(sample_xout_xps)

for i in range(flatNum):
    file_name = path+'ff_pre_'+str(i)+'.tif'
    img, _ = det.acquire()
    out.save(img, file_name, metadata_list=(det,))
    
tools_xps.move_xsample_abs(sample_xin_xps)

#Rotate and acquire images
for angle in angles:
    print('Acquiring projection # ', proj0)
    tools_pi.move_theta_abs(piezo, angle)
    file_name = path+'proj_000'+str(proj0)+'.tif'
    img, _ = det.acquire()
    out.save(img, file_name, metadata_list=(det,))
    proj0+=1

#Acquire last flat field
print('Acquiring FlatField')
tools_xps.move_xsample_abs(sample_xout_xps)
for i in range(flatNum):
    file_name = path+'ff_post_'+str(i)+'.tif'
    img, _ = det.acquire()
    out.save(img, file_name, metadata_list=(det,))

tools_xps.move_xsample_abs(sample_xin_xps)

det.terminate(dethermalize=True)

elapsed_time = time.time() - start_time
print('Elapsed time: '+ str(elapsed_time)+ ' s')