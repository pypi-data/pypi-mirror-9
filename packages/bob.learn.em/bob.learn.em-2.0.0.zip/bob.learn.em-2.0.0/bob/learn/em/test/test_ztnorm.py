#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Francois Moulin <Francois.Moulin@idiap.ch>
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Tue Jul 19 15:33:20 2011 +0200
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""Tests on the ZTNorm function
"""

import numpy

from bob.io.base.test_utils import datafile
import bob.io.base

#from . import znorm, tnorm, ztnorm
import bob.learn.em

def sameValue(vect_A, vect_B):
  sameMatrix = numpy.zeros((vect_A.shape[0], vect_B.shape[0]), 'bool')

  for j in range(vect_A.shape[0]):
    for i in range(vect_B.shape[0]):
      sameMatrix[j, i] = (vect_A[j] == vect_B[i])

  return sameMatrix

def tnorm(A, C):
  Cmean = numpy.mean(C, axis=0)
  if C.shape[1] > 1:
    Cstd = numpy.sqrt(numpy.sum((C - numpy.tile(Cmean.reshape(1,C.shape[1]), (C.shape[0],1))) ** 2, axis=0) / (C.shape[0]-1))
  else:
    Cstd = numpy.ones(shape=(C.shape[1],), dtype=numpy.float64)
  return (A - numpy.tile(Cmean.reshape(1,C.shape[1]), (A.shape[0],1))) / numpy.tile(Cstd.reshape(1,C.shape[1]), (A.shape[0],1))

def znorm(A, B):
  Bmean = numpy.mean(B, axis=1)
  if B.shape[1] > 1:
    Bstd = numpy.sqrt(numpy.sum((B - numpy.tile(Bmean.reshape(B.shape[0],1), (1,B.shape[1]))) ** 2, axis=1) / (B.shape[1]-1))
  else:
    Bstd = numpy.ones(shape=(B.shape[0],), dtype=numpy.float64)

  return (A - numpy.tile(Bmean.reshape(B.shape[0],1), (1,A.shape[1]))) / numpy.tile(Bstd.reshape(B.shape[0],1), (1,A.shape[1]))


def test_ztnorm_simple():
  # 3x5
  my_A = numpy.array([[1, 2, 3, 4, 5],
                      [6, 7, 8, 9, 8],
                      [7, 6, 5, 4, 3]],'float64')
  # 3x4
  my_B = numpy.array([[5, 4, 7, 8],[9, 8, 7, 4],[5, 6, 3, 2]],'float64')
  # 2x5
  my_C = numpy.array([[5, 4, 3, 2, 1],[2, 1, 2, 3, 4]],'float64')
  # 2x4
  my_D = numpy.array([[8, 6, 4, 2],[0, 2, 4, 6]],'float64')

  # 4x1
  znorm_id = numpy.array([1, 2, 3, 4],'uint32')
  # 2x1
  tnorm_id = numpy.array([1, 5],'uint32')
  
  scores = bob.learn.em.ztnorm(my_A, my_B, my_C, my_D,
      sameValue(tnorm_id, znorm_id))

  ref_scores = numpy.array([[-4.45473107e+00, -3.29289322e+00, -1.50519101e+01, -8.42086557e-01, 6.46544511e-03], [-8.27619927e-01,  7.07106781e-01,  1.13757710e+01,  2.01641412e+00, 7.63765080e-01], [ 2.52913570e+00,  2.70710678e+00,  1.24400233e+01,  7.07106781e-01, 6.46544511e-03]], 'float64')

  assert (abs(scores - ref_scores) < 1e-7).all()

def test_ztnorm_big():
  my_A = bob.io.base.load(datafile("ztnorm_eval_eval.hdf5", __name__, path="../data/"))
  my_B = bob.io.base.load(datafile("ztnorm_znorm_eval.hdf5", __name__, path="../data/"))
  my_C = bob.io.base.load(datafile("ztnorm_eval_tnorm.hdf5", __name__, path="../data/"))
  my_D = bob.io.base.load(datafile("ztnorm_znorm_tnorm.hdf5", __name__, path="../data/"))

  # ZT-Norm
  ref_scores = bob.io.base.load(datafile("ztnorm_result.hdf5", __name__, path="../data/"))
  scores = bob.learn.em.ztnorm(my_A, my_B, my_C, my_D)
  assert (abs(scores - ref_scores) < 1e-7).all()

  # T-Norm
  scores = tnorm(my_A, my_C)
  scores_py = tnorm(my_A, my_C)
  assert (abs(scores - scores_py) < 1e-7).all()

  # Z-Norm
  scores = znorm(my_A, my_B)
  scores_py = znorm(my_A, my_B)
  assert (abs(scores - scores_py) < 1e-7).all()

def test_tnorm_simple():
  # 3x5
  my_A = numpy.array([[1, 2, 3, 4, 5],
                      [6, 7, 8, 9, 8],
                      [7, 6, 5, 4, 3]],'float64')
  # 2x5
  my_C = numpy.array([[5, 4, 3, 2, 1],[2, 1, 2, 3, 4]],'float64')

  zC = tnorm(my_A, my_C)
  zC_py = tnorm(my_A, my_C)
  assert (abs(zC - zC_py) < 1e-7).all()

  empty = numpy.zeros(shape=(0,0), dtype=numpy.float64)
  zC = bob.learn.em.ztnorm(my_A, empty, my_C, empty)
  assert (abs(zC - zC_py) < 1e-7).all()

def test_znorm_simple():
  # 3x5
  my_A = numpy.array([[1, 2, 3, 4, 5],
                      [6, 7, 8, 9, 8],
                      [7, 6, 5, 4, 3]], numpy.float64)
  # 3x4
  my_B = numpy.array([[5, 4, 7, 8],[9, 8, 7, 4],[5, 6, 3, 2]], numpy.float64)

  zA = znorm(my_A, my_B)
  zA_py = znorm(my_A, my_B)
  assert (abs(zA - zA_py) < 1e-7).all()

  empty = numpy.zeros(shape=(0,0), dtype=numpy.float64)
  zA = bob.learn.em.ztnorm(my_A, my_B, empty, empty)
  assert (abs(zA - zA_py) < 1e-7).all()
