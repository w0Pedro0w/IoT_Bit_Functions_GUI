from IOTBit_library_auto import Modem
import subprocess
import RPi.GPIO as GPIO
import time
APN = 'everywhere'
_4G = Modem('USB',APN)

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

        print(_4G.response)



Set_Pins()
