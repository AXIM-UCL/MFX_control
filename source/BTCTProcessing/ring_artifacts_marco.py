# -*- coding: utf-8 -*-
"""
Created on Sun Oct 31 10:07:27 2021

@author: XPCI_BT
"""

import numpy as np 
import os
import tifffile
import statistics
import time
import matplotlib.pyplot as plt

folder=r'C:\Data\21_10_25\2BTCT_900proj_calib_phantom\Sinograms_Att\\'
file='sino0000.tif'

Isinos=tifffile.imread(folder+file)s
Isinos=np.rot90(Isinos)

[a,b] =np.shape(Isinos)


Fsinos = (np.fft.fft2(Isinos))
Fsino = np.real(np.fft.fft2(Isinos));

[af, bf] = np.shape(Fsino);


plt.figure()
plt.imshow(Isinos)
