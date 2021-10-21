# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 01:58:50 2021

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

def filter_exp_freq(f_obs, f_exp, middles):
    fo=[];fe=[];m=[]
    for i in range(np.size(f_exp)):
        if(f_exp[i]>5):
            fo.append(f_obs[i]); fe.append(f_exp[i]); m.append(middles[i])
    fo=np.array(fo); fe=np.array(fe); m=np.array(m)
    fraction=np.size(fe)/np.size(f_exp)
    return fo, fe, m, fraction

folder=r'C:\\Data\\08_12_20\\Thresholds\\'
name='FF_40kVp_250uA_512x1s_1keV_88cm_thermalON_1.dat'
full_name=folder+name
N_samples=512
frames, sums=tools_pixirad.read_Pixirad_data(full_name, N_samples)
rows, cols = sums.shape

pvalues=np.zeros((rows, cols))
fractions=np.zeros((rows, cols))

for r in range(rows):
    for c in range(cols):
        pixel=frames[r,c,:]
        mu=np.mean(pixel)
        fo, b=np.histogram(pixel, bins='auto')#, range=(mu-3*sigma, mu+3*sigma))
        obs_freq, bin_edges=rebin(fo, b)
        bin_middles = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        poisson_cdf=poisson.cdf(bin_edges, mu)
        exp_freq=(poisson_cdf[1:] - poisson_cdf[:-1])*np.size(pixel)
        obs_freq, exp_freq, bin_middles, frac=filter_exp_freq(f_obs=obs_freq, f_exp=exp_freq, middles=bin_middles)     
        chi_sq, pvalue=chisquare(f_obs=obs_freq, f_exp=exp_freq,ddof=1)
        pvalues[r,c]=pvalue
        fractions[r,c]=frac

#%%
alpha=0.01
out=np.where(pvalues>=alpha, 1, 0)
total=np.sum(out)
perc=round(total/(rows*cols)*100,1)
plt.figure(figsize=(12, 5));plt.imshow(out, cmap=plt.cm.get_cmap('viridis', 2));
plt.title('TH0 = 1 keV, Poisson = ' + str(perc) + ' %' + r', $\alpha$ = '+str(alpha))

#np.save(r'C:\Data\08_12_20\Results_binning_filtering\pvalues_9kev.npy', pvalues)              
        
# #%%

# plt.figure()
# plt.hist(pixel, bins=bin_edges, label='Observed')
# plt.plot(bin_middles, exp_freq, label='Expected')
# plt.annotate('p-value= '+str(np.around(pvalue, 2)), xy=(0.75, 0.75), xycoords='axes fraction')
# plt.legend()

#%%
plt.figure(figsize=(12, 5));plt.imshow(sums, cmap='gray');
plt.colorbar(); plt.title('Flat-field image - 9keV')

f=np.where(fractions>0.8,1,0)
print(np.sum(f)/np.size(f))