# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 23:01:17 2021

@author: XPCI_BT
"""
import sys
sys.path.insert(1, r'C:\Data\21_06_08\\')
# import CT_scan

# folders=['21_06_08\CT_900_3sphsample_1\\', '21_06_08\CT_900_3sphsample_2\\', '21_06_08\CT_900_3sphsample_3\\', '21_06_08\CT_900_3sphsample_4\\', '21_06_08\CT_360_3sphsample_5\\']

# for folder in folders:
#     CT_scan.run_scan(folder)

folders=[r'C:\Data\21_06_08\CT_360_3sphsample_6\RAW\\', r'C:\Data\21_06_08\CT_360_3sphsample_7\RAW\\', r'C:\Data\21_06_08\CT_360_3sphsample_8\RAW\\', r'C:\Data\21_06_08\CT_900_3sphsample_1\RAW\\', r'C:\Data\21_06_08\CT_900_3sphsample_2\RAW\\', r'C:\Data\21_06_08\CT_900_3sphsample_3\RAW\\', r'C:\Data\21_06_08\CT_900_3sphsample_4\RAW\\']
out_folders=[r'C:\Data\21_06_08\CT_360_3sphsample_6\FFC\\', r'C:\Data\21_06_08\CT_360_3sphsample_7\FFC\\', r'C:\Data\21_06_08\CT_360_3sphsample_8\FFC\\', r'C:\Data\21_06_08\CT_900_3sphsample_1\FFC\\', r'C:\Data\21_06_08\CT_900_3sphsample_2\FFC\\', r'C:\Data\21_06_08\CT_900_3sphsample_3\FFC\\', r'C:\Data\21_06_08\CT_900_3sphsample_4\FFC\\']

N_proj=1

import preprocessing

for i in range(7):
    preprocessing.process_data(folders[i], out_folders[i], N_proj)
    print(folders[i])