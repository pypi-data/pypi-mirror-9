#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Fri Sep 20 15:14:48 CEST 2013

"""
This script creates naive GMM based generative models for one or more type of features in a spoofing database.
"""

import os, sys
import argparse
import bob.io.base
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
  
  parser.add_argument('-o', '--outdir', dest='outdir', type=str, default='./tmp', help='Directory to output the trained machines')

  parser.add_argument('-g', '--gaussians', type=int, dest='gaussians', default=(1,), help='The number of Gaussians. Several different numbers corresponding to different numbers of Gaussians for different features are possible (defaults to "%(default)s")', nargs='*')

  parser.add_argument('--mt', '--modeltype', dest='modeltype', type=str, default='real', help='The type of samples that the model will be created for', choices={'real', 'attack'})

  parser.add_argument('-n', '--normalize', action='store_true', dest='normalize', default=False, help='If True, will do zero mean unit variance normalization on the data before training')
  
  parser.add_argument('-r', '--pca_reduction', action='store_true', dest='pca_reduction', default=False, help='If set, PCA dimensionality reduction will be performed to the data before training')
  
  parser.add_argument('-c', '--cov_pca', action='store_true', dest='cov_pca', default=False, help='If set, PCA computation will be done using the covariance instead of SVD method')

  parser.add_argument('-e', '--energy', type=str, dest="energy", default='0.99', help='The energy which needs to be preserved after the dimensionality reduction if PCA is performed before training')
  
  parser.add_argument('-j', '--join', action='store_true', dest='join', default=False, help='If set, the real access and attack features will be concatenated and normalization and PCA will be performed on the concatenated data. Otherwise, normalization and PCA will be performed only on the subset over the data specified in args.modeltype')

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
  
  # associate features with directories and number of gaussians
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
  
  # Read the training data
  feat_assoc = {}
  for featname, featdir in dir_assoc.items():
    sys.stdout.write("Reading data from %s...\n" % featdir)
    process_train_real, process_train_attack = database.get_train_data()
    feat_assoc[featname] = [sm.create_full_dataset(featdir, process_train_real)[1], sm.create_full_dataset(featdir, process_train_attack)[1]]; # the entries of this dict have form: {featname:[feat_real, feat_attack]}
    
  ensure_dir(args.outdir)
  filename='-'.join([str(g) for g in args.gaussians])
  f = bob.io.base.HDF5File(os.path.join(args.outdir, 'GMM-'+str(filename)+'.hdf5'), 'w')
  
  # Creating the model for each feature type
  for featname, featset in feat_assoc.items():
    sys.stdout.write("Creating model for %s features...\n" % featname)
    train_real = featset[0]; train_attack = featset[1] 
    
    if args.normalize: 
      sys.stdout.write("...normalization...\n")
      if args.join:
        origfeats = numpy.concatenate((train_real,train_attack), axis=0)
      elif args.modeltype == 'real':
        origfeats = train_real
      else:
        origfeats = train_attack
      #mean, std = norm.calc_mean_std(train_real, train_attack, nonStdZero = True)
      mean, std = norm.calc_mean_std(origfeats, nonStdZero = True)
      train_real = norm.zeromean_unitvar_norm(train_real, mean, std); train_attack = norm.zeromean_unitvar_norm(train_attack, mean, std)
      norm_params = numpy.array([mean, std], dtype='float64')
    
    if args.pca_reduction:
      sys.stdout.write("...PCA reduction...\n")
      if args.join:
        normfeats = numpy.concatenate((train_real,train_attack), axis=0)
      elif args.modeltype == 'real':
        normfeats = train_real
      else:
        normfeats = train_attack
      #data_pca = numpy.concatenate((train_real,train_attack),axis=0)
      pca_machine = pca.make_pca(normfeats, float(args.energy), False, True) # performing PCA, no norm within PCA, use covariance method        
      train_real = pca.pcareduce(pca_machine, train_real); train_attack = pca.pcareduce(pca_machine, train_attack)      
          
    if args.modeltype == 'real':
      feats = train_real
    else:
      feats = train_attack
    
    sys.stdout.write("...K-means initialization...\n")        
    kmeans = bob.learn.em.KMeansMachine(gauss_assoc[featname], feats.shape[1])
    kmeansTrainer = bob.learn.em.KMeansTrainer()
    kmeansTrainer.initialization_method = "RANDOM_NO_DUPLICATE"
    print kmeansTrainer.initialization_method ###############
    bob.learn.em.train(kmeansTrainer, kmeans, feats, max_iterations=200, convergence_threshold=1e-5, initialize=True)
    
    sys.stdout.write("...GMM training...\n") 
    gmm = bob.learn.em.GMMMachine(gauss_assoc[featname], feats.shape[1])
    gmm.means = kmeans.means
    trainer = bob.learn.em.ML_GMMTrainer(True, True, True) # update means/variances/weights at each iteration
    bob.learn.em.train(trainer, gmm, feats, convergence_threshold=1e-5)

    # saving the parameters
    sys.stdout.write("...saving parameters...\n")   
    f.create_group(featname)
    f.cd(featname)
    if args.normalize: 
      f.create_group('norm')
      f.cd('norm')
      f.set_attribute('norm',norm_params)
      f.cd('..')
    if args.pca_reduction:  
      f.create_group('pca_machine')
      f.cd('pca_machine')
      pca_machine.save(f)
      f.cd('..')
    f.create_group('gmm_machine')
    f.cd('gmm_machine')
    gmm.save(f)
    f.cd('/')
 
  sys.stdout.write("Done!\n")  
  
if __name__ == "__main__":
  main()




