#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Fri Nov  8 15:11:10 CET 2013
"""
This script adapts GMM models of one or more types of features to the clients in a subset (training, devel or test set) using MAP adaptation. The adaptation can be done using the real access, attack or enrollment samples
"""

import os, sys
import argparse
import bob.io.base
import bob.learn.em
import bob.learn.linear
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

  parser.add_argument('-m', '--modelfile', dest='modelfile', type=str, default='./tmp/GMM.hdf5', help='File containing the models')  
  
  parser.add_argument('-o', '--outfile', dest='outfile', type=str, default='./tmp/mapmodels.hdf5', help='File to write the client models')

  parser.add_argument('--gr', '--group', type=str, dest='group', default='train', help='The group of clients to adapt the models for (defaults to "%(default)s")', choices = ('train', 'devel', 'test'))

  parser.add_argument('-c', '--clss', type=str, dest='clss', default='enroll', help='The class of data to adapt the models to (defaults to "%(default)s")', choices = ('real', 'attack', 'enroll'))
  
  parser.add_argument('--rel', type=float, dest='relevance_factor', default=[4.,], help='Relevance factor for the MAP adaptation (defaults to "%(default)s")', nargs='*')

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')
  
  os.umask(002)
  #######
  # Database especific configuration
  #######
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()
  
  sys.stdout.write("MAP adaptation of %s data...\n" % args.group)
  
  #######################
  # Loading the database objects
  #######################
  database = args.cls(args)
  
  # associate features with directories and relevance factors
  if args.featname:
    dir_assoc = {args.featname[i]:args.inputdirs[i] for i in range(len(args.featname))}
    if len(args.relevance_factor) == 1:
      relfactor_assoc = {args.featname[i]:args.relevance_factor[0] for i in range(len(args.featname))}
    else:
      relfactor_assoc = {args.featname[i]:args.relevance_factor[i] for i in range(len(args.featname))}
  else:
    dir_assoc = {i:args.inputdirs[i] for i in range(len(args.inputdirs))}     
    if len(args.relevance_factor) == 1:
      relfactor_assoc = {i:args.relevance_factor[0] for i in range(len(args.featname))}
    else:
      relfactor_assoc = {i:args.relevance_factor[i] for i in range(len(args.featname))}
  
  # Read the GMMs and other parameters
  f = bob.io.base.HDF5File(args.modelfile, 'r')
  
  norm_assoc = {}
  pca_machine_assoc = {}
  gmm_machine_assoc = {}
  scores_assoc = {}
  
  sys.stdout.write("Reading background model parameters...\n")   
  
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
  
  # Query the videos used to do the MAP
  if args.clss == 'enroll':
    process = database.get_enroll_data(args.group) 
  else:
    if args.group == 'train':
      process_real, process_attack = database.get_train_data() # contains a list of real and attack videos  
    elif args.group == 'devel':
      process_real, process_attack = database.get_devel_data() # contains a list of real and attack videos  
    else:
      process_real, process_attack = database.get_test_data() # contains a list of real and attack videos  
    if args.clss == 'real':
      process = process_real
    else:
      process = process_attack    
  
  #import ipdb; ipdb.set_trace()
  ensure_dir(os.path.dirname(args.outfile))
  fout = bob.io.base.HDF5File(args.outfile, 'w')
  
  if data_read == True:
  
    for featname, featdir in dir_assoc.items():
      sys.stdout.write("MAP for models for %s features...\n" % featname)     
      # firstly, immidiately save the normalization parameters into the file with the client models  
      fout.create_group(featname)
      fout.cd(featname)
      if norm_assoc.has_key(featname):
        fout.create_group('norm')
        fout.cd('norm')
        fout.set_attribute('norm',norm_assoc[featname])
        fout.cd('..')
      if pca_machine_assoc.has_key(featname):  
        fout.create_group('pca_machine')
        fout.cd('pca_machine')
        pca_machine_assoc[featname].save(fout)
        fout.cd('..')
      fout.create_group('client_models')  
      fout.cd('client_models')
 
      #import ipdb; ipdb.set_trace()
      sys.stdout.write("Reading the data for the clients...\n") 
      for client in database.get_clients(args.group):
        sys.stdout.write("Processing client %d...\n" % client)   
        client_data = [c for c in process if c.get_client_id() == client]  
        client_alldata_info, client_alldata = sm.create_full_dataset(featdir, client_data);
    
        if norm_assoc.has_key(featname):
          mean = norm_assoc[featname][0]; std = norm_assoc[featname][1]
          client_alldata = norm.zeromean_unitvar_norm(client_alldata, mean, std);
        
        if pca_machine_assoc.has_key(featname):
          pca_machine = pca_machine_assoc[featname]
          client_alldata = pca.pcareduce(pca_machine, client_alldata);
     
        # MAP adaptation is performed here
        gmm = gmm_machine_assoc[featname]
        relevance_factor = relfactor_assoc[featname] # args.relevance_factor
        trainer = bob.learn.em.MAP_GMMTrainer(gmm, True, False, False, relevance_factor=relevance_factor) #trainer = bob.trainer.MAP_GMMTrainer(relevance_factor, True, False, False)
        #trainer.convergence_threhsold=1e-5
        #trainer.max_iterations = 1
     
        gmmAdapted = bob.learn.em.GMMMachine(gmm.shape[0], gmm.shape[1])

        bob.learn.em.train(trainer, gmmAdapted, client_alldata, convergence_threshold=1e-5, max_iterations=1) #trainer.max_iterations = 1

    
        # saving the model for the client       
        sys.stdout.write("Saving the model parameters for client %d...\n" % client)   
        fout.create_group("gmm_client_%d" % client)
        fout.cd("gmm_client_%d" % client)
        gmmAdapted.save(fout)
        fout.cd('..')     
      fout.cd('/')
    sys.stdout.write("Done!\n")  
    
  else:
    sys.stdout.write("Model data are not available! No error is raised, but also no output is generated!\n")           
  
if __name__ == "__main__":
  main()




