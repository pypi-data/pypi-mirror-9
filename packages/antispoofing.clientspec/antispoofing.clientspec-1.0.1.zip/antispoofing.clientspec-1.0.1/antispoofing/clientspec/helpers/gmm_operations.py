#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Tue Dec  3 17:56:05 CET 2013

import pkg_resources

import os, sys
import bob.learn.em
import numpy

from antispoofing.utils.helpers import *
from antispoofing.utils.ml import *

"""
Utilitary functions to work with GMMs (computing likelihood, comparing GMMs etc.)
"""

def compute_likelihood(data, gmm_machine, normparams, pca_machine):
  """Computes the log likelihood for all the samples in data to the gmm_machine given as a parameters. It first normalizes and does dimensionality reduction on the data using normparams and pca_machine parameters"""
  if not normparams is None:
    mean = normparams[0]; std = normparams[1]
    data = norm.zeromean_unitvar_norm(data, mean, std)
    
  if not pca_machine is None: 
    data = pca.pcareduce(pca_machine, data) 
   
  scores = numpy.array([gmm_machine.log_likelihood(i) for i in data])  
  return scores



def gather_cohort_scores(ll_cohort, cohorts_to_count, sort=False):
  """
  For each sample, it gathers its scores to the different cohort models into a single array. Returns a numpy array where each row corresponds to a a single sample and each column corresponds to the score of that sample to one cohort model.
  
  Keyword parameters:
    ll_cohort - dictionary with keys: cohort model names and values: scores of all the samples to these cohort models
    cohorts_to_count - the number of cohorts to be accounted. The resulting numpy.array will have this number of columns (each column corresponds to a single cohort model)
    sort - if True, will sort the sample scores to the cohort models in decreasing order. The scores in each row of the resulting numpy.array will be sorted in decreasing order.
  """
  samples = len(ll_cohort.values()[0])
  cohorts = len(ll_cohort.keys())
  gather_scores = numpy.ndarray((samples, cohorts), dtype = 'float64')
  
  for i in range(samples):
    all_scores_per_sample = [ll_cohort[key][i] for key in ll_cohort.keys()]
    if numpy.isnan(all_scores_per_sample).any():
      nanarray = numpy.empty((1, cohorts), 'float64'); nanarray.fill(numpy.nan)
      gather_scores[i,:] = nanarray
    elif sort:
      all_scores_per_sample.sort()
      all_scores_per_sample.reverse()
      gather_scores[i,:] = numpy.array(all_scores_per_sample)
    else:
      gather_scores[i,:] = numpy.array(all_scores_per_sample)  
  return numpy.reshape(gather_scores[:, :cohorts_to_count], (samples, cohorts_to_count))
  
  
  
def kl_divergence_gaussian(machine_1, machine_2):  
  dist = 0;
  # since the variance matrices are only diagonal, all the computations are simplified  
  dist += math.log(numpy.prod(machine_2.variance) / numpy.prod(machine_1.variance)) # ratio of determinants of variances
  dist += numpy.sum(1 / machine_2.variance * machine_1.variance) # trace if Sigma2^{-1}*Sigma1
  dist += numpy.sum((machine_1.mean - machine_2.mean) * (1 / machine_2.variance) * (machine_1.mean - machine_2.mean)) 
  return dist / 2
  
  
  
  
def gmm_distance(machine_1, machine_2):
  dist = 0;
  component_distances = numpy.ndarray([machine_1.shape[0], machine_2.shape[0]], 'float64')
  for i in range(0, machine_1.shape[0]):
    for j in range(0, machine_2.shape[0]):
      comp1 = bob.learn.em.Gaussian()
      comp1.shape[0] = machine_1.shape[1] # the dimensionality is shape[0] for bob.learn.em.Gaussian, but shape[1] for bob.learn.em.GMMMachine
      comp1.mean = machine_1.means[i] 
      comp1.variance = machine_1.variances[i]
      comp2 = bob.learn.em.Gaussian()
      comp2.shape[0] = machine_2.shape[1] # the dimensionality is shape[0] for bob.learn.em.Gaussian, but shape[1] for bob.learn.em.GMMMachine
      comp2.mean = machine_2.means[j]
      comp2.variance = machine_2.variances[j]
      component_distances[i, j] = kl_divergence_gaussian(comp1, comp2)
 
  component_distances_sub = numpy.subtract(component_distances, numpy.log(machine_2.weights))
  min_dists = numpy.amin(component_distances_sub, axis=1) # find the indices of the components of the second machine closest with smallest value in each row
  
  for i in range(0, machine_1.dim_c):
    j = numpy.where(component_distances_sub[i,:] == min_dists[i])[0]
    dist += machine_1.weights[i] * (component_distances[i,j] + math.log(machine_1.weights[i] / machine_2.weights[j]))
      
  return dist[0]  
  
