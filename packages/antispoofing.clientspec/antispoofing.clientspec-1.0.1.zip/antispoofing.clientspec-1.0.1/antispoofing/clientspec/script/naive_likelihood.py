#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Wed Sep 25 14:14:08 CEST 2013
"""
This script computes scores for samples based on the log-likelihood obtained using a GMM based generative model.
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

def main():

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('inputdirs', type=str, help='Directory containing the feature vectors. Several directories corresponding to different *independent* features can be given', nargs='*')

  parser.add_argument('-f', '--featname', type=str, help='Unique names of the *independent* features. The order of stating those should be the same as for the inputdirs parameters', nargs='*')

  parser.add_argument('-m', '--modeldir', dest='modeldir', type=str, default='./tmp', help='Directory containing the models')  
  
  parser.add_argument('-o', '--outdir', dest='outdir', type=str, default='./tmp', help='Directory to output the calculated scores')

  parser.add_argument('-g', '--gaussians', type=int, dest='gaussians', default=(1,), help='The number of Gaussians used to build the model given as input.  Several different numbers corresponding to different numbers of Gaussians for different features are possible (defaults to "%(default)s")', nargs='*')

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')
  
  os.umask(002)
  
  #######
  # Database especific configuration
  #######
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()
    
  #######################
  # Loading the database objects
  #######################
  database = args.cls(args)

  # associate features with directories
  if args.featname:
    dir_assoc = {args.featname[i]:args.inputdirs[i] for i in range(len(args.featname))}
    if len(args.gaussians) == 1:
      gauss_assoc = {args.featname[i]:args.gaussians[0] for i in range(len(args.featname))}
    else:
      gauss_assoc = {args.featname[i]:args.gaussians[i] for i in range(len(args.featname))}
  else:
    dir_assoc = {i:args.inputdirs[i] for i in range(len(args.inputdirs))}  
    if len(args.gaussians) == 1:
      gauss_assoc = {i:args.gaussians[0] for i in range(len(args.featname))}
    else:
      gauss_assoc = {i:args.gaussians[i] for i in range(len(args.featname))}
  
  # Read the GMMs and other parameters
  filename='-'.join([str(g) for g in args.gaussians])
  f = bob.io.base.HDF5File(os.path.join(args.modeldir, 'GMM-'+str(filename)+'.hdf5'), 'r') #only the input directory is given

  
  norm_assoc = {}
  pca_machine_assoc = {}
  gmm_machine_assoc = {}
  scores_assoc = {}
  
  sys.stdout.write("Reading parameters of classification...\n")   
  
  data_read = True
  for featname in args.featname:
    if not f.has_group(featname):
      data_read = False
      break  
    f.cd(featname)
    if f.has_group('norm'):
      f.cd('norm')
      norm_assoc[featname] = f.get_attribute('norm')
      f.cd('..')
    if f.has_group('pca_machine'):
      f.cd('pca_machine')
      pca_machine_assoc[featname] = bob.learn.linear.Machine(f)
      f.cd('..')
    f.cd('gmm_machine')      
    gmm_machine_assoc[featname] = bob.learn.em.GMMMachine(f)
    f.cd('/')
  
  filename='-'.join([str(g) for g in args.gaussians])
  outdir = os.path.join(args.outdir, 'GMM-'+str(filename)) # the outdir is not fully given
    
  if data_read == True:
    ensure_dir(outdir)
    
    # Read the data to be classified  
    for subset in ('train', 'devel', 'test'):
      sys.stdout.write("Classifying %s data...\n" % subset)   
      if subset == 'train':
        process_real, process_attack = database.get_train_data() # contains a list of real and attack videos  
      elif subset == 'devel':
        process_real, process_attack = database.get_devel_data() # contains a list of real and attack videos  
      else:
        process_real, process_attack = database.get_test_data() # contains a list of real and attack videos  
    
      for featname, featdir in dir_assoc.items():
        frame_info_real, data_real = sm.create_full_dataset(featdir, process_real); frame_info_attack, data_attack = sm.create_full_dataset(featdir, process_attack)
        
        if norm_assoc.has_key(featname):
          mean = norm_assoc[featname][0]; std = norm_assoc[featname][1]
          data_real = norm.zeromean_unitvar_norm(data_real, mean, std); data_attack = norm.zeromean_unitvar_norm(data_attack, mean, std)
        
        if pca_machine_assoc.has_key(featname):
          pca_machine = pca_machine_assoc[featname]
          data_real = pca.pcareduce(pca_machine, data_real); data_attack = pca.pcareduce(pca_machine, data_attack)      
     
        gmm = gmm_machine_assoc[featname]
        scores_real = numpy.array([gmm.log_likelihood(i) for i in data_real])
        scores_attack = numpy.array([gmm.log_likelihood(i) for i in data_attack])
      
        scores_assoc[featname] = [sm.reverse_nans(frame_info_real, process_real, scores_real), sm.reverse_nans(frame_info_attack, process_attack, scores_attack)]
      
      final_scores_real = numpy.zeros((scores_assoc[args.featname[0]][0].size, ), dtype='float')
      final_scores_attack = numpy.zeros((scores_assoc[args.featname[0]][1].size, ), dtype='float')    
      
      for featname in args.featname:
        final_scores_real += scores_assoc[featname][0]
        final_scores_attack += scores_assoc[featname][1]
    
      sys.stdout.write("Saving %s scores...\n" % subset) 
      sm.save_scores(final_scores_real, frame_info_real, process_real, outdir); sm.save_scores(final_scores_attack, frame_info_attack, process_attack, outdir) 
      
    sys.stdout.write("Done!\n")  
    
  else:
    sys.stdout.write("Model data are not available! No error is raised, but also no output is generated!\n")    
  
if __name__ == "__main__":
  main()




