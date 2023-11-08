'''
A Python class for Adpative Differential Pulse Code Modulation.  

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

import sys

_indexAdjust = [ -1, -1, -1, -1, 2, 4, 6, 8 ]

_stepTable = [
 7,
 8,
 9,
 10,
 11,
 12,
 13,
 14,
 16,
 17,
 19,
 21,
 23,
 25,
 28,
 31,
 34,
 37,
 41,
 45,
 50,
 55,
 60,
 66,
 73,
 80,
 88,
 97,
 107,
 118,
 130,
 143,
 157,
 173,
 190,
 209,
 230,
 253,
 279,
 307,
 337,
 371,
 408,
 449,
 494,
 544,
 598,
 658,
 724,
 796,
 876,
 963,
 1060,
 1166,
 1282,
 1411,
 1552,
 1707,
 1878,
 2066,
 2272,
 2499,
 2749,
 3024,
 3327,
 3660,
 4026,
 4428,
 4871,
 5358,
 5894,
 6484,
 7132,
 7845,
 8630,
 9493,
 10442,
 11487,
 12635,
 13899,
 15289,
 16818,
 18500,
 20350,
 22385,
 24623,
 27086,
 29794,
 32767]
 
def _constrain(val, minval, maxval):
    return min(max(val, minval), maxval)


def decodeADPCMToPCM(raw, pre_sample, index):
    ''' Returns ordinary PCM samples in interval +/- 2^15, decoded from ADPCM samples
    '''
    decoded = []
   
    for i in range(len(raw) << 1):

        if sys.version_info < (3,):
            b = ord(raw[i >> 1])
        else:
            b = raw[i >> 1]

        code = 0xF & b if i & 1 else b >> 4
        
        sb = 1 if code & 0x08 else 0
                                              
        code &= 0x07

        delta = (_stepTable[index] * code) / 4 + _stepTable[index] / 8
        
        if sb:
            delta = -delta
        
        pre_sample += delta;

        pre_sample = _constrain(pre_sample, -32768, 32767)

        decoded.append(pre_sample)
                                                    
        index += _indexAdjust[code];

        index = _constrain(index, 0, 88)
        
    return decoded
             
                
        
