#!/usr/bin/env python
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Mon Oct  7 14:35:23 CEST 2013

import pkg_resources

import os, sys
import bob.io.base
import numpy
from antispoofing.utils.helpers import *
"""
Utilitary functions to collect features in a matrix for a database and to map scores with the corresponding frame
"""

def read_full_dataset(indir, objects):
  """Creates a full dataset matrix out of all the specified files, without discarding the Nans"""
  dataset = None
  obj_frame_info = {} #dictionary of information about the frames of each object
  for obj in objects:
    filename = os.path.expanduser(obj.make_path(indir, '.hdf5'))
    fvs = bob.io.base.load(filename)
    if fvs.ndim == 1:
      fvs = fvs.reshape(len(fvs), 1)
    if dataset is None:
      dataset = fvs
    else:
      dataset = numpy.append(dataset, fvs, axis = 0)
  return dataset  # return dictionary of frame info; list with removed Nan elements 


def create_full_dataset(indir, objects):
  """Creates a full dataset matrix out of all the specified files"""
  dataset = None
  obj_frame_info = {} #dictionary of information about the frames of each object
  for obj in objects:
    filename = os.path.expanduser(obj.make_path(indir, '.hdf5'))
    fvs = bob.io.base.load(filename)
    if fvs.ndim == 1:
      fvs = fvs.reshape(len(fvs), 1)
    if dataset is None:
      dataset = fvs
    else:
      dataset = numpy.append(dataset, fvs, axis = 0)
    obj_frame_info[obj.make_path()] = [fvs.shape[0], ~numpy.isnan(fvs).any(axis=1)] # the info for each object is of type [total_number of frames, indices_of_nan_frames]
  return obj_frame_info, dataset[~numpy.isnan(dataset).any(axis=1)]  # return dictionary of frame info; list with removed Nan elements 

def map_scores(indir, score_dir, objects, score_list):
  """Maps frame scores to frames of the objects. Writes the scores for each frame in a file, NaN for invalid frames

  Keyword parameters:

  indir: the directory with the feature vectors (needed to read which frames are invalid)

  score_dir: the directory where the score files are going to be written

  objects: list of objects

  score_list: list of scores for the given objects
  """
  num_scores = 0 # counter for how many valid frames have been processed so far in total of all the objects
  for obj in objects:
    filename = os.path.expanduser(obj.make_path(indir, '.hdf5'))
    feat = bob.io.base.load(filename)
    indices = ~numpy.isnan(feat).any(axis=1) #find the indices of invalid frames (they are set to False in the resulting array)
    scores = numpy.ndarray((len(indices), 1), dtype='float64') 
    scores[indices] = score_list[num_scores:num_scores + sum(indices)] # set the scores of the valid frames only
    scores[~indices] = numpy.NaN # set NaN for the scores of the invalid frames
    num_scores += sum(indices) # increase the number of valid scores that have been already maped
    obj.save(scores, score_dir, '.hdf5') # save the scores
    
    
def reverse_nans(frame_info, objects, score_list):
  """Maps frame scores to frames of the FILE objects. Inserts the NaN scores back into the list of scores for each object and returns the list of scores including the Nans

  Keyword parameters:

  frame_info: dictionary with information about the frames for each FILE object

  objects: list of FILE objects

  score_list: list of scores for the given FILE objects
  """
  
  num_scores = 0 # counter for how many valid frames have been processed so far in total of all the objects
  reversed_scores = None # list of reversed scores for all objects
  for obj in objects:
    indices = frame_info[obj.make_path()][1] #find the indices of invalid frames
    #scores = numpy.ndarray((len(indices),1), dtype='float64')
    scores = numpy.ndarray((len(indices),), dtype='float64')
    scores[indices] = score_list[num_scores:num_scores + sum(indices)] # set the scores of the valid frames only
    scores[~indices] = numpy.NaN # set NaN for the scores of the invalid frames
    num_scores += sum(indices) # increase the number of valid scores that have been already maped
    if reversed_scores is None:
      reversed_scores = scores
    else:
      reversed_scores = numpy.append(reversed_scores, scores, axis = 0)
      
  return reversed_scores
  
  
def reverse_nans_obj(frame_info, objects, obj_list, invalid_bob_obj):
  """Maps list of any BOB objects to frames of the FILE objects. Inserts the NaN scores back into the list of BOB objects for each FILE object and returns the list of BOB objects including the Nans

  Keyword parameters:

  frame_info: dictionary with information about the frames for each FILE object

  objects: list of FILE objects

  score_list: list of BOB objects for the given FILE objects
  
  invalid_bob_obj: an object of type BOB object which will denote invalid version of that object and which will be populated in the invalid indices
  """
  
  num_checked_frames = 0 # counter for how many valid frames have been processed so far in total of all the objects
  reversed_obj_list = [] # list of reversed scores for all objects
  for obj in objects:
    indices = frame_info[obj.make_path()][1] #find the indices of invalid frames
    valid_indices = numpy.where(indices)[0]
    curr_obj_list = [invalid_bob_obj] * len(indices)
    
    for i, index in enumerate(valid_indices): 
      curr_obj_list[index] = obj_list[num_checked_frames + i] # set the scores of the valid frames only
    num_checked_frames += sum(indices) # increase the number of valid scores that have been already maped

    reversed_obj_list += curr_obj_list
      
  return reversed_obj_list
  
    
  
def save_scores(score_list, frame_info, objects, score_dir):
  """Maps frame scores to frames of the FILE objects. Writes the scores for each frame in a file, NaN for the invalid frames

  Keyword parameters:

  score_list: list of scores for the given FILE objects
  
  frame_info: dictionary with information about the frames for each FILE object
  
  objects: list of FILE objects
  
  score_dir: the directory where the score files are going to be written
  """
  num_scores = 0 # counter for how frames have been processed so far in total of all the objects
  for obj in objects:
    num_frames = frame_info[obj.make_path()][0] #find the number of frames of the video
    scores = score_list[num_scores:num_scores + num_frames]
    num_scores += num_frames # increase the number of scores that have been already processed
    obj.save(scores, score_dir, '.hdf5') # save the scores
    
def save_obj(obj_list, frame_info, objects, outdir, outgroup=None):
  """Writes the BOB objects corresponding to each frame of the FILE objects in a file. Invalid BOB objects are written for the invalid frames

  Keyword parameters:

  obj_list: list of BOB objects for the given FILE objects
  
  frame_info: dictionary with information about the frames for each FILE object
  
  objects: list of FILE objects
  
  outdir: the directory where the objects are going to be written
  
  outgroup: the subgroup into the hdf5 file where the objects needs to be written (corresponds to the name of feature)
  """
  num_checked_frames = 0 # counter for how frames have been processed so far in total of all the objects
  for i, obj in enumerate(objects):
    sys.stdout.write("Processing file %d / %d...\n" % (i, len(objects))) 
    num_frames = frame_info[obj.make_path()][0] #find the number of frames of the video
    curr_objects = obj_list[num_checked_frames:num_checked_frames + num_frames]
    num_checked_frames += num_frames # increase the number of scores that have been already processed
    outfile = obj.make_path(outdir, '.hdf5')
    ensure_dir(os.path.dirname(outfile))
    f = bob.io.base.HDF5File(outfile, 'a')
    if outgroup != None:
      if not f.has_group(outgroup):
        f.create_group(outgroup)
      f.cd(outgroup)    
    for i, co in enumerate(curr_objects):
      if not f.has_group(str(i)):
        f.create_group(str(i))
      f.cd(str(i))
      co.save(f)
      f.cd('..')
    
  
