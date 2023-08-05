#!/usr/bin/env python
#coding: utf-8

"""
Author: Jon Wright, ESRF.
"""
# Get ready for python3:
from __future__ import with_statement, print_function

__authors__ = ["Jon Wright", "Jérôme Kieffer"]
__contact__ = "wright@esrf.fr"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__version__ = "29 Oct 2013"

import numpy
import sys
import os
from .fabioimage import fabioimage
from .fabioutils import previous_filename, next_filename

class pixiimage(fabioimage):
    _need_a_seek_to_read = True

    def _readheader(self, infile):
        infile.seek(0)
        self.header = {}
        byt = infile.read(4)
        framesize = numpy.fromstring(byt, numpy.int32)
        if framesize == 243722:
            # life is good
            width = 476
            height = 512
            offset = 24
            self.header['framesize'] = framesize
            self.header['width'] = width
            self.header['height'] = height
            self.header['offset'] = offset
        else:
            print("Pixiimage, bad framesize: %s" % framesize)
            raise

    def read(self, fname, frame=None):
        if frame is None:
            frame = 0
        self.header = {}
        self.resetvals()
        infile = self._open(fname, "rb")
        self.sequencefilename = fname
        self._readheader(infile)
        self.nframes = os.path.getsize(fname) / 487448
        self._readframe(infile, frame)
        infile.close()
        return self

    def _makeframename(self):
        self.filename = "%s$%04d" % (self.sequencefilename,
                                     self.currentframe)

    def _readframe(self, filepointer, img_num):
        if (img_num > self.nframes or img_num < 0):
            raise Exception("Bad image number")
        imgstart = self.header['offset'] + img_num * (512 * 476 * 2 + 24)
        filepointer.seek(imgstart, 0)
        self.data = numpy.fromstring(filepointer.read(512 * 476 * 2),
                                      numpy.uint16)
        self.data.shape = self.header['height'], self.header['width']
        self.dim2, self.dim1 = self.data.shape
        self.currentframe = int(img_num)
        self._makeframename()

    def write(self, fname, force_type=numpy.uint16):
        raise Exception("Write is not implemented")

    def getframe(self, num):
        """
        Returns a frame as a new fabioimage object
        """
        if num < 0 or num > self.nframes:
            raise Exception("Requested frame number is out of range")
        # Do a deep copy of the header to make a new one
        newheader = {}
        for k in self.header.keys():
            newheader[k] = self.header[k]
        frame = pixiimage(header=newheader)
        frame.nframes = self.nframes
        frame.sequencefilename = self.sequencefilename
        infile = frame._open(self.sequencefilename, "rb")
        frame._readframe(infile, num)
        infile.close()
        return frame


    def next(self):
        """
        Get the next image in a series as a fabio image
        """
        if self.currentframe < (self.nframes - 1) and self.nframes > 1:
            return self.getframe(self.currentframe + 1)
        else:
            newobj = pixiimage()
            newobj.read(next_filename(
                self.sequencefilename))
            return newobj

    def previous(self):
        """
        Get the previous image in a series as a fabio image
        """
        if self.currentframe > 0:
            return self.getframe(self.currentframe - 1)
        else:
            newobj = pixiimage()
            newobj.read(previous_filename(
                self.sequencefilename))
            return newobj



def demo(fname):
    i = pixiimage()
    i.read(fname)
    import pylab
    pylab.imshow(numpy.log(i.data))
    print("%s\t%s\t%s\t%s" % (i.filename, i.data.max(), i.data.min(), i.data.mean()))
    pylab.title(i.filename)
    pylab.show()
    while 1:
        i = i.next()
        pylab.imshow(numpy.log(i.data))
        pylab.title(i.filename)
        pylab.show()
        raw_input()

if __name__ == "__main__":
    import sys
    demo(sys.argv[1])

