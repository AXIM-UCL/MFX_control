# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 18:14:15 2021

@author: XPCI_BT
"""
import numpy as np
import os
import time
from source.BTCTDetectors.PEPIPixirad import PEPIPixieIII
from source.BTCTProcessing.PEPITIFFIO import PEPITIFFWriter
from source.BTCTMotors import tools_pi
from source.BTCTMotors import tools_xps


start_time = time.time()
print('Waiting for source to stabilize')
#time.sleep(3600)
######################## ------------Parameters ------------------#############

path=r'D:\Data\21_12_09\DirectionalDF_=_40kVp_250uA_100umpitch_medfoc\\'

#Source parameters
voltage=40
current=250
focus_mode='Medium'

M_mask_sample=1.17

# Detector acquisition parameters.

expTime = 1 #integration time for the detector in sec
expNum = 10 #number of images to be acquired
expDelay = 0.1 #time interval between frames$
Loth = 5.0 #low energy threshold (keV)
Hith = 100.0 #high energy threshold (keV)
modeTh = '1COL0'  #must be '1COL0', '1COL1', '2COL'
pixelMode = 'NONPI' # must be 'NONPI' or 'NPI' or 'NPISUM'

#Number of flat field images annd interval (every how many projections)
flatNum=10

#Piezo motors initial positions
#sample_xin=6.0
sample_z=0.0
sample_y=1.0

#position in XPS is 73.7
sample_xin_xps=73.7
#Position for flat field measurement
sample_xout_xps=-75

#Mask positions
Mrot=-1.5
Mx=1.0
Mz=-1.0
My=15.0

#Dithering steps
num_dith_x=8
num_dith_y=8

########## ---------- Information file -----------###############
try:
    out=os.mkdir(path)
except OSError:
    print ("Can't create directory %s" % path)

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

#file.write("PI x_pos: "); file.write(str(sample_xin)+"\n")
#file.write("PI z_pos: "); file.write(str(sample_z)+"\n")
file.write("PI y_pos: "); file.write(str(sample_y)+"\n")
#file.write("PI x_out_pos: "); file.write(str(sample_xout)+"\n")
file.write("XPS x_in_pos: "); file.write(str(sample_xin_xps)+"\n")
file.write("XPS x_out_pos: "); file.write(str(sample_xout_xps)+"\n")
file.write("XPS Mask rot: "); file.write(str(Mrot)+"\n")
file.write("XPS Mask x: "); file.write(str(Mx)+"\n")
file.write("XPS Mask z: "); file.write(str(Mz)+"\n")
file.write("XPS Mask y: "); file.write(str(My)+"\n")

file.close()

######### ------ Acquisition ------- ############

x_step=100e-3/num_dith_x*M_mask_sample
y_step=100e-3/num_dith_y*M_mask_sample

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
tools_xps.move_xsample_abs(sample_xin_xps-x_step)
tools_xps.move_xsample_abs(sample_xin_xps)
tools_pi.move_y_abs(piezo, sample_y-y_step)
tools_pi.move_y_abs(piezo, sample_y)
print('Sample at starting point')

#Acquire first flat field
print('Acquiring FlatField')
tools_xps.move_xsample_abs(sample_xout_xps)

for i in range(flatNum):
    file_name = path+'ff_pre_'+str(i)+'.tif'
    img, _ = det.acquire()
    out.save(img, file_name, metadata_list=(det,))
    
tools_xps.move_xsample_abs(sample_xin_xps)

for i in range(num_dith_y):
    tools_pi.move_y_abs(piezo, sample_y+i*y_step)
    for j in range(num_dith_x):
        tools_xps.move_xsample_abs(sample_xin_xps+j*x_step)
        file_name = path+'sample_xpos_'+str(round(j*x_step, 4))+'_ypos_'+str(round(i*y_step,4))+'.tif'
        img, _ = det.acquire()
        out.save(img, file_name, metadata_list=(det,))
    tools_xps.move_xsample_abs(sample_xin_xps-x_step)
    tools_xps.move_xsample_abs(sample_xin_xps)

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

    
