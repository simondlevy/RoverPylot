'''
Python methods for converting bytestrings to integers.  

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

import struct
import sys

def dump_bytes(bytes):
    for c in bytes:
        sys.stdout.write('%02x ' % ord(c))
    sys.stdout.write('\n')

def bytes_to_int(bytes, offset):
    return struct.unpack('i', bytes[offset:offset+4])[0]  

def bytes_to_uint(bytes, offset):
    return struct.unpack('I', bytes[offset:offset+4])[0]  
     
def bytes_to_short(bytes, offset):
    return struct.unpack('h', bytes[offset:offset+2])[0]      
