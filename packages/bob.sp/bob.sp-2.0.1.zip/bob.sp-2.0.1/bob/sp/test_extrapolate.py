#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Tue Sep 27 23:26:46 2011 +0200
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

import os, sys
import numpy
import nose.tools

from . import extrapolate_zero, extrapolate_circular, extrapolate_mirror, extrapolate_nearest, extrapolate_constant

#############################################################################
# Tests blitz-based extrapolation implementation with values returned
#############################################################################

########################## Values used for the computation ##################
eps = 1e-3
a5 = numpy.array([1,2,3,4,5], 'float64')
a14_zeros = numpy.array([0,0,0,0,1,2,3,4,5,0,0,0,0,0], 'float64')
a14_twos = numpy.array([2,2,2,2,1,2,3,4,5,2,2,2,2,2], 'float64')
a14_nearest = numpy.array([1,1,1,1,1,2,3,4,5,5,5,5,5,5], 'float64')
a14_circular = numpy.array([2,3,4,5,1,2,3,4,5,1,2,3,4,5], 'float64')
a14_mirror = numpy.array([4,3,2,1,1,2,3,4,5,5,4,3,2,1], 'float64')

a26_zeros = numpy.array([0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,0,0,0,0,0,0,0,0,0,0,0], 'float64')
a26_twos = numpy.array([2,2,2,2,2,2,2,2,2,2,1,2,3,4,5,2,2,2,2,2,2,2,2,2,2,2], 'float64')
a26_nearest = numpy.array([1,1,1,1,1,1,1,1,1,1,1,2,3,4,5,5,5,5,5,5,5,5,5,5,5,5], 'float64')
a26_circular = numpy.array([1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1], 'float64')
a26_mirror = numpy.array([1,2,3,4,5,5,4,3,2,1,1,2,3,4,5,5,4,3,2,1,1,2,3,4,5,5], 'float64')

A22 = numpy.array([1,2,3,4], 'float64').reshape(2,2)
A44_zeros = numpy.array([0,0,0,0,0,1,2,0,0,3,4,0,0,0,0,0], 'float64').reshape(4,4)
A44_twos = numpy.array([2,2,2,2,2,1,2,2,2,3,4,2,2,2,2,2], 'float64').reshape(4,4)
A44_nearest = numpy.array([1,1,2,2,1,1,2,2,3,3,4,4,3,3,4,4], 'float64').reshape(4,4)
A44_circular = numpy.array([4,3,4,3,2,1,2,1,4,3,4,3,2,1,2,1], 'float64').reshape(4,4)
A44_mirror = numpy.array([1,1,2,2,1,1,2,2,3,3,4,4,3,3,4,4], 'float64').reshape(4,4)

A1111_zeros = numpy.array([0,0,0,0,0,0,0,0,0,0,0,
                           0,0,0,0,0,0,0,0,0,0,0,
                           0,0,0,0,0,0,0,0,0,0,0,
                           0,0,0,0,0,0,0,0,0,0,0,
                           0,0,0,0,1,2,0,0,0,0,0,
                           0,0,0,0,3,4,0,0,0,0,0,
                           0,0,0,0,0,0,0,0,0,0,0,
                           0,0,0,0,0,0,0,0,0,0,0,
                           0,0,0,0,0,0,0,0,0,0,0,
                           0,0,0,0,0,0,0,0,0,0,0,
                           0,0,0,0,0,0,0,0,0,0,0], 'float64').reshape(11,11)
A1111_twos = numpy.array([2,2,2,2,2,2,2,2,2,2,2,
                          2,2,2,2,2,2,2,2,2,2,2,
                          2,2,2,2,2,2,2,2,2,2,2,
                          2,2,2,2,2,2,2,2,2,2,2,
                          2,2,2,2,1,2,2,2,2,2,2,
                          2,2,2,2,3,4,2,2,2,2,2,
                          2,2,2,2,2,2,2,2,2,2,2,
                          2,2,2,2,2,2,2,2,2,2,2,
                          2,2,2,2,2,2,2,2,2,2,2,
                          2,2,2,2,2,2,2,2,2,2,2,
                          2,2,2,2,2,2,2,2,2,2,2], 'float64').reshape(11,11)
A1111_nearest = numpy.array([1,1,1,1,1,2,2,2,2,2,2,
                             1,1,1,1,1,2,2,2,2,2,2,
                             1,1,1,1,1,2,2,2,2,2,2,
                             1,1,1,1,1,2,2,2,2,2,2,
                             1,1,1,1,1,2,2,2,2,2,2,
                             3,3,3,3,3,4,4,4,4,4,4,
                             3,3,3,3,3,4,4,4,4,4,4,
                             3,3,3,3,3,4,4,4,4,4,4,
                             3,3,3,3,3,4,4,4,4,4,4,
                             3,3,3,3,3,4,4,4,4,4,4,
                             3,3,3,3,3,4,4,4,4,4,4], 'float64').reshape(11,11)
A1111_circular = numpy.array([1,2,1,2,1,2,1,2,1,2,1,
                              3,4,3,4,3,4,3,4,3,4,3,
                              1,2,1,2,1,2,1,2,1,2,1,
                              3,4,3,4,3,4,3,4,3,4,3,
                              1,2,1,2,1,2,1,2,1,2,1,
                              3,4,3,4,3,4,3,4,3,4,3,
                              1,2,1,2,1,2,1,2,1,2,1,
                              3,4,3,4,3,4,3,4,3,4,3,
                              1,2,1,2,1,2,1,2,1,2,1,
                              3,4,3,4,3,4,3,4,3,4,3,
                              1,2,1,2,1,2,1,2,1,2,1], 'float64').reshape(11,11)
A1111_mirror = numpy.array([1,2,2,1,1,2,2,1,1,2,2,
                            3,4,4,3,3,4,4,3,3,4,4,
                            3,4,4,3,3,4,4,3,3,4,4,
                            1,2,2,1,1,2,2,1,1,2,2,
                            1,2,2,1,1,2,2,1,1,2,2,
                            3,4,4,3,3,4,4,3,3,4,4,
                            3,4,4,3,3,4,4,3,3,4,4,
                            1,2,2,1,1,2,2,1,1,2,2,
                            1,2,2,1,1,2,2,1,1,2,2,
                            3,4,4,3,3,4,4,3,3,4,4,
                            3,4,4,3,3,4,4,3,3,4,4], 'float64').reshape(11,11)

#############################################################################


def compare(v1, v2, width):
  return abs(v1-v2) <= width

def _extrapolate_1D(res, reference):
  # Tests the extrapolation
  nose.tools.eq_(res.shape, reference.shape)
  for i in range(res.shape[0]):
    assert compare(res[i], reference[i], eps)

def _extrapolate_2D(res, reference):
  # Tests the extrapolation
  nose.tools.eq_(res.shape, reference.shape)
  for i in range(res.shape[0]):
    for j in range(res.shape[1]):
      assert compare(res[i,j], reference[i,j], eps)

def test_extrapolation_1D_zeros():
  b = numpy.zeros((14,), numpy.float64)
  extrapolate_zero(a5,b)
  _extrapolate_1D(b,a14_zeros)

  b = numpy.zeros((26,), numpy.float64)
  extrapolate_zero(a5,b)
  _extrapolate_1D(b,a26_zeros)

def test_extrapolation_1D_twos():
  b = numpy.zeros((14,), numpy.float64)
  extrapolate_constant(a5,b,2.)
  _extrapolate_1D(b,a14_twos)

  b = numpy.zeros((26,), numpy.float64)
  extrapolate_constant(a5,b,2.)
  _extrapolate_1D(b,a26_twos)

def test_extrapolation_1D_nearest():
  b = numpy.zeros((14,), numpy.float64)
  extrapolate_nearest(a5,b)
  _extrapolate_1D(b,a14_nearest)

  b = numpy.zeros((26,), numpy.float64)
  extrapolate_nearest(a5,b)
  _extrapolate_1D(b,a26_nearest)

def test_extrapolation_1D_circular():
  b = numpy.zeros((14,), numpy.float64)
  extrapolate_circular(a5,b)
  _extrapolate_1D(b,a14_circular)

  b = numpy.zeros((26,), numpy.float64)
  extrapolate_circular(a5,b)
  _extrapolate_1D(b,a26_circular)

def test_extrapolation_1D_mirror():
  b = numpy.zeros((14,), numpy.float64)
  extrapolate_mirror(a5,b)
  _extrapolate_1D(b,a14_mirror)

  b = numpy.zeros((26,), numpy.float64)
  extrapolate_mirror(a5,b)
  _extrapolate_1D(b,a26_mirror)

def test_extrapolation_2D_zeros():
  B = numpy.zeros((4,4), numpy.float64)
  extrapolate_zero(A22,B)
  _extrapolate_2D(B,A44_zeros)

  B = numpy.zeros((11,11), numpy.float64)
  extrapolate_zero(A22,B)
  _extrapolate_2D(B,A1111_zeros)

def test_extrapolation_2D_twos():
  B = numpy.zeros((4,4), numpy.float64)
  extrapolate_constant(A22,B,2.)
  _extrapolate_2D(B,A44_twos)

  B = numpy.zeros((11,11), numpy.float64)
  extrapolate_constant(A22,B,2.)
  _extrapolate_2D(B,A1111_twos)

def test_extrapolation_2D_nearest():
  B = numpy.zeros((4,4), numpy.float64)
  extrapolate_nearest(A22,B)
  _extrapolate_2D(B,A44_nearest)

  B = numpy.zeros((11,11), numpy.float64)
  extrapolate_nearest(A22,B)
  _extrapolate_2D(B,A1111_nearest)

def test_extrapolation_2D_circular():
  B = numpy.zeros((4,4), numpy.float64)
  extrapolate_circular(A22,B)
  _extrapolate_2D(B,A44_circular)

  B = numpy.zeros((11,11), numpy.float64)
  extrapolate_circular(A22,B)
  _extrapolate_2D(B,A1111_circular)

def test_extrapolation_2D_mirror():
  B = numpy.zeros((4,4), numpy.float64)
  extrapolate_mirror(A22,B)
  _extrapolate_2D(B,A44_mirror)

  B = numpy.zeros((11,11), numpy.float64)
  extrapolate_mirror(A22,B)
  _extrapolate_2D(B,A1111_mirror)
