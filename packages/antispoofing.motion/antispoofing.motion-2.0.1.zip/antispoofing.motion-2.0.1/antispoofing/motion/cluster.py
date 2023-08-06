#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 26 Jul 2011 12:27:28 CEST 

"""Algorithms for clustering frame-diff data.
"""

import sys
import bob.sp
import numpy

def dcratio(arr):
  """Calculates the DC ratio as defined by the following formula
  
  .. math::

    D(N) = \frac{\sum_{i=1}^N{|FFT_i|}}{|FFT_0|}
  """

  if arr.shape[0] <= 1: return 0.

  res = bob.sp.fft(arr.astype('complex128'))
  res = numpy.absolute(res) #absolute value

  if res[0] == 0:
    s = sum(res[1:])
    if s > 0: return sys.float_info.max
    elif s < 0: return -sys.float_info.max
    else: return 0

  return sum(res[1:])/res[0]

def cluster_5quantities(arr, window_size, overlap):
  """Calculates the clustered values as described at the paper:
  Counter-Measures to Photo Attacks in Face Recognition: a public database and
  a baseline, Anjos & Marcel, IJCB'11.

  This script will output a number of clustered observations containing the 5
  described quantities for windows of a configurable size (N):

    1. The minimum value observed on the cluster
    2. The maximum value observed on the cluster
    3. The mean value observed
    4. The standard deviation on the cluster (unbiased estimator)
    5. The DC ratio (D) as defined by:

  .. math::

    D(N) = \frac{\sum_{i=1}^N{|FFT_i|}}{|FFT_0|}

  .. note::
    
    We always ignore the first entry from the input array as, by definition, it 
    is always zero.
  """

  retval = numpy.ndarray((arr.shape[0], 5), dtype='float64')
  retval[:] = numpy.NaN

  for k in range(0, arr.shape[0]-window_size+1, window_size-overlap):
    obs = arr[k:k+window_size].copy()

    # replace NaN values by set mean so they don't disturb calculations much
    ok = obs[~numpy.isnan(obs)]
    obs[numpy.isnan(obs)] = ok.mean()

    retval[k+window_size-1] = \
        (obs.min(), obs.max(), obs.mean(), obs.std(ddof=1), dcratio(obs))
  return retval
