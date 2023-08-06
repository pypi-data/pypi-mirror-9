#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Nov 11 10:50:27 CET 2013

"""
This script computes scores for samples based on the log-likelihood obtained using a client specifiv GMM based generative model.
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

  parser.add_argument('--mf', '--mapmodelfile', dest='mapmodelfile', type=str, default='./mapmodels.hdf5', help='File containing the real access models of all the clients')  
  
  parser.add_argument('-o', '--outdir', dest='outdir', type=str, default='./tmp', help='Output directory')

  parser.add_argument('--gr', '--group', type=str, dest='group', default='train', help='The group of data to compute the likelihood for (defaults to "%(default)s")', choices = ('train', 'devel', 'test'))

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')
  
  os.umask(002)
  #######
  # Database especific configuration
  #######
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()
  
  sys.stdout.write("Calculating client specific likelihoods for %s data...\n" % args.group)   
    
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
  fmapmodels = bob.io.base.HDF5File(args.mapmodelfile, 'r')

  norm_assoc_map = {}
  pca_machine_assoc_map = {}
  
  sys.stdout.write("Reading the normalization and PCA model parameters (if they exist)...\n")   
  data_read = True
  for featname in args.featname:
    if not fmapmodels.has_group(featname):
      data_read = False
      break  
    fmapmodels.cd(featname)
    if fmapmodels.has_group('norm'):
      fmapmodels.cd('norm')
      norm_assoc_map[featname] = fmapmodels.get_attribute('norm')
      fmapmodels.cd('..')
    if fmapmodels.has_group('pca_machine'):
      fmapmodels.cd('pca_machine')
      pca_machine_assoc_map[featname] = bob.learn.linear.Machine(fmapmodels)
      fmapmodels.cd('..')
    fmapmodels.cd('/')
  
  if data_read == True:
    ensure_dir(args.outdir)
  
    # Querying for the files to be evaluated
    if args.group == 'train':
      process_real, process_attack = database.get_train_data() # contains a list of real and attack videos
    elif args.group == 'devel':
      process_real, process_attack = database.get_devel_data() # contains a list of real and attack videos   
    else:
      process_real, process_attack = database.get_test_data() # contains a list of real and attack videos
    process = process_real + process_attack
  
    # Start the evaluation
    for client in database.get_clients(args.group):
      scores_assoc = {}
      sys.stdout.write("Processing data for client %d...\n" % client)   
      client_obj = [c for c in process if c.get_client_id() == client]  

      for featname, featdir in dir_assoc.items():
        data_info, data = sm.create_full_dataset(featdir, client_obj)
         
        # compute the likelihood
        normparams = None; pca_machine = None
        if norm_assoc_map.has_key(featname):
          normparams = norm_assoc_map[featname]
        
        if pca_machine_assoc_map.has_key(featname):
          pca_machine = pca_machine_assoc_map[featname]
        
        fmapmodels.cd(featname)
        fmapmodels.cd('client_models')  
        fmapmodels.cd("gmm_client_%d" % client) # get the model for this client 
        gmm_machine = bob.learn.em.GMMMachine(fmapmodels)
        scores = gmmo.compute_likelihood(data, gmm_machine, normparams, pca_machine)
        scores_assoc[featname] = sm.reverse_nans(data_info, client_obj, scores)
        fmapmodels.cd('/')
           
      final_scores = numpy.zeros((scores_assoc[args.featname[0]].size, ), dtype='float')
      
      for featname in args.featname:
        final_scores += scores_assoc[featname]
    
      sys.stdout.write("Saving scores for client %d...\n" % client) 
      sm.save_scores(final_scores, data_info, client_obj, args.outdir)
    
    sys.stdout.write("Done!\n")  
    
  else:
    sys.stdout.write("Model data are not available! No error is raised, but also no output is generated!\n")           
  
if __name__ == "__main__":
  main()




