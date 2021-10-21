# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 13:13:09 2018

@author: AAstolfo
"""

import socket
import time

def NP_init(No_motors):
    global NP_sockets
    
    #No_motors = 4
    
    # it creates a socket per motor plus two extra for stop and position reading
    No_sockets = No_motors + 2

    #host = '192.168.5.254'
    host = '192.168.254.254'
    
    port = 5001    
    
    for i in range(0,No_sockets):
        if i == 0:
            tmp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            tmp.connect((host, port))
            NP_sockets = [tmp] * No_sockets
        else:
            tmp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            tmp.connect((host, port))
            NP_sockets[i] = tmp
    return NP_sockets

def NP_sendcmd(cmd,socket,readans):
    command = bytes(cmd,'ascii')
    
    NP_sockets[socket].send(command)
    
    if readans == 1:
        ans = NP_readans(socket)
    else:
        ans = ''
    
    return ans
    
def NP_readans(socket):
    msg = b''
    last = b'' 
    
    while last != b'EndOfAPI':
        #print(last+b'merda')        
        msg = msg + NP_sockets[socket].recv(1)                                    
        tmp = msg.split(b',')
        last = tmp[len(tmp)-1]
    
    #print(msg)    
    return msg

def NP_gp(motor):
    cmd = 'GroupPositionCurrentGet(Group'+str(motor)+',double  *)'
    pos_socket = len(NP_sockets) -1
    ans = NP_sendcmd(cmd,pos_socket,1)
    tmp = ans.split(b',')
    #print(tmp)
    pos = float(tmp[1])
    #print(pos)
    return pos

def NP_mr(motor,step, wait=0):
    # set wait=1 to return after the motion completed
    
    cmd = 'GroupMoveRelative(Group'+str(motor)+','+str(step)+')'
    if wait ==1:
        NP_sendcmd(cmd,motor,1)  
        status = 1
        while status == 1:
            #print(status)
            status = NP_gms(motor)
    else:
        NP_sendcmd(cmd,motor,0)
    
def NP_ma(motor, target, wait=0):
    cmd = 'GroupMoveAbsolute(Group'+str(motor)+','+str(target)+')'
    if wait == 1:
        out=NP_sendcmd(cmd,motor,1)
        time.sleep(0.5)
        status = 1
        while status == 1:
            #print(status)
            status = NP_gms(motor)
    else:
        out=NP_sendcmd(cmd,motor,0)
    out=out.decode()
    out=out.split(',')
    if(out[0]!='0'):
        return 0
    else:
        return 1
    
    
    
def NP_stop(motor):
    cmd = 'GroupMoveAbort(Group'+str(motor)+')'
    NP_sendcmd(cmd,0,1) 

def NP_gv(motor):
    cmd = 'PositionerSGammaParametersGet(Group'+str(motor)+'.Pos,double *,double *,double *,double *)'
    ans = NP_sendcmd(cmd,motor,1)     
    tmp = ans.split(b',')
    values = [float(tmp[0]),float(tmp[1]),float(tmp[2]),float(tmp[3]),float(tmp[4])]
    #print(float(tmp[1]))
    return values

def NP_gcv(motor):
    #Get current velocity of the motor
    cmd = 'GroupVelocityCurrentGet(Group'+str(motor)+',double *)'
    pos_socket = len(NP_sockets) -1
    ans = NP_sendcmd(cmd,pos_socket,1)     
    tmp = ans.split(b',')
    values = float(tmp[1])
    #print(float(tmp[1]))
    return values

def NP_gms(motor):
    #Get motion status
    pos_socket = len(NP_sockets) -1
    cmd = 'GroupMotionStatusGet(Group'+str(motor)+',int *)'
    ans = NP_sendcmd(cmd,pos_socket,1)
    #print(ans)
    tmp = ans.split(b',')
    values = int(tmp[1])
    return values
    
def NP_getStatus(motor):
    #Get motion status
    pos_socket = len(NP_sockets) -1
    cmd = 'GroupStatusGet(Group'+str(motor)+',int *)'
    ans = NP_sendcmd(cmd,pos_socket,1)
    tmp = ans.split(b',')
    values = int(tmp[1])
    return values

def NP_sv(motor,velocity):
    
    old_velocity =NP_gv(motor) 
    cmd = 'PositionerSGammaParametersSet(Group'+str(motor)+'.Pos,'+str(velocity)+','+str(old_velocity[2])+','+str(old_velocity[3])+','+str(old_velocity[4])+')'
    ans = NP_sendcmd(cmd,motor,1)    
    #tmp = ans.split(b',')
    #print(ans)
    #print(float(tmp[1])) 
    return ans

def NP_initialize(motor):
    cmd = 'GroupInitialize(Group'+str(motor)+')'
    NP_sendcmd(cmd,0,1)

def NP_home(motor):
    cmd = 'GroupHomeSearch(Group'+str(motor)+')'
    NP_sendcmd(cmd,0,1)

def NP_initialize_and_home(motor):
    # this is to run the initializeation and homing in sequence waiting it to finish it
    status = NP_getStatus(motor)
    if status < 10:
        NP_initialize(motor)
        NP_home(motor) 

def NP_close(NP_sockets):
    for i in NP_sockets:
        i.close()