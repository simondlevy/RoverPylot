#!/usr/bin/env python

'''
rover20battery.py Check battery on Brookstone Rover 2.0.

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

from rover import Rover20
        
tank = Rover20()

print('Battery at %d%%' % tank.getBatteryPercentage())

tank.close()



