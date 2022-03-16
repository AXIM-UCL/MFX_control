# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 18:14:15 2021

@author: Carlos Navarrete-Leon
"""
import numpy as np
import os
import time
from source.BTCTDetectors import hamamatsu_functions2 as hf
from source.BTCTMotors import tools_pi
from source.BTCTMotors import tools_xps

start_time = time.time()
print('Waiting for source to stabilize')
#time.sleep(7200)
######################## ------------Parameters ------------------#############

path=r'D:\Data\22_02_24\Sensitivity_Hamamatsu_2s_6x_zsd860_100umpitch\\'

#Source parameters
voltage=40
current=250
focus_mode='Small'

M_mask=6

mask_period=100e-3
z_sd=860

M_sample=z_sd/165
M_mask_sample=M_mask/M_sample

# Detector acquisition parameters.

expTime = 2 #integration time for the detector in sec
numFrames = 1 #number of images to be acquired
expDelay = 0 #time interval between frames$

#Number of flat field images annd interval (every how many projections)
flatNum=10

#Piezo motors initial positions
#sample_xin=6.0
sample_z=0
sample_y=-5.3

#position in XPS is 73.7
sample_xin_xps=67
#Position for flat field measurement
sample_xout_xps=-75

beam_stopper_xpos=0

#Mask positions
MrotKohzu1=1206
MrotKohzu2=242
MrotNP=-2.6
Mx=7
Mz=-1.0
My=21

#Dithering steps
num_dith_x=8
num_dith_y=8

########## ---------- Information file -----------###############
try:
    out=os.mkdir(path)
except OSError:
    print ("Can't create directory %s" % path)
    
path=path+'RAW\\'
try:
    out=os.mkdir(path)
except OSError:
    print ("Can't create directory %s" % path)


file = open(path+"info.txt","a")

file.write("Source Voltage: "); file.write(str(voltage)+"\n")
file.write("Source Current: "); file.write(str(current)+"\n")

file.write("Mask magnification: "); file.write(str(M_mask)+"\n")
file.write("Total distance: "); file.write(str(z_sd)+"\n")


file.write("Source Focus Mode: "); file.write(str(focus_mode)+"\n")
file.write("Exposure time: "); file.write(str(expTime)+"\n")
file.write("No. of frames: "); file.write(str(numFrames)+"\n")
file.write("Time between frames: "); file.write(str(expDelay)+"\n")

file.write("No. flat frames: "); file.write(str(flatNum)+"\n")

#file.write("PI x_pos: "); file.write(str(sample_xin)+"\n")
#file.write("PI z_pos: "); file.write(str(sample_z)+"\n")
file.write("PI y_pos: "); file.write(str(sample_y)+"\n")
#file.write("PI x_out_pos: "); file.write(str(sample_xout)+"\n")
file.write("XPS x_in_pos: "); file.write(str(sample_xin_xps)+"\n")
file.write("XPS x_out_pos: "); file.write(str(sample_xout_xps)+"\n")
file.write("XPS beam_stopper_pos: "); file.write(str(beam_stopper_xpos)+"\n")
file.write("XPS Mask rot Newport: "); file.write(str(MrotNP)+"\n")
file.write("XPS Mask rot Kohzu 1: "); file.write(str(MrotKohzu1)+"\n")
file.write("XPS Mask rot Kohzu 2: "); file.write(str(MrotKohzu2)+"\n")
file.write("XPS Mask x: "); file.write(str(Mx)+"\n")
file.write("XPS Mask z: "); file.write(str(Mz)+"\n")
file.write("XPS Mask y: "); file.write(str(My)+"\n")

file.close()

######### ------ Acquisition ------- ############

x_step=mask_period/num_dith_x*M_mask_sample
y_step=mask_period/num_dith_y*M_mask_sample

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

print('Moving sample to starting point')
tools_xps.move_xsample_abs(sample_xin_xps-x_step)
tools_xps.move_xsample_abs(sample_xin_xps)
tools_pi.move_y_abs(piezo, sample_y-y_step)
tools_pi.move_y_abs(piezo, sample_y)
print('Sample at starting point')

crashes=0

for i in range(num_dith_y):
    tools_pi.move_y_abs(piezo, sample_y+i*y_step)
    for j in range(num_dith_x):
        print('Acquiring dith step y-x', i, j)
        tools_xps.move_xsample_abs(sample_xin_xps+j*x_step)
        file_name = path+'sample_xpos_'+str(round(j*x_step, 4))+'_ypos_'+str(round(i*y_step,4))
        crashes+=hf.HM_AcquireWaitSaveTest(file_name, expTime)
        #hf.HM_AcqWaitSaveSequenceTest(file_name, expTime, numFrames)
    
    tools_xps.move_xsample_abs(sample_xin_xps-x_step)
    tools_xps.move_xsample_abs(sample_xin_xps)

#Acquire last flat field
print('Acquiring FlatField')
tools_xps.move_xsample_abs(sample_xout_xps)
for i in range(flatNum):
    file_name = path+'ff_post_'+str(i)
    crashes+=hf.HM_AcquireWaitSaveTest(file_name, expTime)
    #hf.HM_AcqWaitSaveSequenceTest(file_name, expTime, numFrames)

#Acquire last Dark
print('Acquiring Dark')
tools_xps.move_xsample_abs(beam_stopper_xpos)

for i in range(flatNum):
    file_name = path+'dark_post_'+str(i)
    crashes+=hf.HM_AcquireWaitSaveTest(file_name, expTime)
    #hf.HM_AcqWaitSaveSequenceTest(file_name, expTime, numFrames)


hf.HM_close()

elapsed_time = time.time() - start_time
print('Elapsed time: '+ str(elapsed_time)+ ' s')
print('Number of crashes:' + str(crashes))
    
