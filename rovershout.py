#!/usr/bin/env python

'''
rovershout.py Shout at the Brookstone Rover 2.0 to make it turn and run.

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

# Noise samples are in +/- 2^15
NOISETHRESH = 10000

TURNSEC     = 1.25
FLEESEC     = 2.0

import rover
import time


# Handler passed to Rover constructor
class AudioRover(rover.Rover):
    
    def __init__(self):
        rover.Rover.__init__(self)
        self.heard = False
            
    def processAudio(self, pcmsamples):
                            
        avg = 0
        
        for sample in pcmsamples:
            avg += abs(sample)
            
        if avg/len(pcmsamples) > NOISETHRESH:
            self.heard = True
           
 
# Create a Rover object that can process audio
rover = AudioRover()


# Loop till a loud noise is heard
while not rover.heard:
    pass
        
# Turn around for a specified duration
rover.setTreads(-1,+1)
time.sleep(TURNSEC)

# Flee for a specified duration
rover.setTreads(1,1)
time.sleep(FLEESEC)
rover.setTreads(0,0)
                
# Shut down Rover
rover.close()




