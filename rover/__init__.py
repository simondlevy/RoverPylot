'''
Python classes for interacting with the Brookstone Rover 2.0  
and Rover Revolution

Copyright (C) 2015 Simon D. Levy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

import struct
import sys
import threading
import socket
import time

from .blowfish import Blowfish
from .adpcm import decodeADPCMToPCM
from .byteutils import *
    
class Rover:

    def __init__(self):
        ''' Creates a Rover object that you can communicate with. 
        '''
      
        self.HOST = '192.168.1.100'
        self.PORT = 80
        
        TARGET_ID = 'AC13'
        TARGET_PASSWORD = 'AC13'      
        
        self.TREAD_DELAY_SEC = 1
        self.KEEPALIVE_PERIOD_SEC = 60
        
                            
        # Create command socket connection to Rover      
        self.commandsock = self._newSocket()
        
        # Send login request with four arbitrary numbers
        self._sendCommandIntRequest(0, [0, 0, 0, 0])
                
        # Get login reply
        reply = self._receiveCommandReply(82)
                
        # Extract Blowfish key from camera ID in reply
        cameraID = reply[25:37].decode('utf-8')
        key = TARGET_ID + ':' + cameraID + '-save-private:' + TARGET_PASSWORD
        
        # Extract Blowfish inputs from rest of reply
        L1 = bytes_to_int(reply, 66)
        R1 = bytes_to_int(reply, 70)
        L2 = bytes_to_int(reply, 74)
        R2 = bytes_to_int(reply, 78)
        
        # Make Blowfish cipher from key
        bf = _RoverBlowfish(key)
        
        # Encrypt inputs from reply
        L1,R1 = bf.encrypt(L1, R1)
        L2,R2 = bf.encrypt(L2, R2)
        
        # Send encrypted reply to Rover
        self._sendCommandIntRequest(2, [L1, R1, L2, R2])     
        
        # Ignore reply from Rover
        self._receiveCommandReply(26)
        
        # Start timer task for keep-alive message every 60 seconds
        self._startKeepaliveTask()
        
       
        # Set up vertical camera controller
        self.cameraVertical = _RoverCamera(self, 1)
                      
        # Send video-start request
        self._sendCommandIntRequest(4, [1])       
        
        # Get reply from Rover
        reply = self._receiveCommandReply(29)
                
        # Create media socket connection to Rover      
        self.mediasock = self._newSocket()

        # Send video-start request based on last four bytes of reply
        if sys.version_info < (3, 0):
            self._sendRequest(self.mediasock, 'V', 0, 4, map(ord, reply[25:]))
        else:
            self._sendRequest(self.mediasock, 'V', 0, 4, reply[25:])

        # Send audio-start request
        self._sendCommandByteRequest(8, [1])
        
        # Ignore audio-start reply
        self._receiveCommandReply(25)
        
        # Receive images on another thread until closed
        self.is_active = True
        self.reader_thread = _MediaThread(self)
        self.reader_thread.start()
            
        
    def close(self):
        ''' Closes off commuincation with Rover.
        '''
        
        self.keepalive_timer.cancel()
        
        self.is_active = False
        self.commandsock.close()
        
        if self.mediasock:
            self.mediasock.close()

    def turnStealthOn(self):    
        ''' Turns on stealth mode (infrared).
        '''
        self._sendCameraRequest(94)  
        
    
    def turnStealthOff(self):   
        ''' Turns off stealth mode (infrared).
        '''
        self._sendCameraRequest(95)   

    def moveCameraVertical(self, where):
        ''' Moves the camera up or down, or stops moving it.  A nonzero value for the 
            where parameter causes the camera to move up (+) or down (-).  A
            zero value stops the camera from moving.
        '''
        self.cameraVertical.move(where)

    def _startKeepaliveTask(self,):
        self._sendCommandByteRequest(255)
        self.keepalive_timer = \
            threading.Timer(self.KEEPALIVE_PERIOD_SEC, self._startKeepaliveTask, [])
        self.keepalive_timer.start()

    def _sendCommandByteRequest(self, id, _bytes=[]):
        self._sendCommandRequest(id, len(_bytes), _bytes)
        
    def _sendCommandIntRequest(self, id, intvals):
        bytevals = []
        for val in intvals:
            for c in struct.pack('I', val):
                if sys.version_info < (3,0):
                    bytevals.append(ord(c))
                else:
                    bytevals.append(c)

        self._sendCommandRequest(id, 4*len(intvals), bytevals)       

    def _sendCommandRequest(self, id, n, contents):
        self._sendRequest(self.commandsock, 'O', id, n, contents)

    def _sendRequest(self, sock, c, id, n, contents):                  
        if sys.version_info < (3, 0):
            _bytes = [ord('M'), ord('O'), ord('_'), ord(c), id, \
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, n, 0, 0, 0, 0, 0, 0, 0]
            _bytes.extend(contents)
            request = ''.join(map(chr, _bytes))
        else:
            request = bytearray([ord('M'), ord('O'), ord('_'), ord(c), id, \
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, n, 0, 0, 0, 0, 0, 0, 0])
            request.extend(bytearray(contents))
        sock.send(request)

    def _receiveCommandReply(self, count):
        reply = self.commandsock.recv(count)
        return reply
        
    def _newSocket(self):
        sock = socket.socket()
        sock.bind(('192.168.1.1',0))
        sock.connect((self.HOST, self.PORT)) 
        return sock

    def _sendDeviceControlRequest(self, a, b) : 
        self._sendCommandByteRequest(250, [a,b])

    def _sendCameraRequest(self, request):
        self._sendCommandByteRequest(14, [request]) 
         
           
class Rover20(Rover):

    def __init__(self):

        Rover.__init__(self)
        
        # Set up treads
        self.leftTread = _RoverTread(self, 4)
        self.rightTread = _RoverTread(self, 1)
     
    def close(self):
        ''' Closes off commuincation with Rover.
        '''

        Rover.close(self)
        
        # Stop moving treads
        self.setTreads(0, 0)
                
    def getBatteryPercentage(self):
        ''' Returns percentage of battery remaining.
        '''
        self._sendCommandByteRequest(251)
        reply = self._receiveCommandReply(32)
        return 15 * ord(reply[23])    
        
    def setTreads(self, left, right):
        ''' Sets the speed of the left and right treads (wheels).  + = forward;
        - = backward; 0 = stop. Values should be in [-1..+1].
        ''' 
        currTime = time.time()
        
        self.leftTread.update(left)
        self.rightTread.update(right)
      
    def turnLightsOn(self):    
        ''' Turns the headlights and taillights on.
        '''
        self._setLights(8)   
        
    
    def turnLightsOff(self):   
        ''' Turns the headlights and taillights off.
        '''
        self._setLights(9)    
        
    def _setLights(self, onoff):    
        self._sendDeviceControlRequest(onoff, 0)

    def processVideo(self, jpegbytes, timestamp_10msec):
        ''' Proccesses bytes from a JPEG image streamed from Rover.  
            Default method is a no-op; subclass and override to do something 
            interesting.
        '''
        pass
        
    def processAudio(self, pcmsamples, timestamp_10msec):
        ''' Proccesses a block of 320 PCM audio samples streamed from Rover.  
            Audio is sampled at 8192 Hz and quantized to +/- 2^15.
            Default method is a no-op; subclass and override to do something 
            interesting.
        '''
        pass
        
   
       
    def _spinWheels(self, wheeldir, speed):    
        # 1: Right, forward
        # 2: Right, backward
        # 4: Left, forward
        # 5: Left, backward        
        self._sendDeviceControlRequest(wheeldir, speed) 
    
  
class Revolution(Rover):

    def __init__(self):

        Rover.__init__(self)

        self.steerdir_prev = 0
        self.command_prev = 0
        self.goslow_prev = 0
        
        self.using_turret = False

        # Set up vertical camera controller
        self.cameraHorizontal = _RoverCamera(self, 5)
 
    def drive(self, wheeldir, steerdir, goslow):

        goslow = 1 if goslow else 0

        command = 0

        if wheeldir == +1 and steerdir ==  0:
            command = 1
        if wheeldir == -1 and steerdir ==  0:
            command = 2
        if wheeldir ==  0 and steerdir == +1:
            command = 4
        if wheeldir ==  0 and steerdir == -1:
            command = 5
        if wheeldir == +1 and steerdir == -1:
            command = 6
        if wheeldir == +1 and steerdir == +1:
            command = 7
        if wheeldir == -1 and steerdir == -1:
            command = 8
        if wheeldir == -1 and steerdir == +1:
            command = 9

        if steerdir == 0 and self.steerdir_prev != 0:
            command = 3

        if command != self.command_prev or goslow != self.goslow_prev:
            self._sendDeviceControlRequest(command, goslow) 

        self.steerdir_prev = steerdir
        self.command_prev = command
        self.goslow_prev = goslow

    def processVideo(self, imgbytes, timestamp_msec):
        ''' Proccesses bytes from an image streamed from Rover.  
            Default method is a no-op; subclass and override to do something 
            interesting.
        '''
        pass
            
    def processAudio(self, audiobytes, timestamp_msec):
        ''' Proccesses a block of 1024 PCM audio samples streamed from Rover.  
            Audio is sampled at 8192 Hz and quantized to +/- 2^15.
            Default method is a no-op; subclass and override to do something 
            interesting.
        '''
        pass

    def useTurretCamera(self):    
        '''  Switches to turret camera.
        '''
        self._sendUseCameraRequest(1)
         
    
    def useDrivingCamera(self):   
        '''  Switches to driving camera.
        '''
        self._sendUseCameraRequest(2)

    def moveCameraHorizontal(self, where):
        ''' Moves the camera up or down, or stops moving it.  A nonzero value for the 
            where parameter causes the camera to move up (+) or down (-).  A
            zero value stops the camera from moving.
        '''
        self.cameraHorizontal.move(where)
 
    def _sendUseCameraRequest(self, camera):
        self._sendCommandByteRequest(19, [6, camera])
   
# "Private" classes ===========================================================
        
# A special Blowfish variant with P-arrays set to zero instead of digits of Pi
class _RoverBlowfish(Blowfish):
    
    def __init__(self, key):
        
        ORIG_P = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self._keygen(key, ORIG_P)


# A thread for reading streaming media from the Rover
class _MediaThread(threading.Thread):
    
    def __init__(self, rover):
        
        threading.Thread.__init__(self)
        
        self.rover = rover
        self.BUFSIZE = 1024
          
    def run(self):
                                    
        # Accumulates media bytes
        mediabytes = ''
                            
        # Starts True; set to False by Rover.close()       
        while self.rover.is_active:
            
            # Grab bytes from rover, halting on failure            
            try:
                buf = self.rover.mediasock.recv(self.BUFSIZE)
            except:
                break

            # Do we have a media frame start?
            if sys.version_info < (3, 0):
                k = buf.find('MO_V')
            else:
                k = buf.find(b'MO_V')

            # Yes
            if k  >= 0:

                # Already have media bytes?
                if len(mediabytes) > 0:
                    
                    # Yes: add to media bytes up through start of new
                    mediabytes += buf[0:k]

                    # Both video and audio messages are time-stamped in 10msec units
                    timestamp = bytes_to_uint(mediabytes, 23)

                    # Video bytes: call processing routine
                    if sys.version_info < (3,):
                        key_value = ord(mediabytes[4])
                    else:
                        key_value = mediabytes[4]

                    if key_value == 1:
                        self.rover.processVideo(mediabytes[36:], timestamp)

                    # Audio bytes: call processing routine
                    else:
                        audsize = bytes_to_uint(mediabytes, 36)
                        sampend = 40 + audsize
                        offset = bytes_to_short(mediabytes, sampend)
                        if sys.version_info < (3,):
                            index  = ord(mediabytes[sampend+2])
                        else:
                            index = mediabytes[sampend + 2]
                        pcmsamples = decodeADPCMToPCM(mediabytes[40:sampend], offset, index)
                        self.rover.processAudio(pcmsamples, timestamp)                    
                        
                    # Start over with new bytes    
                    mediabytes = buf[k:]
             
                # No media bytes yet: start with new bytes
                else:
                    mediabytes = buf[k:]
            
            # No: accumulate media bytes
            else:
          
                mediabytes += buf

class _RoverTread(object):
    
    def __init__(self, rover, index):
        
        self.rover = rover
        self.index = index
        self.isMoving = False
        self.startTime = 0

    def update(self, value):

        if value == 0:
            if self.isMoving:
                self.rover._spinWheels(self.index, 0)
                self.isMoving = False
        else:
            if value > 0:
                wheel = self.index
            else:
                wheel = self.index + 1
            currTime = time.time()
            if (currTime - self.startTime) > self.rover.TREAD_DELAY_SEC:              
                self.startTime = currTime
                self.rover._spinWheels(wheel, int(round(abs(value)*10)))  
                self.isMoving = True

class _RoverCamera(object):

    def __init__(self, rover, stopcmd):
        
        self.rover = rover
        self.stopcmd = stopcmd
        self.isMoving = False

    def move(self, where):

        if where == 0:
            if self.isMoving:
                self.rover._sendCameraRequest(self.stopcmd)
                self.isMoving = False
        elif not self.isMoving:
            if where == 1:
                self.rover._sendCameraRequest(self.stopcmd-1)
            else:
                self.rover._sendCameraRequest(self.stopcmd+1)
            self.isMoving = True


 


