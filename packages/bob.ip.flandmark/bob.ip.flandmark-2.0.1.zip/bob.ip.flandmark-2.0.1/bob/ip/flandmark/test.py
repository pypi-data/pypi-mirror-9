#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 16 Apr 09:35:37 2014 CEST

"""Tests for flandmark python bindings
"""

import os
import numpy
import functools
import pkg_resources
import nose.tools
import bob.io.base
import bob.io.image
import bob.ip.color

from . import Flandmark

def F(f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(__name__, os.path.join('data', f))

LENA = F('lena.jpg')
LENA_BBX = [
    [214, 202, 183, 183]
    ] #from OpenCV's cascade detector

MULTI = F('multi.jpg')
MULTI_BBX = [
    [326, 20, 31, 31],
    [163, 25, 34, 34],
    [253, 42, 28, 28],
    ] #from OpenCV's cascade detector

def opencv_detect(image):
  """Detects a face using OpenCV's cascade detector

  Returns a list of arrays containing (x, y, width, height) for each detected
  face.
  """

  from cv2 import CascadeClassifier

  cc = CascadeClassifier(F('haarcascade_frontalface_alt.xml'))
  return cc.detectMultiScale(
      image,
      1.3, #scaleFactor (at each time the image is re-scaled)
      4, #minNeighbors (around candidate to be retained)
      0, #flags (normally, should be set to zero)
      (20,20), #(minSize, maxSize) (of detected objects on that scale)
      )

def pnpoly(point, vertices):
  """Python translation of the C algorithm taken from:
  http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
  """

  (x, y) = point
  j = vertices[-1]
  c = False
  for i in vertices:
    if ( (i[1] > y) != (j[1] > y) ) and \
        ( x < (((j[0]-i[0]) * (y-i[1]) / (j[1]-i[1])) + i[0]) ):
      c = not c
    j = i

  return c

def is_inside(point, box, eps=1e-5):
  """Calculates if a point lies inside a bounding box"""

  (y, x, height, width) = box
  #note: vertices must be organized clockwise
  vertices = numpy.array([
    (x-eps, y-eps),
    (x+width+eps, y-eps),
    (x+width+eps, y+height+eps),
    (x-eps, y+height+eps),
    ], dtype=float)
  return pnpoly((point[1], point[0]), vertices)

def opencv_available(test):
  """Decorator for detecting if OpenCV/Python bindings are available"""
  from nose.plugins.skip import SkipTest

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    try:
      import cv2
      return test(*args, **kwargs)
    except ImportError:
      raise SkipTest("The cv2 module is not available")

  return wrapper

def test_is_inside():

  box = (0, 0, 1, 1)

  # really inside
  assert is_inside((0.5, 0.5), box, eps=1e-10)

  # on the limit of the box
  assert is_inside((0.0, 0.0), box, eps=1e-10)
  assert is_inside((1.0, 1.0), box, eps=1e-10)
  assert is_inside((1.0, 0.0), box, eps=1e-10)
  assert is_inside((0.0, 1.0), box, eps=1e-10)

def test_is_outside():

  box = (0, 0, 1, 1)

  # really outside the box
  assert not is_inside((1.5, 1.0), box, eps=1e-10)
  assert not is_inside((0.5, 1.5), box, eps=1e-10)
  assert not is_inside((1.5, 1.5), box, eps=1e-10)
  assert not is_inside((-0.5, -0.5), box, eps=1e-10)

@opencv_available
def test_lena_opencv():

  img = bob.io.base.load(LENA)
  gray = bob.ip.color.rgb_to_gray(img)
  (x, y, width, height) = opencv_detect(gray)[0]

  flm = Flandmark()
  keypoints = flm.locate(gray, y, x, height, width)
  nose.tools.eq_(keypoints.shape, (8, 2))
  nose.tools.eq_(keypoints.dtype, 'float64')
  for k in keypoints:
    assert is_inside(k, (y, x, height, width), eps=1)

def test_lena():

  img = bob.io.base.load(LENA)
  gray = bob.ip.color.rgb_to_gray(img)
  (x, y, width, height) = LENA_BBX[0]

  flm = Flandmark()
  keypoints = flm.locate(gray, y, x, height, width)
  nose.tools.eq_(keypoints.shape, (8, 2))
  nose.tools.eq_(keypoints.dtype, 'float64')
  for k in keypoints:
    assert is_inside(k, (y, x, height, width), eps=1)

@opencv_available
def test_multi_opencv():

  img = bob.io.base.load(MULTI)
  gray = bob.ip.color.rgb_to_gray(img)
  bbx = opencv_detect(gray)

  flm = Flandmark()
  for (x, y, width, height) in bbx:
    keypoints = flm.locate(gray, y, x, height, width)
    nose.tools.eq_(keypoints.shape, (8, 2))
    nose.tools.eq_(keypoints.dtype, 'float64')
    for k in keypoints:
      assert is_inside(k, (y, x, height, width), eps=1)

def test_multi():

  img = bob.io.base.load(MULTI)
  gray = bob.ip.color.rgb_to_gray(img)

  flm = Flandmark()
  for (x, y, width, height) in MULTI_BBX:
    keypoints = flm.locate(gray, y, x, height, width)
    nose.tools.eq_(keypoints.shape, (8, 2))
    nose.tools.eq_(keypoints.dtype, 'float64')
    for k in keypoints:
      assert is_inside(k, (y, x, height, width), eps=1)
