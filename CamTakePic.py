import picamera
from datetime import datetime

filePath = "/home/pi/Pics_Taken/"

currentTime = datetime.now()
picTime = currentTime.strftime("%Y.%m.%d-%H%M%S")
picName = picTime + '.jpg'
completeFilePath = filePath + picName
with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.capture(completeFilePath)
    print ("pic Taken")
    
