# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 18:22:26 2021

@author: Carlos Navarrete-Leon
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

path = r'C:\Data\21_10_21\2BTCT_900proj_abs_calib_phantom_angle10_2_aftcrsh\\'
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

#Number of flat field images annd interval (every how many projections)
flatNum=10
flatInterval=900

#position in XPS is 73.7
sample_xin_xps=65.7
#Position for flat field measurement
sample_xout_xps=0
sample_z_pi=0
sample_x_pi=0
sample_y_pi=-4

#Mask positions
Mrot=-1.5
Mx=1.0
Mz=-1.0
My=15.0

#Sample positions

#Dithering steps
num_dith_x=8
num_dith_y=8

#Projections
angle0=-360
proj0=0
N_proj=900

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

file.write("XPS sample x_in_pos: "); file.write(str(sample_xin_xps)+"\n")
file.write("XPS sample x_out_pos: "); file.write(str(sample_xout_xps)+"\n")
file.write("PI sample x: "); file.write(str(sample_z_pi)+"\n")
file.write("PI sample y: "); file.write(str(sample_x_pi)+"\n")
file.write("PI sample z: "); file.write(str(sample_y_pi)+"\n")

file.write("XPS Mask rot: "); file.write(str(Mrot)+"\n")
file.write("XPS Mask x: "); file.write(str(Mx)+"\n")
file.write("XPS Mask z: "); file.write(str(Mz)+"\n")
file.write("XPS Mask y: "); file.write(str(My)+"\n")

file.write("Starting projection: "); file.write(str(proj0)+"\n")
file.write("Starting angle: "); file.write(str(angle0)+"\n")

file.close()

######### ------ Acquisition ------- ############
    
x_step=100e-3/num_dith_x
y_step=100e-3/num_dith_y

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
print('Moving sample and mask to starting point')
tools_xps.connect_XPS()
# Make sure these two are in the right position 
#tools_xps.move_rotmask_abs(Mrot)
#tools_xps.move_zmask_abs(Mz)
tools_xps.move_xsample_abs(sample_xin_xps-x_step)
tools_xps.move_xsample_abs(sample_xin_xps)
piezo=tools_pi.connect_piezo()
tools_pi.move_theta_abs(piezo, angles[0])
print('Done')

print('Moving mask to starting point')
tools_xps.move_xmask_abs(Mx-x_step)
tools_xps.move_xmask_abs(Mx)
tools_xps.move_ymask_abs(My-y_step)
tools_xps.move_ymask_abs(My)
print('Done')

y_start=0
for i in range(y_start, num_dith_y):
        tools_xps.move_ymask_abs(My+i*x_step)
        x_start=0
        if(i==y_start):
            x_start=0
        for j in range(x_start, num_dith_x):
            print('Acquiring dithering step x: '+str(j)+'and dithering step y: '+str(i))
            tools_xps.move_xmask_abs(Mx+j*x_step)
            folder_name = path+'dith_x_'+str(j)+'dith_y_'+str(i)+'\\'
            try:
                file=os.mkdir(folder_name)
            except OSError:
                print ("Couldn't create directory %s already exists" % folder_name)
            #Acquire first flat field
            print('Acquiring FlatField')
            tools_xps.move_xsample_abs(sample_xout_xps)
            for fp in range(flatNum):
                file_name = folder_name+'ff_pre_'+str(fp)+'.tif'
                img, _ = det.acquire()
                out.save(img, file_name, metadata_list=(det,))
            tools_xps.move_xsample_abs(sample_xin_xps)
            #Acquire projections
            print('Acquiring Projections')
            for angle in angles:
                print('Acquiring projection No.: ', proj0)     
                tools_pi.move_theta_abs(piezo, angle)
                file_name = folder_name+'proj_000'+str(proj0)+'.tif'
                img, _ = det.acquire()
                out.save(img, file_name, metadata_list=(det,))
                proj0+=1     
            #Acquire post flat field
            print('Acquiring FlatField')
            tools_xps.move_xsample_abs(sample_xout_xps)
            for fa in range(flatNum):
                file_name = folder_name+'ff_post_'+str(fa)+'.tif'
                img, _ = det.acquire()
                out.save(img, file_name, metadata_list=(det,))
            tools_xps.move_xsample_abs(sample_xin_xps)
                     
        tools_xps.move_xmask_abs(Mx-x_step)
        tools_xps.move_xmask_abs(Mx)

elapsed_time = time.time() - start_time
print('Elapsed time: '+ str(elapsed_time)+ ' s')
