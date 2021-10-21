# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 00:31:40 2021

@author: XPCI_BT
"""

import sys
sys.path.insert(1, r'C:\Data\21_06_24\\')
import CT_scan

folder='21_06_24\CT_CBphantom_3sph_calibration_'
angles0=[-360]
N_projs=[900]

for i in range(5):
    name=folder+str(N_projs[i]) +'projs//'
    print(name)
    
    CT_scan.run_scan(name, -360, N_projs[i])
