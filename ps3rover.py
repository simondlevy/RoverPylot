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
BUTTON_LIGHTS   =    0  # Square button toggles lights
BUTTON_INFRARED =    2  # Circle button toggles infrared
BUTTON_CAMERA_UP =   3  # Triangle button raises camera
BUTTON_CAMERA_DOWN = 1  # X button lowers camera

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

def _signal_handler(signal, frame):
    frame.f_locals['rover'].close()
    sys.exit(0)

# Try to start OpenCV for video
try:
    import cv
except:
    cv = None

# Handler passed to Rover constructor
class PS3Rover(rover.Rover):
            
    def processVideo(self, jpegbytes):
                            
        try:
                    
            if cv:
                
                image = cvutils.jpegbytes_to_cvimage(jpegbytes)    
                wname = 'Rover 2.0'                       
                cv.NamedWindow(wname, cv.CV_WINDOW_AUTOSIZE )
                cv.ShowImage(wname, image )
                cv.WaitKey(5)    
                
            else:
                pass
            
        except:
            
            pass
        
        
# Converts Y coordinate of specified axis to +/-1 or 0
def _axis(index):
    
    value = -controller.get_axis(index)
    
    if value > MIN_AXIS_ABSVAL:
        return 1
    elif value < -MIN_AXIS_ABSVAL:
        return -1
    else:
        return 0


# Handles button bounce by waiting a specified time between button presses   
def _checkButton(controller, lastButtonTime, flag, buttonID, \
    onRoutine=None, offRoutine=None):
    if controller.get_button(buttonID):
        if (time.time() - lastButtonTime) > MIN_BUTTON_LAG_SEC:
            lastButtonTime = time.time()
            if flag:
                if offRoutine:
                    offRoutine()
                flag = False
            else:
                if onRoutine:
                    onRoutine()
                flag = True
    return lastButtonTime, flag
    

# Set up controller using PyGame
pygame.display.init()
pygame.joystick.init()
controller = pygame.joystick.Joystick(0)
controller.init()
 
# Create a PS3 Rover object
rover = PS3Rover()

# Defaults on startup: lights off, ordinary camera
lightsAreOn = False
infraredIsOn = False

# Tracks button-press times for debouncing
lastButtonTime = 0

# Set up signal handler for CTRL-C
signal.signal(signal.SIGINT, _signal_handler)

# Loop till Quit hit
while True:
        
    # Force joystick polling
    pygame.event.pump()    
    
    # Quit on Start button
    if controller.get_button(BUTTON_QUIT):
        break
        
    # Toggle lights    
    lastButtonTime, lightsAreOn  = \
        _checkButton(controller, lastButtonTime,  \
            lightsAreOn, BUTTON_LIGHTS, rover.turnLightsOn, rover.turnLightsOff)   
        
    # Toggle night vision (infrared camera)    
    lastButtonTime, infraredIsOn = \
        _checkButton(controller, lastButtonTime, \
            infraredIsOn, BUTTON_INFRARED, rover.turnInfraredOn, rover.turnInfraredOff)   
        
    # Move camera up/down    
    if controller.get_button(BUTTON_CAMERA_UP):  
        rover.moveCamera(1)
    elif controller.get_button(BUTTON_CAMERA_DOWN): 
        rover.moveCamera(-1)
    else:
        rover.moveCamera(0)
        
        
    # Set treads based on axes        
    rover.setTreads(_axis(1), _axis(3))
                
# Shut down Rover
rover.close()




