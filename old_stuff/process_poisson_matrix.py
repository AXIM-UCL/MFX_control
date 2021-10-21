# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 05:16:17 2021

@author: XPCI_BT
"""
import sys
sys.path.insert(1, r'C:\Users\XPCI_BT\Documents\GitHub\MFX_control')

import tools_pixirad
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson
from scipy.stats import chisquare
from scipy.stats import chi2
import matplotlib.patches as patches

def rebin(raw_freq, raw_edges):
    i=0
    obs=[]
    edg=[]
    edg.append(raw_edges[0])
    while (i < np.size(raw_freq)):
        cur=raw_freq[i]
        j=i+1
        while (cur < 5 and j<np.size(raw_freq)):
            cur+=raw_freq[j]
            j+=1
        edg.append(raw_edges[j])
        obs.append(cur)
        i=j
    obs=np.array(obs); edg=np.array(edg)
    return obs, edg

def chi_square(f_obs, f_exp, ddof):
    chi=0
    raw_dof=0
    for i in range(np.size(f_exp)):
        if(f_exp[i] >= 5):
            chi+=(f_obs[i]-f_exp[i])**2/f_exp[i]
            raw_dof+=1
    dof=raw_dof-1-ddof
    pvalue=1 - chi2.cdf(chi, df=dof)
    return chi, pvalue, dof

def filter_exp_freq(f_obs, f_exp, middles):
    fo=[];fe=[];m=[]
    for i in range(np.size(f_exp)):
        if(f_exp[i]>=5):
            fo.append(f_obs[i]); fe.append(f_exp[i]); m.append(middles[i])
    fo=np.array(fo); fe=np.array(fe); m=np.array(m)
    fraction=np.size(fe)/np.size(f_exp)
    return fo, fe, m, fraction

def choose_poisson(matrix, mask):
    rows, cols= matrix.shape
    list_pixels=[]
    for r in range (rows):
        for c in range (cols):
            if(mask[r,c]==1):
                list_pixels.append(matrix[r,c])
    array_pixels=np.array(list_pixels)
    fraction_poisson=np.size(array_pixels)/np.size(matrix)
    return array_pixels, fraction_poisson

def clean_pixels(matrix):
    vec=matrix.ravel()
    list_pixels=[]
    mu=np.mean(matrix)
    std=np.std(matrix)
    for i in range (np.size(vec)):
        if(abs(vec[i]-mu)<=(2*std)):
            list_pixels.append(vec[i])
    array_pixels=np.array(list_pixels)
    fraction_poisson=np.size(array_pixels)/np.size(matrix)
    return array_pixels, fraction_poisson
            

folder=r'C:\\Data\\08_12_20\\Thresholds\\'
FF_name='FF_40kVp_250uA_512x1s_7keV_88cm_thermalON_2.dat'
RAW_name='FF_40kVp_250uA_512x1s_7keV_88cm_thermalON_1.dat'
N_ff=32
N_raw=10
frames_ff, sum_ff=tools_pixirad.read_Pixirad_data(folder+FF_name, N_ff)
frames_raw, sum_raw=tools_pixirad.read_Pixirad_data(folder+RAW_name, N_raw)
alpha=0.05
imp_pvalues=np.load(r'C:\Data\08_12_20\Results_per_pixel\pvalues_7kev.npy')
out=np.where(imp_pvalues>alpha, 1, 0)

media=np.sum(sum_ff*out)/np.sum(out)#[100:200, 100:200])
FF=sum_ff/np.mean(sum_ff)
raw=frames_raw[:,:,5]
ffc=raw/FF
rows, cols = sum_ff.shape
sq_width=51


fig,ax = plt.subplots(1, figsize=(12,5))
im=ax.imshow(ffc, vmin=np.mean(ffc)-3*np.std(ffc), vmax=np.mean(ffc)+3*np.std(ffc), cmap='gray');#fig.colorbar(im, ax=ax)
ax.set_title('TH0 = 7 keV, FF # = ' + str(N_ff) + r', $\alpha$ = '+str(alpha))

#rows, cols = sum_ff.shape
pvalues=np.zeros((rows, cols))
fractions=np.zeros((rows, cols))
for i in range(int(sq_width/2), rows-int(sq_width/2)):
    for j in range(int(sq_width/2), cols-int(sq_width/2)):
        #sub_mat=ffc[i-int(sq_width/2):i+int(sq_width/2), j-int(sq_width/2):j+int(sq_width/2)]
        #pixels=sub_mat.ravel()
        sub_raw=raw[i-int(sq_width/2):i+int(sq_width/2), j-int(sq_width/2):j+int(sq_width/2)]
        sub_ff=sum_ff[i-int(sq_width/2):i+int(sq_width/2), j-int(sq_width/2):j+int(sq_width/2)]
        sub_ff=sub_ff/np.mean(sub_ff)
        sub_mat=sub_raw/sub_ff
        pixels, fp=choose_poisson(sub_mat, out[i-int(sq_width/2):i+int(sq_width/2), j-int(sq_width/2):j+int(sq_width/2)])
        pixels,fp=clean_pixels(pixels)
        mu=np.mean(pixels)
        sigma=np.std(pixels) 
        fo, b=np.histogram(pixels, bins='auto')#, range=(mu-2*sigma, mu+2*sigma))
        obs_freq, bin_edges=rebin(fo, b)
        bin_middles = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        #mu2=np.sum(obs_freq*bin_middles)/np.sum(obs_freq)
        poisson_cdf=poisson.cdf(bin_edges, mu)
        exp_freq=(poisson_cdf[1:] - poisson_cdf[:-1])*np.size(pixels)
        obs_freq, exp_freq, bin_middles, frac=filter_exp_freq(f_obs=obs_freq, f_exp=exp_freq, middles=bin_middles)
        chi_sq, pvalue=chisquare(f_obs=obs_freq, f_exp=exp_freq, ddof=1)
        pvalues[i,j]=pvalue
        fractions[i,j]=frac
        #rect = patches.Rectangle((col_lims[j],row_lims[i]),sq_width-2,sq_width-2,linewidth=1,edgecolor=color,facecolor='none')
        #ax.add_patch(rect)
        
plt.figure()
plt.hist(pixels, bins=bin_edges, label='Observed')
plt.plot(bin_middles, exp_freq, label='Expected')
plt.annotate('p-value= '+str(np.around(pvalue, 4)), xy=(0.75, 0.75), xycoords='axes fraction')
plt.legend()


result=np.where(pvalues>=alpha, 1, 0)
perc=np.sum(result)/((rows-sq_width)*(cols-sq_width))*100
plt.figure(figsize=(12,5))
plt.imshow(result, cmap=plt.cm.get_cmap('viridis', 2)); plt.colorbar()
plt.title('TH0 = 7 keV, FF # = ' + str(N_ff) + r', $\alpha$ = '+str(alpha) + ', 50x50 window, ' + str(np.around(perc, 2)) + '% Poisson')
