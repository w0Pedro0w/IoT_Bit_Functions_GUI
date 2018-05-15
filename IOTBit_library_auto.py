import serial
import time
import struct
import subprocess

def Getmills():
    mills = int(round(time.time()*1000))
    return mills


class Modem:

    ''' Set up the system only works if no other ttyUSB ports are on board'''
    def __init__(self, UARTPort, APN):
        self.APN = APN
        self.end = '\r'
        try:
            output = subprocess.check_output("ls /dev/ttyUSB*",shell=True)


            GPS = output[13:25]
            AT = output[26:38]
            PPP = output[39:51]
            Audio = output[52:64]
            
            self.GPSPort = serial.Serial(GPS, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)
            self.ATPort = serial.Serial(AT, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)
            self.PPPPort = serial.Serial(PPP, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)
            self.AudioPort = serial.Serial(Audio, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)
            #self.PassthroughPort = serial.Serial(UARTPort, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)

            
        except: 
            print ('Modem not connected via USB')
            
    ''' Function to Send commands via the serial interface. '''
    ''' Waits for a response and returns the respons if there is one. '''
    def sendATcmd(self, ATcmd, Timeout):
        # Modify the ATcmd so that it has the end of line character 
        cmd = ATcmd + self.end
        # Send the cmd to the device 
        self.ATPort.write(cmd)
        time.sleep(0.01)
        # Check the serial buffer to see if there is a response waiting  
        bytestoread = self.ATPort.inWaiting()
        # While timeout not reached keep checking buffer    
        if (bytestoread == 0):
            curtime = Getmills()
            while (bytestoread == 0) & ((Getmills()-curtime)<Timeout):
                bytestoread = self.ATPort.inWaiting()
                # Store the response 
            self.response = self.ATPort.read(bytestoread)
                
        else:
            self.response = self.ATPort.read(bytestoread)

    
    ''' Function to read the a port to see if there data is waiting to be read.'''
    def ReadPort(self, Port, timeout):
        bytestoread = Port.inWaiting()
        if (bytestoread == 0):
            curtime = Getmills()
            while (bytestoread == 0) & ((Getmills()-curtime)<Timeout):
                bytestoread = Port.inWaiting()
            # Store the response 
            response = Port.read(bytestoread)
        else:
            response = Port.read(bytestoread)
        return response
    ''' Check the modem is responding then check if it is registered to the network, finally set the APN '''
    def SimcomInit(self):
        q = '"'
        cmd = 'AT'
        msg = self.sendATcmd(cmd,10)
        if 'OK' in msg:
            print 'Module Responding'
        else:
            print 'Check Modem'
        cmd = 'AT+CREG?'
        msg = self.sendATcmd(cmd,10)
        if '+CREG 0,1' in msg or '+CREG 0,5' in msg:
            print 'Found Network'
        else:
            print 'Check Modem'
            
        cmd = 'AT+CGSOCKCONT=1,"IP",'
        cmd = cmd + q + self.APN + q
        msg = self.sendATcmd(cmd,10)
        if 'OK' in msg:
            print 'APN set'
        else:
            print 'Check APN'
        cmd = 'AT+CSOCKSETPN=1'
        msg = self.sendATcmd(cmd,10)
        print msg

    ''' Function to start the GPS in Standalone mode '''
    ''' Modes can be 0,1 and 2 for cold, hot or normal start.'''
    def StartGPS_S(self, mode):
        print ' Configuring ....'
        ''' Set the NMEA port to output GLNOass and SPRS data'''
        self.sendATcmd('AT+CGPSNMEA=3',100)
        if 'OK' in self.response:
            print 'NMEA Port configured'
        else:
            print self.response
        time.sleep(0.01)
        ''' Make sure the GPS is actually off'''
        self.sendATcmd('AT+CGPS=0',100)
        if 'OK' in self.response:
            print 'Resetting GPS'
        else:
            print self.response
        time.sleep(0.01)
        ''' Check which mode has been chosen to turn on GPS'''
        if mode == 0:
            self.sendATcmd('AT+CGPSCOLD',100)
            if 'OK' in self.response:
                print ' Cold starting GPS'
            else:
                print self.response
        elif mode == 1:
            self.sendATcmd('AT+CGPSHOT',100)
            if 'OK' in self.response:
                print ' Hot starting GPS'
            else:
                print self.response
        elif mode == 2:
            self.sendATcmd('AT+CGPS=1',100)
            if 'OK' in self.response:
                print ' Starting GPS'
            else:
                print self.response
        else:
            print "Mode not set"
        time.sleep(0.01)

    ''' Fuction to turn off the GPS '''
    def StopGPS(self):
        self.sendATcmd('AT+CGPS=0',1)
        if 'OK' in self.response:
                print ' Stopping GPS'
        else:
                print self.response
        time.sleep(0.01)

    ''' Function to get current GPS information from the nmea port'''
    def GetGPSposition(self):
        self.GPS = self.sendATcmd('AT+CGPSINFO',1)
        return self.GPS

    ''' Function to Send an sms '''
    def SendSMS(self, number, message):
        print 'Configuring Modem for SMS...'
        self.sendATcmd('AT+CMGF=1',1)
        time.sleep(0.01)
        self.sendATcmd('AT+CPMS="SM","SM","SM"',1)
        time.sleep(0.01)
        self.sendATcmd('AT+CNMI=2,1',1)
        time.sleep(0.01)
        print 'Sending SMS ...'
        q = '"'
        cmd = 'AT+CMGSO='
        cmd = cmd + q + number + q + ',' + q + message + q
        msg = self.sendATcmd(cmd,5000)
        if 'OK' in msg:
            print ' Sending successful'

        else:
            print ' Sending Unsuccessful'
    ''' Function to read the sms in storage, if index is 0 print all msgs '''    
    def ReadSMS(self, index):
        if index == 0:
            self.content = self.sendATcmd('AT+CMGL="ALL"',1000)
        elif index > 0:
            cmd = 'AT+CMGR=' 
            index = str(index - 1)
            cmd = cmd + index
            self.content = self.sendATcmd(cmd,3000)

        return self.content
    
    ''' Function to delete an sms in storeage, index refers to the position of the message'''
    def DeleteSMS(self, index):
        cmd = 'AT+CMGD='
        index = str(index)
        cmd = cmd + index
        print (cmd)
        self.content = self.sendATcmd(cmd,100)
        return self.content    
    ''' Function to make a call'''
    def MakeCall(self, number):
        cmd = 'ATD'
        cmd = cmd + number + ';'
        self.sendATcmd(cmd, 1)
        print 'Calling...'
        
    ''' Function to hang up a call'''
    def Hangup(self):
        print ' Hanging up...'
        self.sendATcmd('ATH',1)
    ''' Test if the modem is responding'''
    def Test(self):
        self.sendATcmd('AT',100)
    
    ''' Function to send a HTTP Get request'''
    def HTTP_Get(self,APN,Host,Port,Resource):
        q = '"'
        done = 0
        cmd = 'AT+NETOPEN'
        msg = self.sendATcmd(cmd,100)
        print msg
        cmd = 'AT+CIPHEAD=1'
        msg = self.sendATcmd(cmd,100)
        print msg
        cmd = 'AT+CHTTPACT='
        cmd = cmd + q + Host + q + ',' + Port
        msg = self.sendATcmd(cmd,10)
        print msg
        time.sleep(4)
        cmd = 'GET /'+ Resource + ' HTTP/1.1' + self.end + 'Host: ' + Host + self.end + 'connection: Keep-alive' + self.end + 'Content-Length: 0' + self.end
        print cmd
        self.ATPort.write(cmd)
        time.sleep(0.01)
        message = "1a".decode("hex")
        self.ATPort.write(message)
        while '+CHTTPACT: 0' not in msg:
            msg = self.ReadPort(100)
            print msg
            time.sleep(.1)        
        cmd = 'AT+NETCLOSE'
        msg = self.sendATcmd(cmd,100)
        print msg 

    def CheckSIM(self):
        msg = self.sendATcmd('AT+CPIN?',100)
        if 'OK' in msg:
            print 'SIM inserted'
        else:
            print 'SIM not inserted'
            
    ''' Function to Send commands via the serial interface. '''
    ''' Waits for a response and returns the respons if there is one. '''
    ''' Usable only with firmware verison 1.5'''
    def sendATcmdUART(self, ATcmd, Timeout):
        # Modify the ATcmd so that it has the end of line character
        
        cmd = ATcmd + self.end
        
        # Wait for modem to be ready
        ready = ""
        ready = self.PassthroughPort.readline()
        #print ready
        if 'Modem Ready' in ready:
            self.PassthroughPort.write('P')
            '''
            Sendtimeout = ""
            Sendtimeout = self.PassthroughPort.readline()
            print Sendtimeout
            if 'Send Timeout' in Sendtimeout:               
                self.PassthroughPort.write(str(Timeout))
                '''
            Sendcmd = ""
            Sendcmd = self.PassthroughPort.readline()
            #print Sendcmd
            if 'Send CMD' in Sendcmd:
                # Send the cmd to the device 
                self.PassthroughPort.write(cmd)
                #time.sleep((Timeout/1000))
                # Check the serial buffer to see if there is a response waiting
        
                bytestoread = self.PassthroughPort.inWaiting()
                # While timeout not reached keep checking buffer    
                if (bytestoread == 0):
                    curtime = Getmills()
                    while (bytestoread == 0) & ((Getmills()-curtime)<Timeout):
                        bytestoread = self.PassthroughPort.inWaiting()
                        time.sleep(0.15)
                    #print bytestoread
                    # Store the response 
                    self.response = self.PassthroughPort.read(bytestoread)
                    #print bytestoread
                        
                else:      
                    self.response = self.PassthroughPort.readline()
            else:
                print 'Cmd not sent'
            '''
            else:
                 print 'No Timeout cmd'
                 '''
        else:
            print 'Modem not ready'
            
    ''' Function reset the modem, usable only with firmware verison 1.5'''
    def ResetModem(self):
    # Wait for modem to be ready
        ready = ""
        ready = self.PassthroughPort.readline()
        print ready
        if 'Modem Ready' in ready:
            self.PassthroughPort.write('R')
            time.sleep(15)
            bytestoread = self.PassthroughPort.inWaiting()
            # While timeout not reached keep checking buffer    
            if (bytestoread == 0):
                curtime = Getmills()
                while (bytestoread == 0) & ((Getmills()-curtime)<1000):
                    bytestoread = self.PassthroughPort.inWaiting()
                    time.sleep(0.15)
            #print bytestoread
            # Store the response 
                self.response = self.PassthroughPort.read(bytestoread)
                print bytestoread
                        
            else:      
                self.response = self.PassthroughPort.readline()     
            
                
    ''' Reset the IOTBit'''
    def ResetAll(self):
        # Wait for modem to be ready
        ready = ""
        ready = self.PassthroughPort.readline()
        print ready
        if 'Modem Ready' in ready:
            self.PassthroughPort.write('S')
    '''    
    def StatusGSM(self):
        self.sendATcmd('AT+MONI?',1000)

    def StatusLTE(self):
        self.sendATcmd('AT+CMGSI=4',1000)
        
    def ResetSIM(self):
        self.sendATcmd('AT+CRESET', 1000)

    def PoweroffSIM(self):
        self.sendATcmd('AT+CPOF', 1000)
    '''
