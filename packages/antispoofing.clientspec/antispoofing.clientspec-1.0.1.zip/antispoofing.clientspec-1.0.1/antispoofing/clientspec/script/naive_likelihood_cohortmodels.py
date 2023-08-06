#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Nov 11 11:22:58 CET 2013
"""
This script computes scores for samples based on the log-likelihood obtained using a set of cohort GMM based generative models.
"""

import os, sys
import argparse
import bob.io.base
import bob.learn.linear
import bob.learn.em
import numpy

import antispoofing

from antispoofing.utils.db import *
from antispoofing.utils.helpers import *
from antispoofing.utils.ml import *
from ..helpers import score_manipulate as sm
from ..helpers import gmm_operations as gmmo


def main():

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('inputdirs', type=str, help='Directory containing the feature vectors. Several directories corresponding to different *independent* features can be given', nargs='*')

  parser.add_argument('-f', '--featname', type=str, help='Unique names of the *independent* features. The order of stating those should be the same as for the inputdirs parameters', nargs='*')
  
  parser.add_argument('--cf', '--cohortfile', dest='cohortfile', type=str, default='./cohortmodels.hdf5', help='File containing the attack models of the cohort clients')
  
  parser.add_argument('--gr', '--group', type=str, dest='group', default='train', help='The group of data to adapt the models for (defaults to "%(default)s")', choices = ('train', 'devel', 'test'))

  parser.add_argument('-s', '--sort_cohort', type=int, dest='sortcohort', default=0, help='If this value equals to X>0, then only the first largest X scores to the cohort models are taken in consideration. If 0 or larger then the number of cohort models, the scores to all the cohort models are considered (defaults to "%(default)s")')
  
  parser.add_argument('-o', '--outdir', dest='outdir', type=str, default='./tmp', help='Output directory')

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

  os.umask(002)
  #######
  # Database especific configuration
  #######
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()
    
  sys.stdout.write("Calculating cohort likelihoods for %s data...\n" % args.group)
    
  #######################
  # Loading the database objects
  #######################
  database = args.cls(args)
  
  # associate features with directories
  if args.featname:
    dir_assoc = {args.featname[i]:args.inputdirs[i] for i in range(len(args.featname))}
  else:
    dir_assoc = {i:args.inputdirs[i] for i in range(len(args.inputdirs))}  
  
  # Read the GMMs and other parameters
  fcohort = bob.io.base.HDF5File(args.cohortfile, 'r')

  # read cohort models
  norm_assoc = {}
  pca_machine_assoc = {}
  gmm_machine_assoc = {}
  scores_assoc = {}
  
  sys.stdout.write("Reading the cohort models parameters...\n")   
  data_read = True
  for featname in args.featname:
    if not fcohort.has_group(featname):
      data_read = False
      break  
    fcohort.cd(featname)
    if fcohort.has_group('norm'):
      fcohort.cd('norm')
      norm_assoc[featname] = fcohort.get_attribute('norm')
      fcohort.cd('..')
    if fcohort.has_group('pca_machine'):
      fcohort.cd('pca_machine')
      pca_machine_assoc[featname] = bob.learn.linear.Machine(fcohort)
      fcohort.cd('..')
    fcohort.cd('client_models') 
    machines = {}
    available_models = fcohort.sub_groups(relative=True, recursive=False)
    for m in available_models:
      fcohort.cd(m)
      machines[m] = bob.learn.em.GMMMachine(fcohort)
      fcohort.cd('..')
    gmm_machine_assoc[featname] = machines
    fcohort.cd('/')
  
  # Querying for the files to be evaluated
  if args.group == 'train':
    process_real, process_attack = database.get_train_data() # contains a list of real and attack videos
  elif args.group == 'devel':
    process_real, process_attack = database.get_devel_data() # contains a list of real and attack videos   
  else:
    process_real, process_attack = database.get_test_data() # contains a list of real and attack videos
  process = process_real + process_attack
  
  
  if data_read == True:
    # Start the evaluation

    cohorts_to_count = args.sortcohort

    ll_cohort = {}; # dictionary containing the scores with regards to each cohort model
    for featname, featdir in dir_assoc.items():
      sys.stdout.write("Likelihood %s features...\n" % featname)   
      frame_info, data = sm.create_full_dataset(featdir, process)

      # compute likelihood of the cohort models
      normparams = None; pcamachine = None
      if norm_assoc.has_key(featname):
        normparams = norm_assoc[featname]
       
      if pca_machine_assoc.has_key(featname):
        pca_machine = pca_machine_assoc[featname]
    
      for cohort_id, gmm_machine in gmm_machine_assoc[featname].items():
        sys.stdout.write("Likelihood of %s cohort...\n" % cohort_id)   
        scores = gmmo.compute_likelihood(data, gmm_machine, normparams, pca_machine)  
        if ll_cohort.has_key(cohort_id):
          ll_cohort[cohort_id] += sm.reverse_nans(frame_info, process, scores) # add the scores for the different independent features 
        else:
          ll_cohort[cohort_id] = sm.reverse_nans(frame_info, process, scores)  
    
    # sort the scores to the cohort models
    if cohorts_to_count == 0 or cohorts_to_count > len(ll_cohort):
      cohorts_to_count = len(ll_cohort)
      gather_scores = gmmo.gather_cohort_scores(ll_cohort, cohorts_to_count, sort=False)
    else:
      gather_scores = gmmo.gather_cohort_scores(ll_cohort, cohorts_to_count, sort=True)   
    
    # logadd the scores for all the cohort models
    final_scores = None;
    for i in range(gather_scores.shape[1]):
      if final_scores is None:
        final_scores = gather_scores[:,i]
      else:
        final_scores = numpy.logaddexp(final_scores, gather_scores[:,i])
    
    final_scores = final_scores - numpy.log(cohorts_to_count) # compute avg of likelihoods to the cohorts
            
    sm.save_scores(final_scores, frame_info, process, args.outdir)
    sys.stdout.write("Done!\n")  
    
  else:
    sys.stdout.write("Model data are not available! No error is raised, but also no output is generated!\n")           
  
if __name__ == "__main__":
  main()




