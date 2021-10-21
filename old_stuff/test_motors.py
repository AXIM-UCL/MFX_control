# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 16:38:26 2021

@author: XPCI_BT
"""

import tools_pi
import numpy as np
import time

N_proj=360
proj0=0
angle0=-90
#Piezo motors initial positions
sample_xin=6.0
sample_z=0.0
sample_y=-8.7
#Position for flat field measurement
sample_xout=-5.0

angles=angle0+np.linspace(proj0*360/N_proj,360,N_proj-proj0+1)#, endpoint=False) #Angles for the projections

#Connect the motors and move to starting point
piezo=tools_pi.connect_piezo()
print('Moving sample to starting point')
tools_pi.move_theta_abs(piezo, angles[0])
tools_pi.move_x_abs(piezo, sample_xin)
tools_pi.move_y_abs(piezo, sample_y)
tools_pi.move_z_abs(piezo, sample_z)
print('Done')

x_poss=[]
theta_poss=[]

for angle in angles:         
    tools_pi.move_theta_abs(piezo, angle)
    t=time.time()
    xs=[];ts=[]
    while(time.time()-t<3):
        xs.append(tools_pi.get_x_sample(piezo))
        ts.append(tools_pi.get_theta_sample(piezo))
    proj0+=1
    x_poss.append(xs)
    theta_poss.append(ts)