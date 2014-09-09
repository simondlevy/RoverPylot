'''
cvutils.py OpenCV utilties in Python

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

import cv

def jpegbytes_to_cvimage(jpegbytes):
    '''
    Accepts JPEG image bytes and returns an OpenCV image.  
    '''
    
    # Save image to file on disk
    fname = 'tmp.jpg'
    fd = open(fname, 'w')
    fd.write(jpegbytes)
    fd.close()
    
    # Load file and return image
    return cv.LoadImage(fname)
