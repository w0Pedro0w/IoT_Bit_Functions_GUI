import picamera
from subprocess import call
from datetime import datetime
from time import sleep

Filepath = "/home/pi/Vid_recorded/"
Currenttime = datetime.now()
Pictime = Currenttime.strftime("%Y.%m.%d-%H%M%S")
picName = Pictime + '.h264'
completefilepath = Filepath + picName
with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.start_recording(completefilepath)
    sleep(10)
    print("Video Recorded")
    camera.stop_recording()
