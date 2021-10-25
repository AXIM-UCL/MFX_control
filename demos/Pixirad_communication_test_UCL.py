# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 12:17:17 2021

@author: L Brombal
"""

from source.BTCTDetectors.PEPIPixirad import PEPIPixieIII
from source.BTCTProcessing.PEPITIFFIO import PEPITIFFWriter

try:
    det = PEPIPixieIII()    
    out = PEPITIFFWriter(asynchronous=False)
    
    det.set_param("E0_KEV",7.0)
    det.set_param("E1_KEV",200.0)
    det.set_param("MODE","NONPI")        
    det.set_param("COL","1COL0")
    det.set_param("SHOTS",1)
    det.set_param("EXP_TIME_MILLISEC",1000)

    det.initialize()
    print(det)
    img, _ = det.acquire()
    out.save(img, r"C:\Data\21_10_19\dummy.tif", metadata_list=(det,))


except Exception as e:
    print("Something went wrong: " + str(e))

finally:
    det.terminate(dethermalize=True)

