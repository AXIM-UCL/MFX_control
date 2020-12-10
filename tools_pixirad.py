# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 22:36:05 2020

@author: XPCI_BT
"""

import os
import time
import numpy as np 


def pixirad_acquire_new(file_name, expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode):
    pixirad_soft_trigger (expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
    time.sleep(1)
    pixirad_trigger()
    time.sleep(1)
    pixirad_save_sequence (file_name, expNum, modeTh)
    print('Acquired ' + str(expNum) + ' frame(s)')
    
def pixirad_soft_trigger (expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode):
    command=(r'C:\Python26\python C:\PXRD\PX\PXRD2\PX2_PIII_DAQ_soft_trigger.py asic=PIII build=PX2 printamelo=ciao'+
             ' hith='+str(Hith)+
             ' loth='+str(Loth)+
             ' modeth='+modeTh+
             ' pixelmode='+pixelMode+  
             ' frames='+str(expNum)+
             ' shutter='+str(expTime*1000)+
             ' delayms='+str(expDelay*1000))

    os.system("start cmd /c "+ command)

def pixirad_trigger():
    os.system(r"start /wait cmd /c C:\Python26\python C:\PXRD\PX\PXRD2\UDPTrigger.py")
    
def pixirad_save_sequence (file_name, expNum, modeTh):
    file_source = "C:\\PXRD\\PX\\PXRD2\\SavedData\\BOX_002008\\DATA\\temp_data.dat"
    
    if(modeTh == '1COL0'):
        filesize = (24. + 2.*(402.*1024.))*expNum
    elif(modeTh == '1COL1'):
        filesize = (24. + 2.*(402.*1024.))*expNum
    elif(modeTh == '2COL'):
        filesize = (24. + 2.*(402.*1024.))*expNum*2
    else:
        print('wrong modeTh definition')
    
    size_file=os.stat(file_source).st_size
    while size_file != filesize:
        time.sleep(0.5)
        size_file=os.stat(file_source).st_size
    os.rename(file_source, file_name)

def read_Pixirad_data(file, N_img):
    offset=24
    width=1024
    height=402
    frames=np.zeros((height, width, N_img))
    point_end=0
    fid=open(file, "r")
    for pos in range(N_img):
        fid.seek(offset+point_end)
        temp=np.fromfile(fid, dtype=np.int16, count=height*width).reshape((width, height))
        temp=np.rot90(temp)
        frames[:,:,pos]=temp
        point_end=fid.tell()       
    fid.close()
    return frames, np.sum(frames, axis=2)
