#!/usr/bin/env python

'''
ps3revolution.py Drive the Brookstone Rover Revolution via the P3 Controllerj

Copyright (C) 2014 Simon D. Levy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

# You may want to adjust these for your own controller
BUTTON_STEALTH     = 'z'  # Circle button toggles stealth mode
BUTTON_TURRET      = 'x'  # Square button toggles turret camera
# AXIS don't need: WASD - for move car, IJKL - for turret
#AXIS_PAN_HORZ      = 0  # Left joystick controls turret pan
#AXIS_PAN_VERT      = 1  #  and tilt

# Avoid button bounce by enforcing lag between button events
MIN_BUTTON_LAG_SEC = 0.3

# Avoid close-to-zero values on axis
MIN_AXIS_ABSVAL    = 0.01

# Threshold for faster speed
SPEED_THRESH       = 0.5

# For FFPLAY 
FRAMERATE          = 20
#DELAY_SEC          = 2.5

import time
import cv2
import ffmpeg
#import tempfile
import numpy as np

from rover import Revolution

wheeldir, steerdir, goslow = 0, 0, 1

# Supports CTRL-C to override threads
#def _signal_handler(signal, frame):
#    frame.f_locals['rover'].close()
#    sys.exit(0)

# Rover subclass for PS3 + OpenCV
class CVRover(Revolution):

    def __init__(self, tmpfile):

        # Set up basics
        Revolution.__init__(self)
        self.wname = 'Rover Revolution'

         # Defaults on startup: no stealth; driving camera
        self.stealthIsOn = False #True
        self.usingTurret = False #True

        # Tracks button-press times for debouncing
        self.lastButtonTime = 0

        # Saves data to video file for display
        self.tmpfile = tmpfile

    # Automagically called by Rover class
    def processVideo(self, h264bytes, timestamp_msec):
        # Send video through pipe
        #self.tmpfile.write(h264bytes)
        self.tmpfile.stdin.write(h264bytes)

# main -----------------------------------------------------------------------------------

if __name__ == '__main__':

    width, height = 640, 480

    #process = tempfile.NamedTemporaryFile()
    #process = tempfile.NamedTemporaryFile(mode='w+b', bufsize=0 , suffix='.avi', prefix='RoverRev',
    #                                       dir='\Python27\RoverRev_WinPylot', delete=False)
    # Create a OpenCV Rover object
    rover = CVRover((
        ffmpeg
            .input('pipe:')
            .video
            .output('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{width}x{height}')
            .run_async(pipe_stdin=True, pipe_stdout=True)
    ))

    # Wait a few seconds, then being playing the tmp video file
    #time.sleep(DELAY_SEC)

    while True:
        in_bytes = rover.tmpfile.stdout.read(height * width * 3)

        # transform the byte read into a numpy array
        in_frame = (
            np
            .frombuffer(in_bytes, np.uint8)
            .reshape([height, width, 3])
        )

        # Display the frame
        cv2.imshow('in_frame', in_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            break
        elif key == ord(BUTTON_STEALTH):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                rover.stealthIsOn = not rover.stealthIsOn;
                if(rover.stealthIsOn):
                    print('Stealth mode On')
                    rover.turnStealthOn()
                else:
                    print('Stealth mode Off')
                    rover.turnStealthOff()
        elif key == ord(BUTTON_TURRET):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                rover.usingTurret = not rover.usingTurret;
                if(rover.usingTurret):
                    print('Turret Camera')
                    rover.useTurretCamera()
                else:
                    print('Driving Camera')
                    rover.useDrivingCamera()
        elif key == ord('w'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                steerdir = 0
                wheeldir = 1
        elif key == ord('s'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                steerdir = 0
                wheeldir = -1
        elif key == ord('d'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                steerdir = 1
                wheeldir = -1
        elif key == ord('a'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                steerdir = -1
                wheeldir = -1
        elif key == ord('q'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                steerdir = -1
                wheeldir = 1
        elif key == ord('e'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                steerdir = 1
                wheeldir = 1
        elif key == ord('l'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                hr = -1
        elif key == ord('j'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                hr = 1
        elif key == ord('k'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                vr = -1
        elif key == ord('i'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                vr = 1
        elif key == ord('t'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                goslow = 1 - goslow
                if(goslow):
                    print('Slow mode')
                else:
                    print('Speed mode')
        else:
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                steerdir, wheeldir = 0, 0
                hr, vr = 0, 0

        rover.moveCameraHorizontal(hr)
        rover.moveCameraVertical(vr)
        # Shut down Rover
        rover.drive(wheeldir, steerdir, goslow)
    rover.close()