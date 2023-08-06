#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Mon Apr 2 11:19:00 2013 +0200
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland


"""Tests the I-Vector machine
"""

import numpy
import numpy.linalg
import numpy.random

from bob.learn.em import GMMMachine, GMMStats, IVectorMachine


### Test class inspired by an implementation of Chris McCool
### Chris McCool (chris.mccool@nicta.com.au)
class IVectorMachinePy():
  """An IVector extractor"""

  def __init__(self, ubm=None, dim_t=1):
    # Our state
    self.m_ubm = ubm
    self.m_dim_t = dim_t
    # Resize the matrices T and sigma
    self.resize()
    # Precompute
    self.precompute()

  def resize(self):
    if self.m_ubm:
      dim_cd = self.m_ubm.shape[0] * self.m_ubm.shape[1]
      self.m_t = numpy.random.randn(dim_cd, self.m_dim_t)
      self.m_sigma = numpy.random.randn(dim_cd)

  def precompute(self):
    if self.m_ubm and self.m_t is not None and self.m_sigma is not None:
      #dim_c = self.m_ubm.dim_c
      #dim_d = self.m_ubm.dim_d
      dim_c,dim_d = self.m_ubm.shape
      self.m_cache_TtSigmaInv = {}
      self.m_cache_TtSigmaInvT = {}
      for c in range(dim_c):
        start                       = c*dim_d
        end                         = (c+1)*dim_d
        Tc                          = self.m_t[start:end,:]
        self.m_cache_TtSigmaInv[c]  = Tc.transpose() / self.m_sigma[start:end]
        self.m_cache_TtSigmaInvT[c] = numpy.dot(self.m_cache_TtSigmaInv[c], Tc);

  def set_ubm(self, ubm):
    self.m_ubm = ubm
    # Precompute
    self.precompute()

  def get_ubm(self):
    return self.m_ubm

  def set_t(self, t):
    # @warning: no dimensions check
    self.m_t = t
    # Precompute
    self.precompute()

  def get_t(self):
    return self.m_t

  def set_sigma(self, sigma):
    # @warning: no dimensions check
    self.m_sigma = sigma
    # Precompute
    self.precompute()

  def get_sigma(self):
    return self.m_sigma


  def _get_TtSigmaInv_Fnorm(self, N, F):
    # Initialization
    #dim_c = self.m_ubm.dim_c
    #dim_d = self.m_ubm.dim_d
    dim_c,dim_d = self.m_ubm.shape
    mean_supervector = self.m_ubm.mean_supervector
    TtSigmaInv_Fnorm = numpy.zeros(shape=(self.m_dim_t,), dtype=numpy.float64)

    # Loop over each Gaussian component
    dim_c = self.m_ubm.shape[0]
    for c in range(dim_c):
      start             = c*dim_d
      end               = (c+1)*dim_d
      Fnorm             = F[c,:] - N[c] * mean_supervector[start:end]
      TtSigmaInv_Fnorm  = TtSigmaInv_Fnorm + numpy.dot(self.m_cache_TtSigmaInv[c], Fnorm)
    return TtSigmaInv_Fnorm

  def _get_I_TtSigmaInvNT(self, N):
    # Initialization
    #dim_c = self.m_ubm.dim_c
    #dim_d = self.m_ubm.dim_d
    dim_c, dim_d = self.m_ubm.shape

    TtSigmaInvNT = numpy.eye(self.m_dim_t, dtype=numpy.float64)
    for c in range(dim_c):
      TtSigmaInvNT = TtSigmaInvNT + self.m_cache_TtSigmaInvT[c] * N[c]

    return TtSigmaInvNT

  def project(self, gmmstats):
    if self.m_ubm and self.m_t is not None and self.m_sigma is not None:
      N = gmmstats.n
      F = gmmstats.sum_px

      TtSigmaInv_Fnorm = self._get_TtSigmaInv_Fnorm(N, F)
      TtSigmaInvNT = self._get_I_TtSigmaInvNT(N)

      return numpy.linalg.solve(TtSigmaInvNT, TtSigmaInv_Fnorm)


def test_machine():

  # Ubm
  ubm = GMMMachine(2,3)
  ubm.weights = numpy.array([0.4,0.6])
  ubm.means = numpy.array([[1.,7,4],[4,5,3]])
  ubm.variances = numpy.array([[0.5,1.,1.5],[1.,1.5,2.]])

  # Defines GMMStats
  gs = GMMStats(2,3)
  log_likelihood = -3.
  T = 1
  n = numpy.array([0.4, 0.6], numpy.float64)
  sumpx = numpy.array([[1., 2., 3.], [2., 4., 3.]], numpy.float64)
  sumpxx = numpy.array([[10., 20., 30.], [40., 50., 60.]], numpy.float64)
  gs.log_likelihood = log_likelihood
  gs.t = T
  gs.n = n
  gs.sum_px = sumpx
  gs.sum_pxx = sumpxx

  # IVector (Python)
  m = IVectorMachinePy(ubm, 2)
  t = numpy.array([[1.,2],[4,1],[0,3],[5,8],[7,10],[11,1]])
  m.set_t(t)
  sigma = numpy.array([1.,2.,1.,3.,2.,4.])
  m.set_sigma(sigma)

  wij_ref = numpy.array([-0.04213415, 0.21463343]) # Reference from original Chris implementation
  wij = m.project(gs)
  assert numpy.allclose(wij_ref, wij, 1e-5)

  # IVector (C++)
  mc = IVectorMachine(ubm, 2)
  mc.t = t
  mc.sigma = sigma

  wij_ref = numpy.array([-0.04213415, 0.21463343]) # Reference from original Chris implementation
  wij = mc.project(gs)
  assert numpy.allclose(wij_ref, wij, 1e-5)
