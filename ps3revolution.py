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
BUTTON_STEALTH     = 1  # Circle button toggles stealth mode
BUTTON_TURRET      = 3  # Square button toggles turret camera
AXIS_PAN_HORZ      = 0  # Left joystick controls turret pan
AXIS_PAN_VERT      = 1  #  and tilt

# Avoid button bounce by enforcing lag between button events
MIN_BUTTON_LAG_SEC = 0.5

# Avoid close-to-zero values on axis
MIN_AXIS_ABSVAL    = 0.01

# Threshold for faster speed
SPEED_THRESH       = 0.5

# For FFPLAY 
FRAMERATE          = 20
#DELAY_SEC          = 2.5

#import signal
import time
import cv2
import ffmpeg
import numpy as np
#import threading
from pynput.keyboard import Key, Listener
#from pynput import keyboard
from rover import Revolution

def up():
    print("Go up")


def down():
    print("Go down")


def left():
    print("Go left")


def right():
    print("Go right")


def up_left():
    print("Go up_left")


def up_right():
    print("Go up_right")


def down_left():
    print("Go down_left")


def down_right():
    print("Go down_right")


def do_nothing():
    print("Do Nothing")


# Create a mapping of keys to function (use frozenset as sets are not hashable - so they can't be used as keys)

combination_to_function = {
    frozenset([Key.up]): up,  # No `()` after function_1 because
    # we want to pass the function, not the value of the function
    frozenset([Key.down, ]): down,
    frozenset([Key.left, ]): left,
    frozenset([Key.right, ]): right,
    frozenset([Key.up, Key.left]): up_left,
    frozenset([Key.up, Key.right]): up_right,
    frozenset([Key.down, Key.left]): down_left,
    frozenset([Key.down, Key.right]): down_right,
}

# Currently pressed keys
current_keys = set()
wheeldir, steerdir, goslow = 0, 0, 1

def on_press(key):
    # When a key is pressed, add it to the set we are keeping track of and check if this set is in the dictionary
    current_keys.add(key)
    if frozenset(current_keys) in combination_to_function:
        # If the current set of keys are in the mapping, execute the function
        combination_to_function[frozenset(current_keys)]()


def on_release(key):
    # When a key is released, remove it from the set of keys we are keeping track of
    if key in current_keys:
        current_keys.remove(key)

# Supports CTRL-C to override threads
#def _signal_handler(signal, frame):
#    frame.f_locals['rover'].close()
#    sys.exit(0)

# Rover subclass for PS3 + OpenCV
class PS3Rover(Revolution):

    def __init__(self, tmpfile):

        # Set up basics
        Revolution.__init__(self)
        self.wname = 'Rover Revolution'

        # Set up controller using PyGame
        #pygame.display.init()
        #pygame.joystick.init()
        #self.controller = pygame.joystick.Joystick(0)
        #self.controller.init()

         # Defaults on startup: no stealth; driving camera
        self.stealthIsOn = True
        self.usingTurret = True

        # Tracks button-press times for debouncing
        self.lastButtonTime = 0

        # Saves data to video file for display
        self.tmpfile = tmpfile

    # Automagically called by Rover class
    def processVideo(self, h264bytes, timestamp_msec):

        # Update controller events
        #pygame.event.pump()

        # Toggle stealth mode (lights off / infrared camera on)    
        #self.stealthIsOn = self.checkButton(self.stealthIsOn, BUTTON_STEALTH, self.turnStealthOn, self.turnStealthOff)
        #self.turnStealthOff()
        # Toggle stealth mode (lights off / infrared camera on)    
        #self.usingTurret = self.checkButton(self.usingTurret, BUTTON_TURRET, self.useTurretCamera, self.useDrivingCamera)
        #self.useTurretCamera()
        # Use right joystick to drive
        #axis2 = self.get_axis(2)
        #axis3 = self.get_axis(3)
        #goslow = False if abs(axis3) > SPEED_THRESH or abs(axis2) > SPEED_THRESH else True
        #wheeldir = -self.axis_to_dir(axis3)
        #steerdir = self.axis_to_dir(axis2)
        #self.drive(wheeldir, steerdir, goslow)

        # Use left joystick to control turret camera
        #axis0 = self.axis_to_dir(self.get_axis(AXIS_PAN_HORZ))
        #self.moveCameraHorizontal(-axis0)
        #axis1 = self.axis_to_dir(self.get_axis(AXIS_PAN_VERT))
        #self.moveCameraVertical(-axis1)

        # Send video through pipe
        self.tmpfile.stdin.write(h264bytes)
    # Converts axis value to direction
    def axis_to_dir(self, axis):

        d = 0

        if axis > 0:
            d = 1
        elif axis < 0:
            d = -1

        return d

    # Returns axis value when outside noise threshold, else 0
    def get_axis(self, index):
        
        value = 0 #self.controller.get_axis(index)
        
        if value > MIN_AXIS_ABSVAL:
            return value
        elif value < -MIN_AXIS_ABSVAL:
            return value
        else:
            return 0


    # Handles button bounce by waiting a specified time between button presses   
    def checkButton(self, flag, buttonID, onRoutine=None, offRoutine=None):
        if (buttonID):
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

    width, height = 640, 480
    process = (
        ffmpeg
            .input('pipe:')
            .video
            .output('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(width, height))
            .run_async(pipe_stdin=True, pipe_stdout=True)
    )
    # Create a named temporary file for video stream
    #tmpfile = io.BytesIO() #tempfile.NamedTemporaryFile()

    # Create a PS3 Rover object
    rover = PS3Rover(process)

    # Set up signal handler for CTRL-C
    #signal.signal(signal.SIGINT, _signal_handler)

    # Wait a few seconds, then being playing the tmp video file
    #time.sleep(DELAY_SEC)

    while True:
        #listener = Listener(on_press=on_press, on_release=on_release)
        #listener.start()

        in_bytes = process.stdout.read(height * width * 3)

        if not in_bytes:
            continue

        # transform the byte read into a numpy array
        in_frame = (
            np
            .frombuffer(in_bytes, np.uint8)
            .reshape([height, width, 3])
        )

        # Display the frame
        cv2.imshow('in_frame', in_frame)
        key = cv2.waitKey(33) & 0xFF
        if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
            wheeldir, steerdir, goslow = 0, 0, 1
        if key == ord('q'):
            break
        elif key == ord('z'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                rover.stealthIsOn = not rover.stealthIsOn;
                if(rover.stealthIsOn):
                    print('Stealth mode On')
                    rover.turnStealthOn()
                else:
                    print('Stealth mode Off')
                    rover.turnStealthOff()
        elif key == ord('x'):
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
                wheeldir = 1
        elif key == ord('s'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                wheeldir = -1
        elif key == ord('a'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                steerdir = -1
                wheeldir = 1
        elif key == ord('d'):
            if (time.time() - rover.lastButtonTime) > MIN_BUTTON_LAG_SEC:
                rover.lastButtonTime = time.time()
                steerdir = 1
                wheeldir = 1
        elif key == ord('l'):
            rover.moveCameraHorizontal(-1)
        elif key == ord('j'):
            rover.moveCameraHorizontal(1)
        elif key == ord('k'):
            rover.moveCameraVertical(-1)
        elif key == ord('i'):
            rover.moveCameraVertical(1)

        # Shut down Rover
        rover.drive(wheeldir, steerdir, goslow)
        #listener.stop()
    rover.close()
