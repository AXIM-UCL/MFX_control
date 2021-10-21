# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 16:36:21 2020

@author: Carlos Navarrete-Leon

This script acquires a simple CT sequence of images in which only the sample
is rotating.
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import tools_pi
import tools_pixirad
import time
import os
import sys
import tools_xps

start_time = time.time()

######################## ------------Parameters ------------------#############


dir_date=r'C:\Data\\'
#folder=sys.argv[1]
#folder = '21_06_08\CT_360_3sphsample_8\\'

#Source parameters
voltage=40
current=250
focus_mode='Small'
    
# Detector acquisition parameters.

expTime = 1 #integration time for the detector
expNum = 1 #number of images to be acquired
expDelay = 0.1 #time interval between frames$
Loth = 7.0 #low energy threshold (keV)
Hith = 50.0 #high energy threshold (keV)
modeTh = '1COL0'  #must be '1COL0', '1COL1', '2COL'
pixelMode = 'NONPI' # must be 'NONPI' or 'NPI' or 'NPISUM'

#Number of flat field images annd interval (every how many projections)
flatNum=10
flatInterval=900

#N_proj=900
proj0=0
#angle0=-360

#Piezo motors initial positions
#sample_xin=6.0
sample_z=0.0
sample_y=-11


#position in XPS is 73.7
sample_xin_xps=58.5
#Position for flat field measurement
sample_xout_xps=20

######### ------ Acquisition ------- ############

def run_scan(folder, angle0, N_proj):
    path=dir_date+folder
    try:
        out=os.mkdir(path)
    except OSError:
        print ("Directory %s already exists" % path)
    proj0=0
    angles=angle0+np.linspace(proj0*360/N_proj,360,N_proj-proj0+1)#, endpoint=False) #Angles for the projections
    
    #Start pixirad server
    print('Starting Pixirad server')
    os.chdir("C:\PXRD\PX\PXRD2")
    os.system(r"start cmd /k pxrd_server.exe")
    
    
    #Connect the motors and move to starting point
    piezo=tools_pi.connect_piezo()
    tools_xps.connect_XPS()
    print('Moving sample to starting point')
    tools_pi.move_theta_abs(piezo, angles[0])
    #tools_pi.move_x_abs(piezo, sample_xin)
    tools_xps.move_xsample_abs(sample_xin_xps-0.1)
    tools_xps.move_xsample_abs(sample_xin_xps)
    tools_pi.move_y_abs(piezo, sample_y)
    tools_pi.move_z_abs(piezo, sample_z)
    print('Done')
    
    #Rotate, acquire image, save image and acquire Flat Field every 100 projections
    print('Acquiring FlatField')
    #tools_pi.move_x_abs(piezo, sample_xout)
    tools_xps.move_xsample_abs(sample_xout_xps)
    file_name = path+'ff_000'+str(proj0)+'.dat'
    tools_pixirad.pixirad_acquire_new(file_name, flatNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
    #tools_pi.move_x_abs(piezo, sample_xin)
    tools_xps.move_xsample_abs(sample_xin_xps)
    
    for angle in angles:         
        tools_pi.move_theta_abs(piezo, angle)
        file_name = path+'proj_000'+str(proj0)+'.dat'
        tools_pixirad.pixirad_acquire_new(file_name, expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
        proj0+=1
        
    #Rotate, acquire image, save image and acquire Flat Field every 100 projections
    print('Acquiring FlatField')
    #tools_pi.move_x_abs(piezo, sample_xout)
    tools_xps.move_xsample_abs(sample_xout_xps)
    file_name = path+'ff_000'+str(proj0)+'.dat'
    tools_pixirad.pixirad_acquire_new(file_name, flatNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
    #tools_pi.move_x_abs(piezo, sample_xin)
    tools_xps.move_xsample_abs(sample_xin_xps)
    
        
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
    file.write("Flat field interval: "); file.write(str(flatInterval)+"\n")
    file.write("No. of projections: "); file.write(str(N_proj)+"\n")
    file.write("Starting projection: "); file.write(str(proj0)+"\n")
    file.write("Starting angle: "); file.write(str(angle0)+"\n")
    
    #file.write("PI x_pos: "); file.write(str(sample_xin)+"\n")
    file.write("PI z_pos: "); file.write(str(sample_z)+"\n")
    file.write("PI y_pos: "); file.write(str(sample_y)+"\n")
    #file.write("PI x_out_pos: "); file.write(str(sample_xout)+"\n")
    file.write("XPS x_in_pos: "); file.write(str(sample_xin_xps)+"\n")
    file.write("XPS x_out_pos: "); file.write(str(sample_xout_xps)+"\n")
    
    
    file.close()
    
    elapsed_time = time.time() - start_time
    print('Elapsed time: '+ str(elapsed_time)+ ' s')