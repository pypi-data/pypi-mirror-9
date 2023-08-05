
CDL Convert
===========

- **Author/Maintainer:** Sean Wallitsch
- **Email:** shidarin@alphamatte.com
- **License:** MIT
- **Status:** Development
- **GitHub:** https://github.com/shidarin/CGITestConvert
- **Python Versions:** 2.6-2.7

Introduction
------------

Converts CGITest Eclipse camera tracking files to Nuke .chan camera files.

The `Eclipse`_ camera system is a vehicle (usually helicopter) mounted
camera system that offers stability and camera tracking to film & tv
photography.

CGITest is the provided application to write out the tracking data when the
Eclipse system is running.

Usage
-----

To convert a CGITest generated Eclipse camera tracking file in ASCII `.txt`
format to a Nuke `.chan` file, all you need to do is supply a file to convert,
and optionally the destination directory to place the converted file.::

    $ cgitest_convert CameraOn-1-cgiLog-141105-121524.txt -d ./chan_files/

If you wish to offset the frame of the resulting frame range, you can
provide a `-f` argument:::

    $ cgitest_convert CameraOn-1-cgiLog-141105-121524.txt -f 1001

The default is 1

Installation
------------

Installing is as simple as using pip:::

    $ pip install CGITestConvert


License
-------

    The MIT License (MIT)

    | CGITestConvert
    | Copyright (c) 2015 Sean Wallitsch
    | http://github.com/shidarin/CGITestConvert/

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

.. _Eclipse: http://www.pictorvision.com/aerial-products/eclipse/

