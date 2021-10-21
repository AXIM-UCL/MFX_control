# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 18:22:26 2021

@author: Carlos Navarrete-Leon
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import tools_pi
import tools_xps
import newport_functions
import tools_pixirad
import time
import os
import sys
from win32com.client import GetObject
    

start_time = time.time()

######################## ------------Parameters ------------------#############

dir_date=r'C:\Data\\'
folder=r'21_07_15\CT_4x4_900projs_test\\'

#Source parameters
voltage=40
current=250
focus_mode='Medium'
    
# Detector acquisition parameters.

expTime = 1 #integration time for the detector
expNum = 1 #number of images to be acquired
expDelay = 0.1 #time interval between frames$
Loth = 7.0 #low energy threshold (keV)
Hith = 50.0 #high energy threshold (keV)
modeTh = '1COL0'  #must be '1COL0', '1COL1', '2COL'
pixelMode = 'NONPI' # must be 'NONPI' or 'NPI' or 'NPISUM'

#Number of flat field images annd interval (every how many projections)
flatNum=1
flatInterval=300

#Piezo motors initial positions
#sample_xin=6.0
sample_z=0.0
sample_y=6.0


#position in XPS is 73.7
sample_xin_xps=58.5
#Position for flat field measurement
sample_xout_xps=0

sample_z=0.0
sample_y=-4.5
#Mask positions
Mrot=-1.5
Mx=1.0
Mz=-1.0
My=15.0

#Sample positions

#Dithering steps
num_dith_x=4
num_dith_y=4

#Projections
angle0=-360
proj0=0
N_proj=900

######### ------ Acquisition ------- ############

#def run_scan(folder, num_dith_x, num_dith_y):
path=dir_date+folder
try:
    out=os.mkdir(path)
except OSError:
    print ("Directory %s already exists" % path)
    
x_step=100e-3/num_dith_x
y_step=100e-3/num_dith_y

angles=angle0+np.linspace(proj0*360/N_proj,360,N_proj-proj0+1)#, endpoint=False) #Angles for the projections
    
#Start pixirad server
print('Starting Pixirad server')
os.chdir("C:\PXRD\PX\PXRD2")
os.system(r"start cmd /k pxrd_server.exe")


#Connect the motors and move to starting point
print('Moving sample and mask to starting point')
tools_xps.connect_XPS()
tools_xps.move_rotmask_abs(Mrot)
tools_xps.move_zmask_abs(Mz)
tools_xps.move_xsample_abs(sample_xin_xps-x_step)
tools_xps.move_xsample_abs(sample_xin_xps)
piezo=tools_pi.connect_piezo()
#tools_pi.move_theta_abs(piezo, angles[0]-0.1)
tools_pi.move_theta_abs(piezo, angles[0])
tools_pi.move_y_abs(piezo, sample_y)
tools_pi.move_z_abs(piezo, sample_z)
print('Done')


for angle in angles:    
    print('Acquiring projection No.: ', proj0)     
    tools_pi.move_theta_abs(piezo, angle)
    folder_name = path+'proj_000'+str(proj0)+'\\'
    try:
        out=os.mkdir(folder_name)
    except OSError:
        print ("Couldn't create directory %s already exists" % folder_name)
    if(proj0%flatInterval==0):
        ff_folder_name = path+'ff_000'+str(proj0)+'\\'
        try:
            out=os.mkdir(ff_folder_name)
        except OSError:
            print ("Couldn't create directory %s already exists" % folder_name)
    print('Moving mask to starting point')
    tools_xps.move_xmask_abs(Mx-x_step)
    tools_xps.move_xmask_abs(Mx)
    tools_xps.move_ymask_abs(My-y_step)
    tools_xps.move_ymask_abs(My)
    print('Done')
    for i in range(num_dith_y):
        tools_xps.move_ymask_abs(My+i*x_step)
        for j in range(num_dith_x):
            tools_xps.move_xmask_abs(Mx+j*x_step)
            file_name = folder_name+'proj_000'+str(proj0)+'_sample_xpos_'+str(round(j*x_step, 4))+'_ypos_'+str(round(i*y_step,4))+'.dat'
            tools_pixirad.pixirad_acquire_new(file_name, expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
            if(proj0%flatInterval==0):
                print('Acquiring FlatField')
                tools_xps.move_xsample_abs(sample_xout_xps)
                ff_name = ff_folder_name+'proj_000'+str(proj0)+'_ff_xpos_'+str(round(j*x_step,4))+'_ypos_'+str(round(i*y_step,4))+'.dat'
                tools_pixirad.pixirad_acquire_new(ff_name, flatNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
                tools_xps.move_xsample_abs(sample_xin_xps)
        tools_xps.move_xmask_abs(Mx-x_step)
        tools_xps.move_xmask_abs(Mx)
    # if(angle%100==0):
    #     print('Restarting pixirad server')
        WMI = GetObject('winmgmts:')
        processes = WMI.InstancesOf('Win32_Process')
        for p in WMI.ExecQuery('select * from Win32_Process where Name="cmd.exe"'):
            print ("Killing PID:", p.Properties_('ProcessId').Value)
            os.system("taskkill /pid "+str(p.Properties_('ProcessId').Value))
    #     os.chdir("C:\PXRD\PX\PXRD2")
    #     os.system(r"start cmd /k pxrd_server.exe")
    proj0+=1
   
########## ---------- Information file -----------###############

file = open(path+"info.txt","a")

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

file.write("PI z_pos: "); file.write(str(sample_z)+"\n")
file.write("PI y_pos: "); file.write(str(sample_y)+"\n")
file.write("XPS x_in_pos: "); file.write(str(sample_xin_xps)+"\n")
file.write("XPS x_out_pos: "); file.write(str(sample_xout_xps)+"\n")
file.write("XPS Mask rot: "); file.write(str(Mrot)+"\n")
file.write("XPS Mask x: "); file.write(str(Mx)+"\n")
file.write("XPS Mask z: "); file.write(str(Mz)+"\n")
file.write("XPS Mask y: "); file.write(str(My)+"\n")

file.write("Starting projection: "); file.write(str(proj0)+"\n")
file.write("Starting angle: "); file.write(str(angle0)+"\n")

file.close()

elapsed_time = time.time() - start_time
print('Elapsed time: '+ str(elapsed_time)+ ' s')