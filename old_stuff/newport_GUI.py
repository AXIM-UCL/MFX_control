# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 15:25:57 2018

@author: AAstolfo
"""

import newport_functions as NP
import tkinter
from tkinter import ttk


class NP_GUI(ttk.Frame):
    #import Newport_functions
    """The Newport motors GUI and functions."""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()

    def update_positions(self):
        if initialised == 1:
            
            #Check the status of the motors
            status1 = NP.NP_getStatus(1)
            status2 = NP.NP_getStatus(2)
            status3 = NP.NP_getStatus(3)
            status4 = NP.NP_getStatus(4)            
            
            pos1 = NP.NP_gp(1)
            pos2 = NP.NP_gp(2)
            pos3 = NP.NP_gp(3)
            pos4 = NP.NP_gp(4)
            #pos5 = NP.NP_gp(5)
            
            #print(pos2)
            #time.sleep(1)
            if status1 > 10:
                self.M1_pos.config(text=str(round(pos1,6)))
            else:
                self.M1_pos.config(text='Status = '+str(status1))
            if status2 > 10:
                self.M2_pos.config(text=str(round(pos2,6)))
            else:
                self.M2_pos.config(text='Status = '+str(status2))                
            if status3 > 10:
                self.M3_pos.config(text=str(round(pos3,6)))
            else:
                self.M3_pos.config(text='Status = '+str(status3))                  
            if status4 > 10:
                self.M4_pos.config(text=str(round(pos4,6)))
            else:
                self.M4_pos.config(text='Status = '+str(status4))                  
                
            #self.M2_pos.config(text=str(round(pos2,6)))
            #self.M3_pos.config(text=str(round(pos3,6)))
            #self.M4_pos.config(text=str(round(pos4,6)))
            #self.M5_pos.config(text=str(round(pos5,6)))
            #message=Read_SoakTests_Gunshop_func.RunIt(path)
            #print(message)     
            #self.answer_label6['text'] = message[6]#'Done!'
        else:
            self.M1_pos.config(text='Not connected')
            self.M2_pos.config(text='Not connected')
            self.M3_pos.config(text='Not connected')
            self.M4_pos.config(text='Not connected')
            #self.M5_pos.config(text='Not connected')
    def update_label(self):
        #self.label.configure(cpuTemp)
        #self.M1_pos.config(text='ciao')
        self.update_positions()
        self.M1_pos.after(1000,self.update_label)

    def sockets_init(self):
        
        global NP_sockets,initialised
        
        NP_sockets = NP.NP_init()
        initialised = 1

    def sockets_close(self):
        
        global initialised        
        NP.NP_close(NP_sockets)
        initialised = 0
        

    def init_gui(self):
        
        global initialised
        
        """Builds GUI."""
        self.root.title('NEWPORT MOTORS')
        self.root.option_add('*tearOff', 'FALSE')

        self.grid(column=0, sticky='nsew')

        self.menubar = tkinter.Menu(self.root)

        self.menu_file = tkinter.Menu(self.menubar)
        self.menu_file.add_command(label='Exit')

        self.menu_edit = tkinter.Menu(self.menubar)

        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')

        self.root.config(menu=self.menubar)

        #self.INIT_button = ttk.Button(self,text="INIT", command = lambda: NP.NP_init())
        self.INIT_button = ttk.Button(self,text="INIT", command = self.sockets_init)
        self.QUIT_button = ttk.Button(self,text="QUIT", command = self.sockets_close)

        self.INIT_button.grid(row = 8, column =2)
        self.QUIT_button.grid(row = 8, column =3)
    
    
        #-----MOTOR 1------
        MOTOR_No = 1
    
        self.M1_label_1 = ttk.Label(self,text = "MOTOR 1")
        self.M1_label_1.config(font='-weight bold')
        self.M1_pos = ttk.Label(self)
        self.M1_pos.after(1000,self.update_label)
        self.M1_label_1.grid(row = 0, column =1)
        self.M1_pos.grid(row=1,column =1)
        self.M1_label_2 = ttk.Label(self,text = "Move ABS [mm]")
        self.M1_Entry_1 = ttk.Entry(self)
        self.M1_label_3 = ttk.Label(self,text = "Move REL [mm]")
        self.M1_Entry_2 = ttk.Entry(self)
        
        self.M1_button_1 = ttk.Button(self,text="<", command = lambda: NP.NP_mr(1,'-'+self.M1_Entry_2.get()))
        self.M1_button_2 = ttk.Button(self,text=">", command = lambda: NP.NP_mr(1,self.M1_Entry_2.get()))
        self.M1_button_3 = ttk.Button(self,text="STOP", command = lambda: NP.NP_stop(1))
        self.M1_button_4 = ttk.Button(self,text="HOME", command = lambda: NP.NP_initialize_and_home(1))
        self.M1_button_5 = ttk.Button(self,text="GO", command = lambda: NP.NP_ma(1,self.M1_Entry_1.get()))
        
        self.M1_label_1.grid(row = 0, column =1+(MOTOR_No-1)*3)
        self.M1_pos.grid(row=1,column =1+(MOTOR_No-1)*3)
        self.M1_label_2.grid(row = 2, column =1+(MOTOR_No-1)*3)
        self.M1_Entry_1.grid(row = 3, column =1+(MOTOR_No-1)*3)
        self.M1_label_3.grid(row = 4, column =1+(MOTOR_No-1)*3)
        self.M1_Entry_2.grid(row = 5, column =1+(MOTOR_No-1)*3)
        self.M1_button_1.grid(row = 5, column =0+(MOTOR_No-1)*3)
        self.M1_button_2.grid(row = 5, column =2+(MOTOR_No-1)*3)
        self.M1_button_3.grid(row = 6, column =1+(MOTOR_No-1)*3)
        self.M1_button_4.grid(row = 7, column =1+(MOTOR_No-1)*3)
        self.M1_button_5.grid(row = 3, column =2+(MOTOR_No-1)*3)
        
        
        #-----MOTOR 2------
        MOTOR_No = 2
        self.M2_label_1 = ttk.Label(self,text = "MOTOR 2")
        self.M2_label_1.config(font='-weight bold')
        self.M2_pos = ttk.Label(self,text = "0.0")
        
        self.M2_label_2 = ttk.Label(self,text = "Move ABS [mm]")
        self.M2_Entry_1 = ttk.Entry(self)
        
        self.M2_label_3 = ttk.Label(self,text = "Move REL [mm]")
        self.M2_Entry_2 = ttk.Entry(self)
        #self.M2_Entry_2.insert(0, "0.00011")
        
        self.M2_button_1 = ttk.Button(self,text="<", command = lambda: NP.NP_mr(2,'-'+self.M2_Entry_2.get()))
        self.M2_button_2 = ttk.Button(self,text=">", command = lambda: NP.NP_mr(2,self.M2_Entry_2.get()))
        self.M2_button_3 = ttk.Button(self,text="STOP", command = lambda: NP.NP_stop(2) )
        self.M2_button_4 = ttk.Button(self,text="HOME", command = lambda: NP.NP_initialize_and_home(2) )
        self.M2_button_5 = ttk.Button(self,text="GO", command = lambda: NP.NP_ma(2,self.M2_Entry_1.get()))
        
        self.M2_label_1.grid(row = 0, column =1+(MOTOR_No-1)*3)
        self.M2_pos.grid(row=1,column =1+(MOTOR_No-1)*3)
        self.M2_label_2.grid(row = 2, column =1+(MOTOR_No-1)*3)
        self.M2_Entry_1.grid(row = 3, column =1+(MOTOR_No-1)*3)
        self.M2_label_3.grid(row = 4, column =1+(MOTOR_No-1)*3)
        self.M2_Entry_2.grid(row = 5, column =1+(MOTOR_No-1)*3)
        self.M2_button_1.grid(row = 5, column =0+(MOTOR_No-1)*3)
        self.M2_button_2.grid(row = 5, column =2+(MOTOR_No-1)*3)
        self.M2_button_3.grid(row = 6, column =1+(MOTOR_No-1)*3)
        self.M2_button_4.grid(row = 7, column =1+(MOTOR_No-1)*3)
        self.M2_button_5.grid(row = 3, column =2+(MOTOR_No-1)*3)


        #-----MOTOR 3------
        MOTOR_No = 3
        self.M3_label_1 = ttk.Label(self,text = "MOTOR 3")
        self.M3_label_1.config(font='-weight bold')
        self.M3_pos = ttk.Label(self,text = "0.0")
        
        self.M3_label_2 = ttk.Label(self,text = "Move ABS [mm]")
        self.M3_Entry_1 = ttk.Entry(self)
        
        self.M3_label_3 = ttk.Label(self,text = "Move REL [mm]")
        self.M3_Entry_2 = ttk.Entry(self)
        
        self.M3_button_1 = ttk.Button(self,text="<", command = lambda: NP.NP_mr(3,'-'+self.M3_Entry_2.get()))
        self.M3_button_2 = ttk.Button(self,text=">", command = lambda: NP.NP_mr(3,self.M3_Entry_2.get()))
        self.M3_button_3 = ttk.Button(self,text="STOP", command = lambda: NP.NP_stop(3) )
        self.M3_button_4 = ttk.Button(self,text="HOME", command = lambda: NP.NP_initialize_and_home(3) )
        self.M3_button_5 = ttk.Button(self,text="GO", command = lambda: NP.NP_ma(3,self.M3_Entry_1.get()))
        
        self.M3_label_1.grid(row = 0, column =1+(MOTOR_No-1)*3)
        self.M3_pos.grid(row=1,column =1+(MOTOR_No-1)*3)
        self.M3_label_2.grid(row = 2, column =1+(MOTOR_No-1)*3)
        self.M3_Entry_1.grid(row = 3, column =1+(MOTOR_No-1)*3)
        self.M3_label_3.grid(row = 4, column =1+(MOTOR_No-1)*3)
        self.M3_Entry_2.grid(row = 5, column =1+(MOTOR_No-1)*3)
        self.M3_button_1.grid(row = 5, column =0+(MOTOR_No-1)*3)
        self.M3_button_2.grid(row = 5, column =2+(MOTOR_No-1)*3)
        self.M3_button_3.grid(row = 6, column =1+(MOTOR_No-1)*3)
        self.M3_button_4.grid(row = 7, column =1+(MOTOR_No-1)*3)
        self.M3_button_5.grid(row = 3, column =2+(MOTOR_No-1)*3)

        #-----MOTOR 4------
        MOTOR_No = 4
        self.M4_label_1 = ttk.Label(self,text = "MOTOR 4")
        self.M4_label_1.config(font='-weight bold')
        self.M4_pos = ttk.Label(self,text = "0.0")
        
        self.M4_label_2 = ttk.Label(self,text = "Move ABS [mm]")
        self.M4_Entry_1 = ttk.Entry(self)
        
        self.M4_label_3 = ttk.Label(self,text = "Move REL [mm]")
        self.M4_Entry_2 = ttk.Entry(self)
        
        self.M4_button_1 = ttk.Button(self,text="<", command = lambda: NP.NP_mr(4,'-'+self.M4_Entry_2.get()))
        self.M4_button_2 = ttk.Button(self,text=">", command = lambda: NP.NP_mr(4,self.M4_Entry_2.get()))
        self.M4_button_3 = ttk.Button(self,text="STOP", command = lambda: NP.NP_stop(4) )
        self.M4_button_4 = ttk.Button(self,text="HOME", command = lambda: NP.NP_initialize_and_home(4) )
        self.M4_button_5 = ttk.Button(self,text="GO", command = lambda: NP.NP_ma(4,self.M4_Entry_1.get()))
        
        self.M4_label_1.grid(row = 0, column =1+(MOTOR_No-1)*3)
        self.M4_pos.grid(row=1,column =1+(MOTOR_No-1)*3)
        self.M4_label_2.grid(row = 2, column =1+(MOTOR_No-1)*3)
        self.M4_Entry_1.grid(row = 3, column =1+(MOTOR_No-1)*3)
        self.M4_label_3.grid(row = 4, column =1+(MOTOR_No-1)*3)
        self.M4_Entry_2.grid(row = 5, column =1+(MOTOR_No-1)*3)
        self.M4_button_1.grid(row = 5, column =0+(MOTOR_No-1)*3)
        self.M4_button_2.grid(row = 5, column =2+(MOTOR_No-1)*3)
        self.M4_button_3.grid(row = 6, column =1+(MOTOR_No-1)*3)
        self.M4_button_4.grid(row = 7, column =1+(MOTOR_No-1)*3)
        self.M4_button_5.grid(row = 3, column =2+(MOTOR_No-1)*3)

        #-----MOTOR 5------
# =============================================================================
#         MOTOR_No = 5
#         self.M5_label_1 = ttk.Label(self,text = "MOTOR 5")
#         self.M5_label_1.config(font='-weight bold')
#         self.M5_pos = ttk.Label(self,text = "0.0")
#         
#         self.M5_label_2 = ttk.Label(self,text = "Move ABS [mm]")
#         self.M5_Entry_1 = ttk.Entry(self)
#         
#         self.M5_label_3 = ttk.Label(self,text = "Move REL [mm]")
#         self.M5_Entry_2 = ttk.Entry(self)
#         
#         self.M5_button_1 = ttk.Button(self,text="<", command = lambda: NP.NP_mr(5,'-'+self.M5_Entry_2.get()))
#         self.M5_button_2 = ttk.Button(self,text=">", command = lambda: NP.NP_mr(5,self.M5_Entry_2.get()))
#         self.M5_button_3 = ttk.Button(self,text="STOP", command = lambda: NP.NP_stop(5) )
#         self.M5_button_4 = ttk.Button(self,text="HOME", command = lambda: NP.NP_home(5) )
#         self.M5_button_5 = ttk.Button(self,text="GO", command = lambda: NP.NP_ma(5,self.M5_Entry_1.get()))
#         
#         self.M5_label_1.grid(row = 0, column =1+(MOTOR_No-1)*3)
#         self.M5_pos.grid(row=1,column =1+(MOTOR_No-1)*3)
#         self.M5_label_2.grid(row = 2, column =1+(MOTOR_No-1)*3)
#         self.M5_Entry_1.grid(row = 3, column =1+(MOTOR_No-1)*3)
#         self.M5_label_3.grid(row = 4, column =1+(MOTOR_No-1)*3)
#         self.M5_Entry_2.grid(row = 5, column =1+(MOTOR_No-1)*3)
#         self.M5_button_1.grid(row = 5, column =0+(MOTOR_No-1)*3)
#         self.M5_button_2.grid(row = 5, column =2+(MOTOR_No-1)*3)
#         self.M5_button_3.grid(row = 6, column =1+(MOTOR_No-1)*3)
#         self.M5_button_4.grid(row = 7, column =1+(MOTOR_No-1)*3)
#         self.M5_button_5.grid(row = 3, column =2+(MOTOR_No-1)*3)
# =============================================================================

        initialised = 0

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

if __name__ == '__main__':
    root = tkinter.Tk()
    NP_GUI(root)
    root.mainloop()
