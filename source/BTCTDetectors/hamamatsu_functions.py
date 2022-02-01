# -*- coding: utf-8 -*-
"""
Spyder Editor

@author: AAstolfo
"""

import socket
import os.path
import time

def HM_init():
    global HM_socket
    host = '127.0.0.1'
    port = 1001

    HM_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #HM_socket.settimeout(0.05)
    HM_socket.settimeout(1)
    #HM_socket.settimeout(0.0)

    # attempt to fix the occasional timeout 
    try: 
        HM_socket.connect((host,port))
    except OSError:
        pass
        
    
    HM_readans()

    return HM_socket

def HM_close():
    
    HM_socket.close()

def HM_sendcmd(cmd):
    command = bytes(cmd+'\r','ascii')
    ans = HM_clearbuffer()
    HM_socket.send(command)
    ans = HM_readans()
    
    return ans

def HM_readans():
    msg = b''
    last = b''

    count = 0

    while last != bytes('\r','ascii'):   
        #last = HM_socket.recv(1)
        
        try:
            last = HM_socket.recv(1)
        except OSError:
            pass
        
        #print(last)
        msg = msg + last
        count = count + 1
    #print(msg)
    return msg

def HM_closeAll():
    HM_sendcmd(r'ImgDelete(All)')
 

def HM_setExposureTime(Exposure_time):
    HM_sendcmd(r'CamParamSet(Acquire,exposure,'+str(Exposure_time) + ' s)')
    HM_sendcmd(r'CamParamSet(Live,exposure,'+str(Exposure_time) + ' s)')

def HM_AcqStart():
    HM_sendcmd(r'AcqStart(Acquire)')
    
def HM_AcqStatus():
    err_flag = 0 
    ans = 0
    while err_flag == 0:
        try:
            ans = HM_sendcmd(r'AcqStatus()')
            err_flag = 1
        except OSError:
            err_flag = 1
    return ans
    
def HM_ImgSave(file_address, image_format = 0):
    
    if image_format == 0:
        # save the last image as tiff file
        HM_sendcmd(r'ImgSave(Current,TIFF,' + file_address + '.tif,1)')
    if image_format == 2:
        # save the last image as his file
        HM_sendcmd(r'ImgSave(Current,img,' + file_address + '.img,1)')        
        #HM_readans()
    
def HM_SequenceSave(file_address, image_format = 0):
    if image_format == 0:
        # save the last image as tiff file
        HM_sendcmd(r'SeqSave(tif,' + file_address + '.tif)')
    if image_format == 1:
         # save the last image as his file
        HM_sendcmd(r'SeqSave(HIS,' + file_address + '.his)')        

    
    
def HM_AcquireWaitSave(file_address,save_format = 0, expTime=1):
    # this is to acquire an image, wait while it is done and save it as tiff
    # in case of HIS = 1 it does the same as a Seq and save as his
    
    if save_format == 0 or save_format == 2:
        done = 0
        while(done==0):
            st_time=time.time()
            HM_AcqStart()
            time.sleep(expTime*0.9)
            #done = 0
            waittime = 0
            problems=0
            while (done == 0 and problems==0):
                #time.sleep(0.01)
                check_status = HM_AcqStatus()
                if check_status == b'0,AcqStatus,idle\r':
                    #print('done')
                    # time to save the image
                    image_extension = (save_format == 0 and '.tif') or (save_format == 2 and '.img') or ''
                    while not os.path.isfile(file_address + image_extension):
                        if save_format == 0:
                            HM_ImgSave(file_address)
                            #time.sleep(0.1)
                        else:
                            HM_ImgSave(file_address,2)
                            #time.sleep(0.1)
                    done = 1
                    #time_flag = 1
                if (waittime >= 5):
                    HM_sendcmd('AcqStop()')
                    print('Problems, stopping acquisition')
                    problems=1
                #print(check_status)
                waittime+=time.time()-st_time
    else:
        HM_StartSequence(1)
        done = 0
        while done == 0:
            check_status = HM_SeqStatus()
            if check_status == b'0,SeqStatus,idle\r':
                #print('done')
                done = 1
                # time to save the image
                image_extension = '.his'
                while not os.path.isfile(file_address + image_extension):
                    HM_SequenceSave(file_address,1)
            #print(check_status)
    #HM_closeAll()

def HM_SetSequence(No_loops, time_interval = 0):
    HM_sendcmd('SeqParamSet(NoOfLoops,' + str(No_loops) + ')')
    
    HM_sendcmd('SeqParamSet(AcquisitionMode,Live)')
    
    if No_loops == 1 or time_interval ==0:
        HM_sendcmd('SeqParamSet(AcquisitionSpeed,Full speed)')
    else:
        HM_sendcmd('SeqParamSet(AcquisitionSpeed,Fixed intervals)')
        HM_sendcmd('SeqParamSet(AcquireInterval,' + str(round(time_interval,2)) + 's)')

def HM_DeleteSequence():
    HM_sendcmd('SeqDelete()')
    
def HM_StartSequence(exit_mode = 0):
    # this is to start a sequence
    # exit mode is to manage the exit as:
    # exit_mode = 0     out after the command is received
    # exit_mode = 1     out after the acquisition is started
    # exit_mode = 2     out after entire sequence is done
    
    # first I check if the sequence is not already running
    ans = ''
    check_status = HM_SeqStatus()
    if check_status == b'0,SeqStatus,busy,Sequence Acquisition\r':
        print('Sequence already running. Not sending it.')
        done = 1
    else:
        ans = HM_sendcmd('SeqStart()')
        print(ans)
        done = 0
    
    if ans == b'0,SeqStart\r' and exit_mode == 0:
        done = 1

    if exit_mode == 1:
        while done == 0:
            check_message = HM_readans()
            #print(check_message)
            # it has difference message if sequence with interval or full frame
            if check_message == b'4,Sequence: Acquisition started\r' or check_message == b'4,Acquiring Sequence\r':
                done = 1   

    while done == 0:
        check_status = HM_SeqStatus()
        #print(check_status)
        #if check_status == 0 and exit_mode == 2:
        if check_status == b'0,SeqStatus,idle\r' and exit_mode == 2:    
            print('done')
            done = 1
    
    return done

def HM_WaitforSequenceImage():
    # this is for getting the image done during a sequence with delay
    done = 0
    while done == 0:
        check_message = HM_readans()
        print(check_message)
        if '4,Frame rate' in str(check_message):
            #print(check_message)
            done = 1
    
    return done


def HM_StopLive():
    # check if detector is live and stop it
    ans = HM_AcqStatus()
    
    if ans == b'0,AcqStatus,busy,Live\r':
        HM_sendcmd('AcqStop()')

def HM_SeqStatus():
    err_flag = 0 
    ans = 0
    busy = 0
    
    while err_flag == 0:
        try:
            ans = HM_sendcmd('SeqStatus()')
            err_flag = 1
        except OSError:
            err_flag = 1
    
    # if ans == b'0,SeqStatus,idle\r':
    #     busy = 0
    # if ans == b'0,SeqStatus,busy,Sequence Acquisition\r':
    #     busy = 1        
    
    return ans  
        
def HM_clearbuffer():
    # this is to clear all the messages from the detector in the buffer
    msg = b''
    err_flag = 0

    while err_flag == 0:
        try:
            last = HM_socket.recv(1)
            #print(last)
            msg = msg + last
        except OSError:
            err_flag = 1
    #print(msg)
    return msg       