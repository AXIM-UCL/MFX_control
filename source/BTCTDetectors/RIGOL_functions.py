# -*- coding: utf-8 -*-
"""
Created on Tue 15 Feb 2022

@author: AAstolfo
"""

# this is to control the power supply RIGOL DP832A via USB and SCPI commands

# see also:
    # https://www.rigol-uk.co.uk/jg/wp-content/uploads/2021/08/Rigol-DP800-Power-Supply-Manual.pdf
    # https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DP800_ProgrammingGuide_EN.pdf


import pyvisa as visa
#import time

global unit_address

# unit address as per visa.ResourceManager() to be sure of controlling the right unit
unit_address = 'USB0::0x1AB1::0x0E11::DP8B214301141::INSTR'
unit_IDN = 'RIGOL TECHNOLOGIES,DP832A,DP8B214301141,00.01.16'


def check_COMM():
    # function to check the status of communication

    ans = 0    

    # find the connected devices
    rm = visa.ResourceManager()
    
    unit_list = rm.list_resources()
    
    # check if the address is on the list
    if unit_address in unit_list:
        unit_index = unit_list.index(unit_address)

        try: 
            RIGOL_unit = rm.open_resource(unit_list[unit_index])
            ans = RIGOL_unit.query('*IDN?').strip('\n')
            RIGOL_unit.close()
            #print(ans)
        except:
            print('RIGOL unit not connected')
            ans = 0
    
    # verify the model and serial number are as expectedpower
    if ans == unit_IDN:
        ans = 1

    return ans    
    
    
def check_STATUS():
    # function to check the status of the 3 channels
    
    ans = 0
    
    # find the connected devices
    rm = visa.ResourceManager()
    
    unit_list = rm.list_resources()
    
    if unit_address in unit_list:
        unit_index = unit_list.index(unit_address)

        # check the communication is ok
        if check_COMM() == 1:
            try: 
                RIGOL_unit = rm.open_resource(unit_list[unit_index])
                ans = RIGOL_unit.query(':OUTP? ALL').strip('\n')
                RIGOL_unit.close()
                print('Status = ', ans)
            except:
                pass 

    return ans


def power_ON():
    # function to power ON the 3 channels
    
    # find the connected devices
    rm = visa.ResourceManager()
    
    unit_list = rm.list_resources()
    
    if unit_address in unit_list:
        unit_index = unit_list.index(unit_address)
        
        # check the communication is ok
        if check_COMM() == 1:
            try:
                RIGOL_unit = rm.open_resource(unit_list[unit_index])
                print(RIGOL_unit.query(':OUTP ALL,ON'))
                RIGOL_unit.close()
            except:
                pass
            
            # return when at least one of the channels are on
            power_ON = 0
            while power_ON == 0:
                ans = check_STATUS()
                if 'ON' in ans:
                    power_ON = 1
                    print('Power ON')
    
    
def power_OFF():
    # function to power OFF the 3 channels
    
    # find the connected devices
    rm = visa.ResourceManager()
    
    unit_list = rm.list_resources()
    
    if unit_address in unit_list:
        unit_index = unit_list.index(unit_address)
        
        if check_COMM() == 1:
            try:
                RIGOL_unit = rm.open_resource(unit_list[unit_index])
                print(RIGOL_unit.query(':OUTP ALL,OFF'))
                RIGOL_unit.close()
            except:
                pass

            power_ON = 1
            while power_ON == 1:
                ans = check_STATUS()
                if 'OFF,OFF,OFF' in ans:
                    power_ON = 0
                    print('Power OFF')            
