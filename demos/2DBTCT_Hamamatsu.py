# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 18:22:26 2021
@author: Carlos Navarrete-Leon
"""

import numpy as np
import sys
sys.path.insert(1, r'C:\Users\XPCI_BT\Documents\GitHub\MFX_control')
import os
import time
from source.BTCTDetectors import hamamatsu_functions2 as hf
from source.BTCTMotors import tools_pi
from source.BTCTMotors import tools_xps

start_time = time.time()
print('Waiting for source to stabilize')
#time.sleep(3600)
######################## ------------Parameters ------------------#############

path = r'D:\Data\22_03_03\2BTCT_2000proj_4x4_ChickenWing_1.2s\\'
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
focus_mode='Small'
    
# Detector acquisition parameters.

expTime = 1.2 #integration time for the detector in sec
numFrames = 1 #number of images to be acquired
expDelay = 0 #time interval between frames$

#Number of flat field images annd interval (every how many projections)
flatNum=10

#Mask parameters
mask_period=50e-3

#Piezo motors initial positions
#sample_xin=6.0
sample_z=0
sample_y_pi=-10.9

#position in XPS is 73.7
sample_xin_xps=62
#Position for flat field measurement
sample_xout_xps=-75
beam_stopper_xpos=0

#Mask positions
MrotKohzu1=706
MrotKohzu2=1932
MrotNP=-2.0
Mx=7.6
Mz=-1.0
My=24.8

#Dithering steps
num_dith_x=4
num_dith_y=4

#Projections
angle0=-360
proj0=0
N_proj=2000

########## ---------- Information file -----------###############

try:       
    file = open(path+"info.txt","a")
except OSError:
    print ("Can't creat file: %s" % path+"info.txt")

file.write("Source Voltage: "); file.write(str(voltage)+"\n")
file.write("Source Current: "); file.write(str(current)+"\n")
file.write("Source Focus Mode: "); file.write(str(focus_mode)+"\n")
file.write("Exposure time: "); file.write(str(expTime)+"\n")
file.write("No. of frames: "); file.write(str(numFrames)+"\n")
file.write("Time between frames: "); file.write(str(expDelay)+"\n")

file.write("No. flat frames: "); file.write(str(flatNum)+"\n")

file.write("XPS sample x_in_pos: "); file.write(str(sample_xin_xps)+"\n")
file.write("XPS sample x_out_pos: "); file.write(str(sample_xout_xps)+"\n")
file.write("PI sample y: "); file.write(str(sample_y_pi)+"\n")

file.write("XPS x_in_pos: "); file.write(str(sample_xin_xps)+"\n")
file.write("XPS x_out_pos: "); file.write(str(sample_xout_xps)+"\n")
file.write("XPS beam_stopper_pos: "); file.write(str(beam_stopper_xpos)+"\n")
file.write("XPS Mask rot Newport: "); file.write(str(MrotNP)+"\n")
file.write("XPS Mask rot Kohzu 1: "); file.write(str(MrotKohzu1)+"\n")
file.write("XPS Mask rot Kohzu 2: "); file.write(str(MrotKohzu2)+"\n")
file.write("XPS Mask x: "); file.write(str(Mx)+"\n")
file.write("XPS Mask z: "); file.write(str(Mz)+"\n")
file.write("XPS Mask y: "); file.write(str(My)+"\n")

file.write("Starting projection: "); file.write(str(proj0)+"\n")
file.write("Starting angle: "); file.write(str(angle0)+"\n")
file.write("No. of Projections: "); file.write(str(N_proj)+"\n")

file.close()

######### ------ Acquisition ------- ############
    
x_step=mask_period/num_dith_x
y_step=mask_period/num_dith_y

angles=angle0+np.linspace(proj0*360/N_proj,360,N_proj-proj0+1)#, endpoint=False) #Angles for the projections
    
#Start Detector
print('Starting Hamamatsu')
hf.HM_init()
hf.HM_setExposureTime(expTime)
#hf.HM_SetSequence(numFrames)
print('Hamamatsu initialized')

#Connect the motors and move to starting point
print('Conecting motors')
piezo=tools_pi.connect_piezo()
tools_xps.connect_XPS()

#Connect the motors and move to starting point
print('Moving sample to starting point')
# Make sure these two are in the right position 
#tools_xps.move_rotmask_abs(Mrot)
#tools_xps.move_zmask_abs(Mz)
tools_xps.move_xsample_abs(sample_xin_xps-x_step)
tools_xps.move_xsample_abs(sample_xin_xps)
tools_pi.move_theta_abs(piezo, angles[0])
tools_pi.move_y_abs(piezo, sample_y_pi)
print('Done')

print('Moving mask to starting point')
tools_xps.move_xmask_abs(Mx-x_step)
tools_xps.move_xmask_abs(Mx)
tools_xps.move_ymask_abs(My-y_step)
tools_xps.move_ymask_abs(My)
print('Done')

crashes=0

y_start=3
for i in range(y_start, num_dith_y):
        tools_xps.move_ymask_abs(My+i*y_step)
        x_start=0
        if(i==y_start):
            x_start=1
        for j in range(x_start, num_dith_x):
            print('Acquiring dithering step x: '+str(j)+'and dithering step y: '+str(i))
            tools_xps.move_xmask_abs(Mx+j*x_step)
            folder_name = path+'dith_x_'+str(j)+'dith_y_'+str(i)+'\\'
            try:
                file=os.mkdir(folder_name)
            except OSError:
                print ("Couldn't create directory %s already exists" % folder_name)
           
            #Acquire first Dark
            print('Acquiring Dark')
            tools_xps.move_xsample_abs(beam_stopper_xpos)
            for dp in range(flatNum):
                file_name = folder_name+'dark_pre_'+str(dp)
                crashes+=hf.HM_AcquireWaitSaveTest(file_name, expTime)
            #Acquire first flat field
            print('Acquiring FlatField')
            tools_xps.move_xsample_abs(sample_xout_xps)
            for fp in range(flatNum):
                file_name = folder_name+'ff_pre_'+str(fp)
                crashes+=hf.HM_AcquireWaitSaveTest(file_name, expTime)
            tools_xps.move_xsample_abs(sample_xin_xps)
            #Acquire projections
            print('Acquiring Projections')
            proj0=0
            for angle in angles:
                print('Acquiring projection No.: ', proj0)     
                tools_pi.move_theta_abs(piezo, angle)
                file_name = folder_name+'proj_000'+str(proj0)
                crashes+=hf.HM_AcquireWaitSaveTest(file_name, expTime)
                proj0+=1     
            #Acquire post flat field
            print('Acquiring FlatField')
            tools_xps.move_xsample_abs(sample_xout_xps)
            for fa in range(flatNum):
                file_name = folder_name+'ff_post_'+str(fa)
                crashes+=hf.HM_AcquireWaitSaveTest(file_name, expTime)
            tools_xps.move_xsample_abs(sample_xin_xps)
            #Acquire last Dark
            print('Acquiring Dark')
            tools_xps.move_xsample_abs(beam_stopper_xpos)
            for da in range(flatNum):
                file_name = folder_name+'dark_post_'+str(da)
                crashes+=hf.HM_AcquireWaitSaveTest(file_name, expTime)
                     
        tools_xps.move_xmask_abs(Mx-x_step)
        tools_xps.move_xmask_abs(Mx)

elapsed_time = time.time() - start_time
print('Elapsed time: '+ str(elapsed_time)+ ' s')
print('Number of crashes:' + str(crashes))