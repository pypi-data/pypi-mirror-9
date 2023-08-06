#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Oct 14 14:21:21 CEST 2013

"""
This script computes scores for samples based on the ratio of log-likelihood obtained using a GMM based generative model for real accesses and spoofing attacks. It utilizes already pre-computed log-likelihood scores for the two models (score directories need to be given as parameters)

"""

import os, sys
import argparse
import bob
import numpy

import antispoofing

from antispoofing.utils.db import *
from antispoofing.utils.helpers import *
from antispoofing.utils.ml import *
from ..helpers import score_manipulate as sm


def main():

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('--dr', '--dirreal', dest='dirreal', type=str, default='./tmp/real', help='Directory containing the scores obtained using real access model')  
  
  parser.add_argument('--da', '--dirattack', dest='dirattack', type=str, default='./tmp/attacks', help='Directory containing the scores obtained using attack model')
  
  parser.add_argument('-o', '--outdir', dest='outdir', type=str, default='./tmp', help='Directory to output the calculated scores')

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')
 
  #######
  # Database especific configuration
  #######
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()
 
  sys.stdout.write("Calculate likelihood ratio...\n")   
 
  if not os.path.exists(args.dirreal) or not os.path.exists(args.dirattack):
    sys.stdout.write("Input directories don't exist: nothing to be done!\n")
    sys.exit(0)     
 
  if not os.listdir(args.dirreal) or not os.listdir(args.dirattack):
    sys.stdout.write("Input directories are empty: nothing to be done!\n")
    sys.exit(0)    
 
  #######################
  # Loading the database objects
  #######################
  database = args.cls(args)
  
  # Read the data to be classified
  for subset in ('train', 'devel', 'test'):
    sys.stdout.write("Processing %s data...\n" % subset)   
    if subset == 'train':
      process_real, process_attack = database.get_train_data() # contains a list of real and attack videos  
    elif subset == 'devel':
      process_real, process_attack = database.get_devel_data() # contains a list of real and attack videos  
    else:
      process_real, process_attack = database.get_test_data() # contains a list of real and attack videos  

    for group in (process_real, process_attack):
      for obj in group:
        scores_real = bob.io.base.load(os.path.expanduser(obj.make_path(args.dirreal, '.hdf5')))
        scores_attack = bob.io.base.load(os.path.expanduser(obj.make_path(args.dirattack, '.hdf5')))
        scores = 2 * (scores_real - scores_attack)
        obj.save(scores, args.outdir, '.hdf5') # save the scores
      
  sys.stdout.write("Done!\n")  
  
if __name__ == "__main__":
  main()




