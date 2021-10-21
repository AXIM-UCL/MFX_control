# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 22:36:05 2020

@author: XPCI_BT
"""

import os
import time
import numpy as np 
from win32com.client import GetObject


def pixirad_acquire_new(file_name, expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode):
    
    pixirad_soft_trigger (expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
    time.sleep(0.1)
    pixirad_trigger()
    time.sleep(0.1)
    fin=pixirad_save_sequence (file_name, expNum, modeTh)
    
    while(fin==False):
        print('Restarting pixirad server')
        WMI = GetObject('winmgmts:')
        processes = WMI.InstancesOf('Win32_Process')
        for p in WMI.ExecQuery('select * from Win32_Process where Name="cmd.exe"'):
            print ("Killing PID:", p.Properties_('ProcessId').Value)
            os.system("taskkill /pid "+str(p.Properties_('ProcessId').Value))
        os.chdir("C:\PXRD\PX\PXRD2")
        os.system(r"start cmd /k pxrd_server.exe")
        pixirad_soft_trigger (expNum, expTime, expDelay, Hith, Loth, modeTh, pixelMode)
        time.sleep(0.1)
        pixirad_trigger()
        time.sleep(0.1)
        fin=pixirad_save_sequence (file_name, expNum, modeTh)
        
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
    #os.system(r"start /wait cmd /c C:\Python26\python C:\PXRD\PX\PXRD2\UDPTrigger.py")
    os.system(r"start cmd /c C:\Python26\python C:\PXRD\PX\PXRD2\UDPTrigger.py")
    
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

    while not os.path.exists(file_source):
    	time.sleep(0.5)
        

    size_file=os.stat(file_source).st_size
    stime=time.time()
    out=True
    while size_file != filesize:
        time.sleep(0.5)
        size_file=os.stat(file_source).st_size
        #print(time.time()-stime)
        if (time.time()-stime > 5*expNum):
            out=False
            break        
    if(out):
        os.rename(file_source, file_name)
        return out
    else:
        print('Unexpected error, restarting pixirad server')
        return out

def read_Pixirad_data(file, N_img):
    offset=24
    width=1024
    height=402
    frames=np.zeros((height, width, N_img), dtype=np.int16)
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
