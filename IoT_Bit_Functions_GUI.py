from IOTBit_library_auto import Modem
from time import sleep
#from tkinter import *
from Tkinter import *
import serial
import time
import struct
import subprocess
import RPi.GPIO as GPIO
import time
import ast

APN = 'everywhere'
_4G = Modem('USB',APN)


class Application(Frame):
    """GUI  app with 3 Buttons"""
    def __init__(self, master):
        """Initialize the frame"""
        Frame.__init__(self,master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Create phone number box"""
        
        self.instruction1 = Label (self, text = "Phone number:")
        self.instruction1.grid(row = 0, column = 0, sticky = E)

        self.e = Entry(self)
        self.e.grid(row = 0, column = 1, sticky = W)

        self.m = Entry(self)
        self.m.grid(row = 1, column = 1, sticky = W)
        
        self.f = Entry(self)
        self.f.grid(row = 2, column = 1, sticky = W)

        self.g = Entry(self)
        self.g.grid(row = 3, column = 1, sticky = W) 
        
        self.submit_button = Button(self, text = "Send SMS   ", command = self.reveal)
        self.submit_button.grid(row = 1, column = 0, sticky = E)

        self.submit_button = Button(self, text = "Display SMS", command = self.show)
        self.submit_button.grid(row = 2, column = 0, sticky = E)

        self.submit_button = Button(self, text = "      Signal Quality       ", command = self.Signal_check)
        self.submit_button.grid(row = 1, column = 3, sticky = W)
        
        self.submit_button = Button(self, text = "Set GPIO to HIGH/LOW", command = self.Set_Pins)
        self.submit_button.grid(row = 0, column = 3, sticky = W)

        self.submit_button = Button(self, text = "Delete SMS ", command = self.DeleteSMS)
        self.submit_button.grid(row = 3, column = 0, sticky = E)

        self.submit_button = Button(self, text = "Make Call", command = self.Make_Call)
        self.submit_button.grid(row = 0, column = 2, sticky = W)

        self.submit_button = Button(self, text = " Hang up ", command = self.Hang_Up)
        self.submit_button.grid(row = 1, column = 2, sticky = W)
        
        self.text1 = Text(self, width = 50, height = 25, wrap = WORD)
        self.text1.grid(row = 4, column = 0, columnspan = 2)

        self.text = Text(self, width = 50, height = 25, wrap = WORD)
        self.text.grid(row = 4, column = 2, columnspan = 2)
        self.text.insert(0.0,'Instructions:\n Input the phone number you want to send an SMS\n or make a call,with the country prefix at the start.\n Type your SMS into the second entry box.\n \nTo Display SMS:\n Type 0 to display all SMS.\n Type the corresponding number to each sms\n individually i.e. 1 = First SMS, 2 = second SMS\n \nTo Delete SMS:\n 0 to delete only SMS stored at storage location.\n 1 to ignore index and delete all\n   "recived read".\n 2 to ignore the index value and delete all\n   "recived read" and "stored sent".\n 3 to ignore index value and delete all\n   "recived read", "stored Sent" and \n   "stored unsent".\n 4 to delete all SMS.  ')
        self.text.config(state=DISABLED)
        self.text.config(background = "grey")
        



    def Make_Call(self):
        self.call = self.e.get()
        _4G.MakeCall(self.call)

        self.text.delete(0.0, END)
        self.text.insert(0.0,_4G.response)
        
    def Hang_Up(self):
        _4G.Hangup()
        
    def DeleteSMS(self):
        self.remove = self.g.get()
        cmd = 'AT+CMGD='
        index = str(self.remove)
        cmd = cmd + index
        _4G.sendATcmd(cmd,100)
        
        self.text.delete(0.0, END)
        self.text.insert(0.0,_4G.response)
        
    def reveal(self):
        """Display _4G.response after sending SMS"""
        self.number = self.e.get()
        
        self.message = self.m.get()

        _4G.SendSMS(self.number,self.message)
       
        self.text.delete(0.0, END)
        self.text.insert(0.0,_4G.response)

    def show(self):
        """ Display SMS to be read"""

        self.display = self.f.get()
       
        _4G.ReadSMS(int(self.display))
        
        
        self.text1.delete(0.0, END)
        self.text1.insert(0.0,_4G.response)
        
    def Signal_check(self):

        '''See Signal Quality'''
        
    
        _4G.sendATcmd('AT+CSQ',1000)
        
        signal = _4G.response    

        if (',' in _4G.response[8:10]):
            signal = signal.replace(',','')
            signal = int(signal[8:9])
        else:
            signal = int(_4G.response[8:10])
        
        if (signal < 10):
            signal = "Poor Signal"
        elif(signal > 10 | signal < 14):
            signal = "OK Signal"
        elif(signal > 14 | signal < 20):
            signal = "Good Signal"
        elif(signal >= 20 | signal < 99):
            signal = "Exceptional Signal"
        elif(signal >= 99):
            signal = "No Connection"

        self.text1.delete(0.0, END)
        self.text1.insert(0.0,signal)
            
        
    def Set_Pins(self):

        '''Set pins to high or low depending on the SMS'''
        
        _4G.ReadSMS(0)
        sleep(2)
    
        REC = '"REC READ"'
        counter = 0

        for i, _ in enumerate(_4G.response):
            if _4G.response[i:i + len(REC)] == REC:
             counter += 1
            
        _4G.ReadSMS(counter)
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        if 'PIN26H' in _4G.response:
           
           GPIO.setup(26,GPIO.OUT)
           GPIO.output(26,GPIO.HIGH)

        elif 'PIN26L' in _4G.response:
        
           GPIO.setup(26,GPIO.OUT)
           GPIO.output(26,GPIO.LOW)

        elif 'PIN19H' in _4G.response:
        
           GPIO.setup(19,GPIO.OUT)
           GPIO.output(26,GPIO.HIGH)

        elif 'PIN19L' in _4G.response:
        
           GPIO.setup(19,GPIO.OUT)
           GPIO.output(19,GPIO.LOW)

        elif 'PIN13H' in _4G.response:
        
           GPIO.setup(13,GPIO.OUT)
           GPIO.output(13,GPIO.HIGH)

        elif 'PIN13L' in _4G.response:
        
           GPIO.setup(13,GPIO.OUT)
           GPIO.output(13,GPIO.LOW)

        else:
            print("NO Signals Sent")

        self.text1.delete(0.0, END)
        self.text1.insert(0.0,_4G.response)


root = Tk()
root.title("IoT Bit Functions")
root.geometry("725x425")
app = Application(root)

root.mainloop()
