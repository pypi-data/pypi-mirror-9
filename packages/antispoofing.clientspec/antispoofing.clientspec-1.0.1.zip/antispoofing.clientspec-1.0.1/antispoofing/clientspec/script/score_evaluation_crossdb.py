#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu 19 Feb 14:44:52 CET 2015

"""
This script will run the result analysis
"""

import os, sys
import argparse
import bob.measure
import numpy

from antispoofing.utils.ml import *
from antispoofing.utils.helpers import *
from antispoofing.utils.db import *
from ..helpers import *


def main():

  available_dbs = get_db_names()
  db_attack_types = get_db_attack_types(get_db_by_name(available_dbs[0])) + get_db_attack_types(get_db_by_name(available_dbs[1]))

  ##########
  # General configuration
  ##########

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('--sd', '--devel-scores-dir', type=str, dest='develScoresDir', default='', help='Base directory containing the Scores of the database used as devel set (defaults to "%(default)s")')

  parser.add_argument('--st', '--test-scores-dir', type=str, dest='testScoresDir', default='', help='Base directory containing the Scores of the database used as test set (defaults to "%(default)s")')

  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

  parser.add_argument('-a', '--average-scores', action='store_true', dest='average_scores', default=False, help='Use the average of scores')

  parser.add_argument('-i', '--average-size', type=int, dest='average_size', default=100, help='The number of accumulated frames to compute the average')

  parser.add_argument('-d', '--dev-set', type=str, dest='dev_set', default=available_dbs[0], choices=available_dbs, help='The database used in the devel set')

  parser.add_argument('-t', '--test-set', type=str, dest='test_set', default=available_dbs[0], choices=available_dbs, help='The database used in the test set')
  
  parser.add_argument('-o', '--outfile', dest='outfile', type=str, default=None, help='Output file to write the results')
  
  parser.add_argument('--ad', '--attack-devel', type=str, dest='attack_devel', default='', choices=db_attack_types, nargs='+', help='The types of attacks to be used in the development stage')

  parser.add_argument('--at', '--attack-test', type=str, dest='attack_test', default='', choices=db_attack_types, nargs='+', help='The types of attacks to be used in the test stage')
  
  parser.add_argument('-q', '--quality', type=str, dest='quality', default=None, choices=('low', 'high', 'normal'), help='The quality of samples to be considered in development and test stage (for CASIA db only)', nargs='+')
  
  parser.add_argument('--fn', '--fold-number', type=int, dest='fold_number', default=1, help='The number of accumulated frames to compute the average')
  
  parser.add_argument('--si', '--score-inversion', action='store_true', dest='score_inversion', default=False, help='If True, scores will be inverted (multiplied by -1)')
  
  args = parser.parse_args()

  os.umask(002)
    
  ## Parsing
  develScoresDir     = args.develScoresDir
  testScoresDir      = args.testScoresDir
  verbose            = args.verbose
  average_scores     = args.average_scores
  average_size       = args.average_size
    
  #Loading databases
  devDB  = get_db_by_name(args.dev_set)
  testDB = get_db_by_name(args.test_set)

  if not os.path.exists(develScoresDir) or not os.path.exists(testScoresDir):
    parser.error("One of the input directories does not exist")

  if args.attack_devel != '' and 'grandtest' not in args.attack_devel: 
    for ad in args.attack_devel:
      if ad not in get_db_attack_types(devDB):
        parser.error("The specified development attack type is not valid for the specified development database")

  if args.attack_test != '' and 'grandtest' not in args.attack_test:
    for at in args.attack_test:
      if at not in get_db_attack_types(testDB):
        parser.error("The specified test attack type is not valid for the specified test database")  

  #########
  # Loading some dataset
  #########
  if(verbose):
    print("Querying the database ... ")

  if args.attack_devel == '' or 'grandtest' in args.attack_devel:
    if devDB.short_name() == 'casia_fasd' or devDB.short_name() == 'all':
      tuneReal, tuneAttack = devDB.get_devel_data(fold_no=args.fold_number)
    elif devDB.short_name() == 'replay':  
      tuneReal, tuneAttack = devDB.get_devel_data()
  else:
    tuneReal = []; tuneAttack = []
    for at in args.attack_devel:
      if devDB.short_name() == 'casia_fasd':
        r, a = devDB.get_filtered_devel_data('types', fold_no=args.fold_number)[at]
      else:
        r, a = devDB.get_filtered_devel_data('protocol')[at]
      tuneReal += r; tuneAttack += a

      
  if args.attack_test == '' or 'grandtest' in args.attack_test:
    if testDB.short_name() == 'casia_fasd' or testDB.short_name() == 'all':
      develReal, develAttack = testDB.get_devel_data(fold_no=args.fold_number)
      testReal, testAttack   = testDB.get_test_data(fold_no=args.fold_number)
    else:  
      develReal, develAttack = testDB.get_devel_data()
      testReal, testAttack   = testDB.get_test_data()  
    
  else: 
    develReal = []; develAttack = []
    testReal = []; testAttack = [] 
    for at in args.attack_test:
      if testDB.short_name() == 'casia_fasd':
        rd, ad = testDB.get_filtered_devel_data('types', fold_no=args.fold_number)[at]
        rt, at = testDB.get_filtered_test_data('types', fold_no=args.fold_number)[at]
      else:
        rd, ad = testDB.get_filtered_devel_data('protocol')[at]
        rt, at = testDB.get_filtered_test_data('protocol')[at]  
        
      develReal += rd; develAttack += ad
      testReal += rt; testAttack += at

    
  if devDB.short_name() == 'casia_fasd' and args.quality != None:
    tuneReal = [f for f in tuneReal if f.get_quality() in args.quality]
  if testDB.short_name() == 'casia_fasd' and args.quality != None:
    develReal = [f for f in develReal if f.get_quality() in args.quality]
    testReal = [f for f in testReal if f.get_quality() in args.quality]     
    
  if(verbose):
    print("Generating test results ....")

  #Getting the scores

  #Tunning (dev) set D1
  realScores   = ScoreReader(tuneReal,develScoresDir)
  attackScores = ScoreReader(tuneAttack,develScoresDir)
  tune_real_scores = realScores.getScores(average=average_scores, average_size=average_size)
  tune_attack_scores = attackScores.getScores(average=average_scores, average_size=average_size)


  #Devel set D2
  realScores   = ScoreReader(develReal,testScoresDir)
  attackScores = ScoreReader(develAttack,testScoresDir)
  devel_real_scores = realScores.getScores(average=average_scores, average_size=average_size)
  devel_attack_scores = attackScores.getScores(average=average_scores, average_size=average_size)


  #Test set D2
  realScores   = ScoreReader(testReal,testScoresDir)
  attackScores = ScoreReader(testAttack,testScoresDir)
  test_real_scores = realScores.getScores(average=average_scores, average_size=average_size)
  test_attack_scores = attackScores.getScores(average=average_scores, average_size=average_size)

  if args.score_inversion:
    tune_real_scores = tune_real_scores * -1; tune_attack_scores = tune_attack_scores * -1
    devel_real_scores = devel_real_scores * -1; devel_attack_scores = devel_attack_scores * -1
    test_real_scores = test_real_scores * -1; test_attack_scores = test_attack_scores * -1


  #Defining threshold
  thres  = bob.measure.eer_threshold(tune_attack_scores,tune_real_scores)

  #EER on the tune set
  far,frr = bob.measure.farfrr(tune_attack_scores, tune_real_scores, thres)
  EER = 100*((far+frr)/2) #In this case far and frr are the same
  HTER = 100* ((far+frr)/2)

  #HTER on the test set
  dev_far, dev_frr = bob.measure.farfrr(devel_attack_scores, devel_real_scores, thres)
  test_far, test_frr = bob.measure.farfrr(test_attack_scores, test_real_scores, thres)
  HTER_dev = 100* ((dev_far+dev_frr)/2)
  HTER_test = 100* ((test_far+test_frr)/2)

  if args.outfile != None:
    ensure_dir(os.path.dirname(args.outfile))
    f = open(args.outfile, 'a+')
    f.write(args.dev_set + '\t' + args.develScoresDir + '\t' + "%.2f" % (HTER) + '\t' + args.test_set + '\t' + args.testScoresDir + '\t' + "%.2f" % (HTER_test) + '\n')
    f.close()

  print("EER in the " + args.dev_set + " database: %.2f%%" % (EER) )
  print("threshold : %.5f" % (thres) )
  print("")
  print("HTER in dev set in the " + args.test_set + " database: %.2f%%" % (HTER_dev))
  print("HTER in test set in the " + args.test_set + " database: %.2f%%" % (HTER_test))
  print("")
 
  if args.verbose:
    print("Details:\n")
    print("Dev set in the " + args.test_set + " database: FAR: %.2f%% /  FRR: %.2f%%" % (100*dev_far, 100*dev_frr))
    print("Test set in the " + args.test_set + " database: FAR: %.2f%% /  FRR: %.2f%%" % (100*test_far, 100*test_frr))


 
  return 0


if __name__ == "__main__":
  main()
