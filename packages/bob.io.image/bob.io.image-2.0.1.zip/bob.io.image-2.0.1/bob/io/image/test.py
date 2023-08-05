#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
# Wed Aug 14 12:27:57 CEST 2013
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""Runs some image tests
"""

import os
import numpy
from bob.io.base import load, write, test_utils

# These are some global parameters for the test.
PNG_INDEXED_COLOR = test_utils.datafile('img_indexed_color.png', __name__)

def test_png_indexed_color():

  # Read an indexed color PNG image, and compared with hardcoded values
  img = load(PNG_INDEXED_COLOR)
  assert img.shape == (3,22,32)
  assert img[0,0,0] == 255
  assert img[0,17,17] == 117

def transcode(filename):

  tmpname = test_utils.temporary_filename(suffix=os.path.splitext(filename)[1])

  try:
    # complete transcoding test
    image = load(filename)

    # save with the same extension
    write(image, tmpname)

    # reload the image from the file
    image2 = load(tmpname)

    assert numpy.array_equal(image, image2)

  finally:
    if os.path.exists(tmpname): os.unlink(tmpname)

def test_netpbm():

  transcode(test_utils.datafile('test.pgm', __name__)) #indexed, works fine
  transcode(test_utils.datafile('test.pbm', __name__)) #indexed, works fine
  transcode(test_utils.datafile('test.ppm', __name__)) #indexed, works fine
  #transcode(test_utils.datafile('test.jpg', __name__)) #does not work because of re-compression
