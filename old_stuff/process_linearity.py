# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 21:44:40 2021

@author: XPCI_BT
"""

import tools_pixirad
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def read_images(direc, list_files):
    num_files=len(list_files)
    imgs=np.zeros((402,1024,num_files))
    for i in range(num_files):
        frs, sums=tools_pixirad.read_Pixirad_data(folder+list_files[i], 1)
        imgs[:,:,i]=sums
    return imgs

folder=r'C:\\Data\\20_12_08\\Linearity-ThermalON\\'
files_40=['FF_40kVp_70uA_2s_7keV_88cm_thermalON.dat', 'FF_40kVp_130uA_2s_7keV_88cm_thermalON.dat', 'FF_40kVp_190uA_2s_7keV_88cm_thermalON.dat', 'FF_40kVp_250uA_2s_7keV_88cm_thermalON.dat']
curs_40=np.array([70, 130, 190, 250]).reshape((-1, 1))
imgs_40=read_images(folder, files_40)

files_50=['FF_50kVp_50uA_2s_7keV_88cm_thermalON.dat', 'FF_50kVp_100uA_2s_7keV_88cm_thermalON.dat', 'FF_50kVp_150uA_2s_7keV_88cm_thermalON.dat', 'FF_50kVp_200uA_2s_7keV_88cm_thermalON.dat']
curs_50=np.array([50, 100, 150, 200]).reshape((-1, 1))
imgs_50=read_images(folder, files_50)

files_70=['FF_70kVp_50uA_2s_7keV_88cm_thermalON.dat', 'FF_70kVp_80uA_2s_7keV_88cm_thermalON.dat', 'FF_70kVp_110uA_2s_7keV_88cm_thermalON.dat', 'FF_70kVp_140uA_2s_7keV_88cm_thermalON.dat']
curs_70=np.array([50, 80, 110, 140]).reshape((-1, 1))
imgs_70=read_images(folder, files_70)

mean_40_1=np.mean(imgs_40[100:300,100:300,:], axis=(0,1))
std_er_40_1=np.std(imgs_40[100:300,100:300,:], axis=(0,1))/np.sqrt(np.size(imgs_40[100:300,100:300,0]))
mean_50_1=np.mean(imgs_50[100:300,100:300,:], axis=(0,1))
std_er_50_1=np.std(imgs_50[100:300,100:300,:], axis=(0,1))/np.sqrt(np.size(imgs_50[100:300,100:300,0]))
mean_70_1=np.mean(imgs_70[100:300,100:300,:], axis=(0,1))
std_er_70_1=np.std(imgs_70[100:300,100:300,:], axis=(0,1))/np.sqrt(np.size(imgs_70[100:300,100:300,0]))


model40 = LinearRegression().fit(curs_40, mean_40_1)
y_pred_40 = model40.predict(curs_40)
r2_40_1 = model40.score(curs_40, mean_40_1)

model50 = LinearRegression().fit(curs_50, mean_50_1)
y_pred_50 = model50.predict(curs_50)
r2_50_1 = model50.score(curs_50, mean_50_1)

model70 = LinearRegression().fit(curs_70, mean_70_1)
y_pred_70 = model70.predict(curs_70)
r2_70_1 = model70.score(curs_70, mean_70_1)



plt.figure()
plt.errorbar(curs_40, mean_40_1, yerr=std_er_40_1,linestyle='None',fmt='o',capsize=3,label='40kVp')
plt.plot(curs_40, y_pred_40, linestyle='--', c='k', label='Linear fit')
plt.annotate(r'$R^2$= '+str(np.around(r2_40_1, 5)), xy=(curs_40[2]+10, mean_40_1[2]-150))

plt.errorbar(curs_50, mean_50_1, yerr=std_er_50_1,linestyle='None',capsize=3,fmt='o',label='50kVp')
plt.plot(curs_50, y_pred_50, linestyle='--', c='k')
plt.annotate(r'$R^2$= '+str(np.around(r2_50_1, 5)), xy=(curs_50[2]+10, mean_50_1[2]-150))

plt.errorbar(curs_70, mean_70_1, yerr=std_er_70_1,linestyle='None',capsize=3,fmt='o',label='70kVp')
plt.plot(curs_70, y_pred_70, linestyle='--', c='k')
plt.annotate(r'$R^2$= '+str(np.around(r2_70_1, 5)), xy=(curs_70[2]+10, mean_70_1[2]-150))

plt.xlabel(r'Current ($\mu$A)')
plt.ylabel('No. of counts')
plt.legend()


mean_40_2=np.mean(imgs_40[100:300,700:900,:], axis=(0,1))
std_er_40_2=np.std(imgs_40[100:300,700:900,:], axis=(0,1))/np.sqrt(np.size(imgs_40[100:300,100:300,0]))
mean_50_2=np.mean(imgs_50[100:300,700:900,:], axis=(0,1))
std_er_50_2=np.std(imgs_50[100:300,700:900,:], axis=(0,1))/np.sqrt(np.size(imgs_50[100:300,100:300,0]))
mean_70_2=np.mean(imgs_70[100:300,700:900,:], axis=(0,1))
std_er_70_2=np.std(imgs_70[100:300,700:900,:], axis=(0,1))/np.sqrt(np.size(imgs_70[100:300,100:300,0]))


model40_2 = LinearRegression().fit(curs_40, mean_40_2)
y_pred_40_2 = model40.predict(curs_40)
r2_40_2 = model40.score(curs_40, mean_40_2)

model50_2 = LinearRegression().fit(curs_50, mean_50_2)
y_pred_50_2 = model50.predict(curs_50)
r2_50_2 = model50.score(curs_50, mean_50_2)

model70_2 = LinearRegression().fit(curs_70, mean_70_2)
y_pred_70_2 = model70.predict(curs_70)
r2_70_2 = model70.score(curs_70, mean_70_2)



plt.figure()
plt.errorbar(curs_40, mean_40_2, yerr=std_er_40_2,linestyle='None',fmt='o',capsize=3,label='40kVp')
plt.plot(curs_40, y_pred_40_2, linestyle='--', c='k', label='Linear fit')
plt.annotate(r'$R^2$= '+str(np.around(r2_40_2, 5)), xy=(curs_40[2]+10, mean_40_2[2]-150))

plt.errorbar(curs_50, mean_50_2, yerr=std_er_50_2,linestyle='None',capsize=3,fmt='o',label='50kVp')
plt.plot(curs_50, y_pred_50_2, linestyle='--', c='k')
plt.annotate(r'$R^2$= '+str(np.around(r2_50_2, 5)), xy=(curs_50[2]+10, mean_50_2[2]-150))

plt.errorbar(curs_70, mean_70_2, yerr=std_er_70_2,linestyle='None',capsize=3,fmt='o',label='70kVp')
plt.plot(curs_70, y_pred_70_2, linestyle='--', c='k')
plt.annotate(r'$R^2$= '+str(np.around(r2_70_2, 5)), xy=(curs_70[2]+10, mean_70_2[2]-150))

plt.xlabel(r'Current ($\mu$A)')
plt.ylabel('No. of counts')
plt.legend()



# data_50=imgs_50[r,c,:]
# model50 = LinearRegression().fit(curs_50, mean_50_1)
# y_pred_50 = model50.predict(curs_50)
# out_r2[r,c,1] = model50.score(curs_50, data_50)

# data_70=imgs_70[r,c,:]
# model70 = LinearRegression().fit(curs_70, data_70)
# y_pred_70 = model70.predict(curs_70)
# out_r2[r,c,2] = model70.score(curs_70, data_70)44
# rows, cols=(402,1024)
# out_r2=np.zeros((rows,cols,3))

# for r in range(rows):
#     for c in range(cols):
#         data_40=imgs_40[r,c,:]
#         model40 = LinearRegression().fit(curs_40, data_40)
#         y_pred_40 = model40.predict(curs_40)
#         out_r2[r,c,0] = model40.score(curs_40, data_40)
        
#         data_50=imgs_50[r,c,:]
#         model50 = LinearRegression().fit(curs_50, data_50)
#         y_pred_50 = model50.predict(curs_50)
#         out_r2[r,c,1] = model50.score(curs_50, data_50)
        
#         data_70=imgs_70[r,c,:]
#         model70 = LinearRegression().fit(curs_70, data_70)
#         y_pred_70 = model70.predict(curs_70)
#         out_r2[r,c,2] = model70.score(curs_70, data_70)

# plt.figure()
# plt.scatter(curs_40, data_40, label='Obs-40kVp')
# plt.plot(curs_40, y_pred_40, label='Fit-40kVp')
# plt.scatter(curs_50, data_50, label='Obs-50kVp')
# plt.plot(curs_50, y_pred_50, label='Fit-50kVp')
# plt.scatter(curs_70, data_70, label='Obs-70kVp')
# plt.plot(curs_70, y_pred_70, label='Fit-70kVp')
# plt.xlabel(r'Current ($\mu$A)')
# plt.ylabel('No. of counts')
# plt.legend()


#file_name='FF_40kVp_250uA_512x1s_7keV_88cm_thermalON_2.dat'
#frames_ff, sum_ff=tools_pixirad.read_Pixirad_data(folder+file_name, N_ff)