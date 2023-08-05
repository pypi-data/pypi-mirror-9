#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Fri Jan 27 11:13:59 CET 2012

"Utility functions for performing PCA dimensionality reduction of data "

import bob.learn.linear
import numpy

def make_pca(data, perc, norm=False, cov=False):
  """ Creates a new LinearMachine for PCA reduction of data, using the training data given as argument. Returns a bob.machine.LinearMachine containing a numpy.ndarray of the most important eigenvectors.

  Keyword parameters:

  data
    numpy.ndarray containing the training data which will be used to calculate the PCA parameters

  perc
    the percentage of energy which should be conserved when reducing the dimensions

  norm
    if set to True, unit-variance normalization will be done to the data prior to reduction (zero mean is done by default anyway)
    
  cov
    if set to True, the covariance method will be used to compute PCA. Otherwise, the SVD method will be used  
"""

  T = bob.learn.linear.PCATrainer()
  if cov == True:
    T.use_svd = False
  params = T.train(data) # params contain a tuple (eigenvecetors, eigenvalues) sorted in descending order

  eigvalues = params[1]
  
  # calculating the cumulative energy of the eigenvalues
  cumEnergy = [sum(eigvalues[0:eigvalues.size-i]) / sum(eigvalues) for i in range(0, eigvalues.size)]
  
  # calculating the number of eigenvalues to keep the required energy
  numeigvalues = len([x for x in cumEnergy if x <= float(perc)])
    
  # recalculating the shape of the LinearMachine
  oldshape = params[0].shape
  params[0].resize(oldshape[0], numeigvalues) # the second parameter gives the number of kept eigenvectors/eigenvalues

  return params[0]


def pcareduce(machine, data):
  """ Reduces the dimension of the data, using the given bob.learn.linear.Machine (projects each of the data feature vector in the lower dimensional space). Returns numpy.ndarray of the feature vectors with reduced dimensionality. The accepted input data can be in numpy.ndarray format format.

  Keyword parameters:

  machine
    bob.learn.linear.Machine
  data
    numpy.ndarray 
  """

  return machine(data)

