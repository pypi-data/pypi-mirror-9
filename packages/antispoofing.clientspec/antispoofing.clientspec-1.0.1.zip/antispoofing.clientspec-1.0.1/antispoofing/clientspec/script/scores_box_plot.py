#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Wed Apr 16 13:10:03 CEST 2014
"""
This script will plot box plots for each client
"""

import os, sys
import argparse
import bob.measure
import numpy
from matplotlib import rc
rc('text',usetex=1)
import matplotlib.pyplot as mpl
import matplotlib.font_manager as fm

from antispoofing.utils.ml import *
from antispoofing.utils.helpers import *
from antispoofing.utils.db import *
from ..helpers import *


def reject_outliers(data, m=2.5):
    if m == 0:
      red_data = data
    else:
      red_data = data[abs(data - numpy.mean(data)) < m * numpy.std(data)]
    return red_data, len(data) - len(red_data), len(data)


def main():

  available_dbs = get_db_names()
  db_attack_types = get_db_attack_types(get_db_by_name(available_dbs[0])) + get_db_attack_types(get_db_by_name(available_dbs[1]))

  ##########
  # General configuration
  ##########

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('--sd', '--devel-scores-dir', type=str, dest='develScoresDir', default='', help='Base directory containing the Scores of the database used as devel set (defaults to "%(default)s")')

  parser.add_argument('--st', '--test-scores-dir', type=str, dest='testScoresDir', default='', help='Base directory containing the Scores of the database used as test set (defaults to "%(default)s")')

  parser.add_argument('-n','--normalization',action='store_true', dest='normalization',default=False, help='If True, will normalize the scores in the [0, 1] range before plotting the box plots')

  parser.add_argument('-r','--reject-outlier',action='store_true', dest='reject_outlier',default=False, help='If True, reject the outliers in normalization')
  
  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

  parser.add_argument('-a', '--average-scores', action='store_true', dest='average_scores', default=False, help='Use the average of scores')

  parser.add_argument('-i', '--average-size', type=int, dest='average_size', default=100, help='The number of accumulated frames to compute the average')

  parser.add_argument('-d', '--dev-set', type=str, dest='dev_set', default=available_dbs[0], choices=available_dbs, help='The database used in the devel set')

  parser.add_argument('-t', '--test-set', type=str, dest='test_set', default=available_dbs[0], choices=available_dbs, help='The database used in the test set')
  
  parser.add_argument('-o', '--outfile', dest='outfile', type=str, default='plot.pdf', help='Output file to write the results')
  
  parser.add_argument('--ad', '--attack-devel', type=str, dest='attack_devel', default='', choices=db_attack_types, nargs='+', help='The types of attacks to be used in the development stage')

  parser.add_argument('--at', '--attack-test', type=str, dest='attack_test', default='', choices=db_attack_types, nargs='+', help='The types of attacks to be used in the test stage')
  
  parser.add_argument('-q', '--quality', type=str, dest='quality', default=None, choices=('low', 'high', 'normal'), help='The quality of samples to be considered in development and test stage (for CASIA db only)', nargs='+')
  
  parser.add_argument('--fn', '--fold-number', type=int, dest='fold_number', default=1, help='The number of accumulated frames to compute the average')

  parser.add_argument('-b', '--big', action='store_true', dest='big', default=False, help='If True, all the box plots, labels and ticks will be plotter larger/thicker')
  
  parser.add_argument('--si', '--score-inversion', action='store_true', dest='score_inversion', default=False, help='If True, scores will be inverted (multiplied by -1)')
  
  args = parser.parse_args()

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

  #Getting the tunning scores to compute threshold

  #Tunning (dev) set D1
  realScores   = ScoreReader(tuneReal,develScoresDir)
  attackScores = ScoreReader(tuneAttack,develScoresDir)
  tune_real_scores = realScores.getScores(average=average_scores, average_size=average_size)
  tune_attack_scores = attackScores.getScores(average=average_scores, average_size=average_size)

  #Defining threshold
  thres  = bob.measure.eer_threshold(tune_attack_scores,tune_real_scores)

  if args.normalization:
    tune_scores = numpy.concatenate((tune_real_scores, tune_attack_scores), axis=0) 
    if args.reject_outlier:
      tune_scores, num_rejected, total_data = reject_outliers(tune_scores)
      sys.stdout.write("%d / %d scores rejected as outliers...\n" % (num_rejected, total_data))   
    mins = numpy.amin(tune_scores); maxs = numpy.amax(tune_scores)
    #mins, maxs = norm.calc_min_max(numpy.resize(tune_scores, [len(tune_scores), 1]))
    tune_real_scores = (tune_real_scores - mins) / (maxs - mins)
    tune_attack_scores = (tune_attack_scores - mins) / (maxs - mins)
    thres = (thres - mins) / (maxs - mins)
  
  # Now get the test scores for each client
  # Process each client of the test set
  clients_real_meanscores = []; clients_attack_meanscores = []
  clients_real_stdscores = []; clients_attack_stdscores = []

  clients_real_allscores = []; clients_attack_allscores = []

  for client in testDB.get_clients('test'):
    sys.stdout.write("Processing client %d...\n" % client)   
    testclient_data_real = [c for c in testReal if c.get_client_id() == client]  
    testclient_data_attack = [c for c in testAttack if c.get_client_id() == client]  
 
    #Getting the scores
    realScores = ScoreReader(testclient_data_real,testScoresDir)
    attackScores = ScoreReader(testclient_data_attack,testScoresDir)
    testclient_real_scores = realScores.getScores(average=average_scores, average_size=average_size)
    testclient_attack_scores = attackScores.getScores(average=average_scores, average_size=average_size)


    if args.normalization:
      testclient_real_scores = (testclient_real_scores - mins) / (maxs - mins)
      testclient_attack_scores = (testclient_attack_scores - mins) / (maxs - mins)

    clients_real_meanscores.append(numpy.mean(testclient_real_scores)); clients_attack_meanscores.append(numpy.mean(testclient_attack_scores));
    clients_real_stdscores.append(numpy.std(testclient_real_scores)); clients_attack_stdscores.append(numpy.std(testclient_attack_scores));

    if args.score_inversion:
      testclient_real_scores = testclient_real_scores * -1; testclient_attack_scores = testclient_attack_scores * -1

    clients_real_allscores.append(testclient_real_scores); clients_attack_allscores.append(testclient_attack_scores)

  from matplotlib.backends.backend_pdf import PdfPages
  outdir = os.path.dirname(args.outfile)
  if outdir and not os.path.exists(outdir): os.makedirs(outdir)
  pp = PdfPages(args.outfile)  
  
  fig = mpl.figure()

  '''
  #Error bar
  mpl.errorbar(range(1,len(clients_real_meanscores)+1), clients_real_meanscores, yerr=clients_real_stdscores, fmt='o', color='blue', label="real accesses")
  mpl.errorbar(range(1,len(clients_attack_meanscores)+1), clients_attack_meanscores, clients_attack_stdscores, fmt='o', color='red', label='spoofing attacks')
  mpl.axhline(y=thres, linewidth=1, color='green', linestyle='-', label="threshold")
  '''

  ''' Box plot '''
  f, axarr = mpl.subplots(2, sharex=True)
  bp1 = axarr[0].boxplot(clients_real_allscores, 0, '')
  bp2 = axarr[1].boxplot(clients_attack_allscores, 0, '')
  axarr[0].axhline(y=thres, linewidth=5, color='green', linestyle='-', label="threshold")
  axarr[1].axhline(y=thres, linewidth=5, color='green', linestyle='-', label="threshold")
  axarr[0].set_ylim(0, 1) #[-3, 5] [-4, 4]
  axarr[1].set_ylim(0, 1) #[-5, 2] [-8, 2]
  
  mpl.xlabel("Client identity", fontsize=20)
  
  if args.big:
    for tick in axarr[1].xaxis.get_major_ticks():
      tick.label.set_fontsize(14) 
    for tick in axarr[0].yaxis.get_major_ticks():
      tick.label.set_fontsize(14) 
    for tick in axarr[1].yaxis.get_major_ticks():
      tick.label.set_fontsize(14) 
     
  fontProperties = {'family':'sans-serif','sans-serif':['Helvetica'], 'weight' : 'normal'}
  axarr[0].set_yticklabels(axarr[0].get_yticks(), fontProperties)
  axarr[1].set_xticklabels(axarr[1].get_xticks(), fontProperties)
  axarr[1].set_yticklabels(axarr[1].get_yticks(), fontProperties)   
   
  if args.big:
    for boxplot in [bp1, bp2]:     
      for box in boxplot['boxes']: box.set(linewidth=3)
      for whisker in boxplot['whiskers']: whisker.set(linewidth=3)
      for cap in boxplot['caps']: cap.set(linewidth=3)
      for median in boxplot['medians']: median.set(linewidth=3)     
       
       
  #mpl.boxplot(clients_real_allscores, 0)#, usermedians=clients_real_meanscores)
  #mpl.axhline(y=thres, linewidth=1,
      #color='green', linestyle='-', label="threshold") #xmin=0, xmax=0,
  pp.savefig()

  pp.close()
  return 0


if __name__ == "__main__":
  main()
