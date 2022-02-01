# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 22:46:16 2021

@author: Carlos Navarrete-Leon
"""

import socket
import numpy as np
from . import mib
import tifffile
import time
HOST = '128.40.160.102'  # The server's hostname or IP address
COMMANDPORT = 6341    # The port used to send commands
DATAPORT = 6342        # The port used to receive the data

# convert command to generate TCP/IP Merlin string
def MPX_CMD(type_cmd='GET',cmd='DETECTORSTATUS'):
    '''Generate TCP command string for Merlin software. type_cmd and cmd are documented in MerlinEM Documentation. Default value GET,DETECTORSTATUS probes for the current status of the detector.'''
    length = len(cmd)
    tmp = 'MPX,00000000' + str(length+5) + ',' + type_cmd + ',' + cmd
    return tmp.encode()

# Connect sockets and probe for the detector status

def Merlin_init(TH0, TH1):  
    s_cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create command socket
    try: 
        s_cmd.connect((HOST, COMMANDPORT))
        print('Merlin connected')
        s_cmd.sendall(MPX_CMD('GET','SOFTWAREVERSION'))
        version = s_cmd.recv(1024)
        s_cmd.sendall(MPX_CMD('GET','DETECTORSTATUS'))
        status = s_cmd.recv(1024)
        print('Version CMD:', version.decode())
        print('Status CMD:', status.decode())
    except ConnectionRefusedError:
        print("Merlin not responding")
    except OSError:
        print("Merlin already connected")

    # Connect data socket
    s_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        s_data.connect((HOST, DATAPORT))
    except ConnectionRefusedError:
        print("Data port not responding")
    
    # Set base Merlin imaging parameters
    #numberFrames = 10000
    s_cmd.sendall(MPX_CMD('SET','HVBIAS,120'))
    s_cmd.sendall(MPX_CMD('SET','THRESHOLD0,'+str(TH0)))
    s_cmd.sendall(MPX_CMD('SET','THRESHOLD1,'+str(TH1)))
    #Set continuous mode on
    s_cmd.sendall(MPX_CMD('SET','CONTINUOUSRW,1'))
    #Set dynamic range
    s_cmd.sendall(MPX_CMD('SET','COUNTERDEPTH,12'))
    #Set gap time in milliseconds (The number fire corresponds to sum of frame and gap time)
    #s_cmd.sendall(MPX_CMD('SET','ACQUISITIONPERIOD,0.8'))
    #Disable file saving
    s_cmd.sendall(MPX_CMD('SET','FILEENABLE,0'))
    s_cmd.sendall(MPX_CMD('SET','SAVEALLTOFILES,1'))    
    return s_cmd, s_data

    
#Start acquisition
def Merlin_acquire(s_cmd, s_data, Nframes, expTime, filename):
    #Set frame time in miliseconds
    s_cmd.sendall(MPX_CMD('SET','ACQUISITIONTIME,'+str(expTime)))
    #Set number of frames to be acquired
    s_cmd.sendall(MPX_CMD('SET','NUMFRAMESTOACQUIRE,'+str(Nframes)))
    #Set file directory
    #s_cmd.sendall(MPX_CMD('SET','FILEDIRECTORY ,'+path))
    #Set file name
    #s_cmd.sendall(MPX_CMD('SET','FILENAME,'+filename))
    print('Acquiring file', filename)
    #Acquire
    time.sleep(0.1)

    s_cmd.sendall(MPX_CMD('CMD','STARTACQUISITION'))

    #output
    out=np.zeros((Nframes,256,256))
    # check TCP header for acquisition header (hdr) file
    data = s_data.recv(14)
    start = data.decode()
    # add the rest
    header = s_data.recv(int(start[4:]))
    if (len(header)==int(start[4:])):
        print("Header data received.")
    for x in range(Nframes):
        tcpheader = s_data.recv(14)
        #print(tcpheader)
        framedata = s_data.recv(int(tcpheader[4:]))
        while (len(framedata)!= int(tcpheader[4:])):
            #print("\tframe",x,"partially received with length",len(framedata))
            framedata += s_data.recv(int(tcpheader[4:])-len(framedata))
        data = mib.loadMib(framedata[1:],scan_size=(1,1))
        out[x,:,:]=np.squeeze(data)
        if(x%10==0):
            print('Acquired frame No.', x)
    print(Nframes,"frames received.")
    #return out
    tifffile.imwrite(filename, data=out.astype(np.int16))
    print('Acquisition done')


#sc, sd =Merlin_init()
#dat=Merlin_acquire(sc, sd, 10, 1000, r'D:\Data\21_11_18\test.tif')
#sc.close()
#sd.close()