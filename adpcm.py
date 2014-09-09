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


def decodeADPCMToPCM(bytes, sampleOffset, tableIndex):
    ''' Returns ordinary PCM samples in interval +/- 2^15, decoded from ADPCM samples.
    '''
    samples = []
   
    for i in range(len(bytes) << 1):
        
        b = ord(bytes[i >> 1])
        
        if i & 1:
            p = (0xF & b)
            
        else:
            p = b >> 4
                                              
        q = p & 0x07
        
        sample = q * _stepTable[tableIndex] / 4 + _stepTable[tableIndex] / 8
        
        if p & 0x08:
            sample = -sample
                                        
        samples.append(_constrain(sample+sampleOffset, -32768, 32767))
                                                    
        tableIndex = _constrain(tableIndex + _indexAdjust[q], 0, len(_stepTable)-1)            
        
    return samples
            
                
        
