from IOTBit_library_auto import Modem
import subprocess
import RPi.GPIO as GPIO
import time
import picamera
import os
from time import sleep

APN = 'everywhere'
_4G = Modem('USB',APN)
        
_4G.ReadSMS(0)
sleep(2)
    
REC = '"REC READ"'
counter = 0
camera = picamera.PiCamera()
camera.close()

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

elif 'TakePicture' in _4G.response:
        
        os.system('sudo python3 CamTakePic.py')

elif 'StartRecording' in _4G.response:

        os.system('sudo python3 Record_Vid.py')
        
