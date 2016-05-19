RoverPylot
==========

Pilot the Brookstone Rover 2.0 and Rover Revolution from Python

<h2>Instructions</h2>

This repository contains a Python API and demo
program allowing you to control the Brookstone 
<a href="http://www.amazon.com/Rover-2-0-App-Controlled-Wireless-Tank/dp/B0093285XK">
Rover 2.0 spy tank</a> and <a
href="http://www.amazon.com/Rover-Revolution-App-Controlled-Wireless-Vehicle/dp/B00GLVXM70/ref=sr_1_1?s=toys-and-games&ie=UTF8&qid=1421113202&sr=1-1&keywords=brookstone+rover+revolution">Rover
Revolution</a> spy vehicle from your laptop or PC. To get started, you should
get hold of a 
Rover 2.0 or Revolution (of course) and a Playstation PS3 controller or clone, and install the repository
(<b>sudo python setup.py install</b> for Linux users), as well as
<a href="http://pygame.org/news.html">PyGame</a> and either <a href="http://opencv.org/">OpenCV</a> for Python
(Rover 2.0) or <a href="https://www.ffmpeg.org/">ffmpeg</a> (Rover Revolution). 
Join the Rover's ad-hoc wifi network from your computer.
Then run either the <b>ps3rover20.py</b> or <b>ps3revolution.py</b> script from the repository.  This script will
allow you to drive the Rover around and watch its streaming video, as shown
<a href="http://www.youtube.com/watch?v=AsRleC1ediU">here</a>.  I have
run this script successfully on Linux (Ubuntu),
but I can't vouch for what happens on Windows or OS X, on which Python packages
become much trickier. Remember, the Rover 20 is a tank, so you
control it by moving the left and right sticks back and forth. If you used an inexpensive clone of the
P3 controller you may have to do some adjusting of
the axis and button settings at the top of the script to make it work.



<table>

<tr>

<td><image height=300 align="left" src="rover20.png"></td>

<td><image height=300 alignt="right" src="revolution.png"></td>

</tr>

</table>



Once you're up and running with the <b>ps3rover.py</b> or  <b>ps3revolution.py</b> script, look at its 
source code (and run pydoc on <b>rover.py</b>) to see how RoverPylot works and
how you can modify it to do other interesting things.
<a href="http://isgroupblog.blogspot.com/2013/09/how-i-hacked-brookstone-rover-20.html">
This blog post</a> explains how I hacked the Rover 2.0, and 
<a href="http://mas802.wordpress.com/2014/04/01/brookstone-rover-2-0-skype-client/">
this blog post</a> shows a clever application using Skype.


<h2>Known issues</h2>



<ol>

<li> The  <b>ps3rover20.py</b> script will report a harmless error about extraneous bytes in the JPEG image.
<p>
<li> The  <b>ps3revolution.py</b> script will often show a blurred/smudged image. This happens because, whereas
the Rover 2.0 sends JPEG images, the Revolution sends <a href="http://en.wikipedia.org/wiki/H.264/MPEG-4_AVC">H.264 video</a>.
I couldn't find a Python package for decoding and displaying H.264 on the fly, so I wrote little workaround that 
saves the video to a temporary file, which
from which the script then reads.  You can tweak the performance of this setup by playing with the <tt>FRAMERATE</tt>
and <tt>DELAY_SEC</tt> parameters at the top of the script.
</ol>


<h2>Tips for Windows</h2>

Rob Crawley has put a lot of work into getting RoverPylot to work smoothly on Windows 10.  Here are his changes:
<ol> 

<li> Original:<br>

<tt># Create a named temporary file for video stream<br>
tmpfile = tempfile.NamedTemporaryFile()</tt><br><br>
Changed to:<br>
<tt>tmpfile = tempfile.NamedTemporaryFile(mode='w+b', bufsize=0 , suffix='.avi', prefix='RoverRev', dir='\Python27\RoverRev_WinPylot', delete=False)</tt>
<p><li> Original:<br>
<tt># Wait a few seconds, then being playing the tmp video file<br>
cmd = 'ffplay -window_title Rover_Revolution -framerate %d %s' % (FRAMERATE, tmpfile.name)</tt><br><br>
Changed to:<br>
<tt>
cmd = '/Python27/ffmpeg/bin/ffplay.exe -x 640 -y 480 -window_title Rover_Revolution -framerate %d %s' % (FRAMERATE, tmpfile.name)</tt>

</ol>

Your files paths may be different than those listed below,  so make your changes accordingly

<h2>Copyright and licensing</h2>

Copyright and licensing information can be found in the header of each source file. 
Please <a href="mailto:simon.d.levy@gmail.com">contact</a> me with any questions or 
suggestions.

