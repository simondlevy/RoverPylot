#!/usr/bin/env python

'''
ps3rover.py Drive the Brookstone Rover 2.0 via the P3 Controller, displaying
the streaming video using OpenCV.

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

# You may want to adjust these buttons for your own controller
BUTTON_GDRIVE    =   8  # Select button toggle G-Drive
BUTTON_QUIT     =    9  # Start button quits
BUTTON_LIGHTS   =    3  # Square button toggles lights
BUTTON_INFRARED =    1  # Circle button toggles infrared
BUTTON_CAMERA_UP =   0  # Triangle button raises camera
BUTTON_CAMERA_DOWN = 2  # X button lowers camera

# Avoid button bounce by enforcing lag between button events
MIN_BUTTON_LAG_SEC = 0.5

# Avoid close-to-zero values on axis
MIN_AXIS_ABSVAL    = 0.01


import rover
import cvutils
import time
import pygame
import sys
import signal
                                   
        
# Supports CTRL-C to override threads
def _signal_handler(signal, frame):
    frame.f_locals['rover'].close()
    sys.exit(0)

# Try to start OpenCV for video
try:
    import cv
except:
    cv = None

# Rover subclass for PS3 + OpenCV
class PS3Rover(rover.Rover):

    def __init__(self):

        # Set up basics
        rover.Rover.__init__(self)
        self.wname = 'Rover 2.0'
        self.quit = False

        # Set up controller using PyGame
        pygame.display.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

         # Defaults on startup: lights off, ordinary camera
        self.lightsAreOn = False
        self.infraredIsOn = False

        # Tracks button-press times for debouncing
        self.lastButtonTime = 0

        # Try to create OpenCV named window
        try:
            if cv:
                cv.NamedWindow(self.wname, cv.CV_WINDOW_AUTOSIZE )
            else:
                pass
        except:
            pass

    # Automagically called by Rover class
    def processVideo(self, jpegbytes):

        # Update controller events
        pygame.event.pump()    

        # Quit on Start button
        if self.controller.get_button(BUTTON_QUIT):
            self.quit = True

        # Toggle lights    
        self.lightsAreOn  = self.checkButton(self.lightsAreOn, BUTTON_LIGHTS, rover.turnLightsOn, rover.turnLightsOff)   
            
        # Toggle night vision (infrared camera)    
        self.infraredIsOn = self.checkButton(self.infraredIsOn, BUTTON_INFRARED, rover.turnInfraredOn, rover.turnInfraredOff)   
        # Move camera up/down    
        if self.controller.get_button(BUTTON_CAMERA_UP):  
            self.moveCamera(1)
        elif self.controller.get_button(BUTTON_CAMERA_DOWN): 
            self.moveCamera(-1)
        else:
            self.moveCamera(0)
            
        # Set treads based on axes        
        self.setTreads(self.axis(1), self.axis(3))

        # Display video image if possible
        try:
            if cv:
                image = cvutils.jpegbytes_to_cvimage(jpegbytes)    
                cv.ShowImage(self.wname, image )
                cv.WaitKey(1)    
            else:
                pass
        except:
            pass
        
        
    # Converts Y coordinate of specified axis to +/-1 or 0
    def axis(self, index):
        
        value = -self.controller.get_axis(index)
        
        if value > MIN_AXIS_ABSVAL:
            return 1
        elif value < -MIN_AXIS_ABSVAL:
            return -1
        else:
            return 0


    # Handles button bounce by waiting a specified time between button presses   
    def checkButton(self, flag, buttonID, onRoutine=None, offRoutine=None):
        if self.controller.get_button(buttonID):
            if (time.time() - self.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                self.lastButtonTime = time.time()
                if flag:
                    if offRoutine:
                        offRoutine()
                    flag = False
                else:
                    if onRoutine:
                        onRoutine()
                    flag = True
        return flag
        
# main -----------------------------------------------------------------------------------

if __name__ == '__main__':

    # Create a PS3 Rover object
    rover = PS3Rover()

    # Set up signal handler for CTRL-C
    signal.signal(signal.SIGINT, _signal_handler)

    # Loop until user hits quit button on controller
    while not rover.quit:
        pass

    # Shut down Rover
    rover.close()



