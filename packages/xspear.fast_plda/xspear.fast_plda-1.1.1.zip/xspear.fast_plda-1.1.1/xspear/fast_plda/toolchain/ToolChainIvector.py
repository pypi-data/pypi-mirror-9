#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Aleksandr Sizov <sizov@cs.uef.fi>
# Tomi Kinnunen <tkinnu@cs.uef.fi>
# Elie Khoury <Elie.Khoury@idiap.ch>
# Thu May 15 14:39:00 CEST 2014
#
# Copyright (C) 2013-2014  University of Eastern Finland, Joensuu, Finland 
# and Idiap Research Institute, Martigny, Switzerland.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os
import numpy
import bob
import pdb

from spear import utils
from spear.toolchain import ToolChainIvector as ToolChain

class ToolChainIvector(ToolChain):
  """This class includes functionalities for an I-Vector tool chain to produce verification scores"""
  
  def train_plda_enroler(self, tool, dir_type=None, force=False):
    """Traines the PLDA model enrolment stage using the projected features"""

    self.m_tool = tool
    if hasattr(tool, 'train_plda_enroler'):
      enroler_file = self.m_file_selector.plda_enroler_file()
      if self.__check_file__(enroler_file, force, 1000):
        print("Enroler '%s' already exists." % enroler_file)
      else:
        train_files = self.m_file_selector.training_feature_list_by_clients_new(dir_type, 'train_plda_enroler')
        # perform PLDA training
        if len(train_files) == 1:
          print("Training PLDA Enroler '%s' as a one-stage model" % (enroler_file))
        else:
          print("Training PLDA Enroler '%s' as a two-stage model" % (enroler_file))
        tool.train_plda_enroler(train_files, str(enroler_file))
  
  def __scores__(self, model, probe_files):
    """Compute simple scores for the given model"""
    scores = numpy.ndarray((1,len(probe_files)), 'float64')

    # Loops over the probes
    i = 0
    for k in probe_files:
      # read probe
      probe = self.__read_probe__(str(k))
      # compute score
      scores[0,i] = self.m_tool.plda_score(model, probe)
      i += 1
    # Returns the scores
    return scores
  
  def __scores_preloaded__(self, model, probes):
    """Compute simple scores for the given model"""
    scores = numpy.ndarray((1,len(probes)), 'float64')
    # Loops over the probes
    i = 0
    for k in probes:
      # take pre-loaded probe
      probe = probes[k]
      # compute score
      scores[0,i] = self.m_tool.plda_score(model, probe)
      i += 1
    # Returns the scores
    return scores
    
  def __scores_a__(self, model_ids, group, dir_type, force, preload_probes, scoring_type='plda'):
    """Computes the scores"""
    # Create score files
    score_file_llr = self.m_file_selector.no_norm_result_file(group)
    
    if hasattr(self.m_tool.plda_conveyor, 'compute_standalone_cm_scores'):
      score_file_cm = str(score_file_llr) + '-cm'
    
    all_probe_objects = []
    all_enrol_features = []
    all_probe_features = []
    
    # probe files:
    probe_files = self.m_file_selector.probe_files(group, dir_type)
    all_probe_objects = self.m_file_selector.probe_objects(group)
    
    # preload the probe files for a faster access (and fewer network load)
    print("Preloading probe files")
    probes = []
    # read all probe files into memory
    for k in probe_files:
      probes.append(self.__read_probe__(str(k)))
        
    for model_id in model_ids:
      enrol_files = self.m_file_selector.enrol_files(model_id, group, dir_type)
      probe_objects = self.m_file_selector.probe_objects_for_model(model_id, group)
      #all_probe_objects.append(probe_objects)
      probe_files = self.m_file_selector.probe_files_for_model(model_id, group, dir_type)

      # Read enrol features
      enrol_features = []
      for k in enrol_files:        # processes one file
        if os.path.exists(str(k)):
          feature = self.m_tool.read_ivector(str(k))
          enrol_features.append(feature)
        else:
          print("Warning: something is wrong with this file: %s" %str(k))
      all_enrol_features.append(enrol_features)
    all_probe_features.append(probes)
    
    self.m_tool.plda_conveyor.enrol_samples(all_enrol_features, all_probe_features)
    
    # Compute the scores
    scores_llr = self.m_tool.plda_conveyor.compute_log_likelihood_ratio()
    
    if hasattr(self.m_tool.plda_conveyor, 'compute_standalone_cm_scores'):
      scores_cm = self.m_tool.plda_conveyor.compute_standalone_cm_scores()
    
    # Save the scores
    self.__save_batch_scores__(score_file_llr, scores_llr, all_probe_objects, 
                               group, model_ids)
                               
    if hasattr(self.m_tool.plda_conveyor, 'compute_standalone_cm_scores'):
      self.__save_cm_scores__(score_file_cm, scores_cm, all_probe_objects)

  def __save_cm_scores__(self, score_file, scores, all_probe_objects):
    """Saves the batch scores for the whole protocol into a text file."""
    print score_file
    
    print len(all_probe_objects)
    print len(numpy.hstack(all_probe_objects))
    
    utils.ensure_dir(os.path.dirname(score_file))
    
    with open(score_file, 'w') as f:
      for j in range(len(all_probe_objects)):
        
        path = str(all_probe_objects[j].path)        
        # Create a suitable name for the evaluation procedure
        if path.find('speech_synthesis') >= 0:
          fname = 'real synth'
        elif path.find('converted') >= 0:
          fname = 'real synth'
        else:
          fname = 'real real'
          
        f.write(fname + " " +  path + " " + str(scores[j]) + "\n")
  
  def __save_batch_scores__(self, score_file, scores, all_probe_objects, group, model_ids):
    """Saves the batch scores for the whole protocol into a text file."""
    print score_file
    
    print len(all_probe_objects)
    print len(numpy.hstack(all_probe_objects))
    
    utils.ensure_dir(os.path.dirname(score_file))
    with open(score_file, 'w') as f:
      k = 0
      for i in range(len(model_ids)):
        model_id = model_ids[i]
        if self.m_tool.m_config.full_matrix_flag:
          for j in range(len(all_probe_objects)):
            probe_object = all_probe_objects[j]
            f.write(str(model_ids[i]) + " " + str(probe_object.client_id) + " " + str(probe_object.path) + " " + str(scores[i][j]) + "\n")
        else:
          probe_objects_for_model = self.m_file_selector.probe_objects_for_model(model_id, group)
          for j in range(len(all_probe_objects)):
            probe_object = all_probe_objects[j]
            if probe_object in probe_objects_for_model:
              f.write(str(model_ids[i]) + " " + str(probe_object.client_id) + " " + str(probe_object.path) + " " + str(scores[i][j]) + "\n")
            else:
              for k in probe_objects_for_model:
                if k.path == probe_object.path:
                  f.write(str(model_ids[i]) + " " + str(k.client_id) + " " + str(k.path) + " " + str(scores[i][j]) + "\n")
      
  def compute_scores(self, tool, norm_type, dir_type, force = False, indices = None, groups = ['dev', 'eval'], types = ['A', 'B', 'C', 'D', 'E'], preload_probes = False):
    print dir_type
    """Computes the scores for 'dev' and 'eval' groups"""
    scoring_type= tool.m_config.scoring_type
    print("Scoring type = %s" %scoring_type)
    if scoring_type == 'plda' and hasattr(tool, 'load_plda_enroler'):
      # read the model enrolment file
      tool.load_plda_enroler(self.m_file_selector.plda_enroler_file())

    # save tool for internal use
    self.m_tool = tool
    self.m_use_projected_ivector_dir = hasattr(tool, 'project_ivector')
    self.m_use_projected_ubm_dir = hasattr(tool, 'project_gmm')
    for group in groups:
      print("----- computing scores for group '%s' -----" % group)
      # get model ids
      model_ids = self.m_file_selector.model_ids(group)
      if norm_type == 'zt_norm' or norm_type == 's_norm':
        tmodel_ids = self.m_file_selector.tmodel_ids(group)
      # compute A scores
      if 'A' in types:
        print("computing A scores")
        self.__scores_a__(model_ids, group, dir_type, force, preload_probes, scoring_type)
        
      if norm_type == 'zt_norm':
        # compute B scores
        if 'B' in types:
          print("computing B scores")
          self.__scores_b__(model_ids, group, dir_type, force, preload_probes, scoring_type)
        # compute C scores
        if 'C' in types:
          print("computing C scores")
          self.__scores_c__(tmodel_ids, group, dir_type, force, preload_probes, scoring_type)
        # compute D scores
        if 'D' in types:
          print("computing D scores")
          self.__scores_d__(tmodel_ids, group, dir_type, force, preload_probes, scoring_type)
      
      if norm_type == 's_norm':
        # compute B scores
        if 'B' in types:
          print("computing B scores")
          self.__scores_b__(model_ids, group, dir_type, force, preload_probes, scoring_type)
        # compute D scores
        if 'D' in types:
          print("computing D scores")
          self.__scores_d__(tmodel_ids, group, dir_type, force, preload_probes, scoring_type) 

  def __scores_b__(self, model_ids, group, dir_type, force, preload_probes, scoring_type='plda'):
    """Computes B scores"""
    
    matrix_B = str(self.m_file_selector.no_norm_result_file(group)) + '-B.hdf5'
    print matrix_B
    if self.__check_file__(matrix_B, force):
      print("Score file '%s' already exists." % (matrix_B))
    else:   
      all_probe_objects = []
      all_enrol_features = []
      all_probe_features = []
      zprobe_objects = self.m_file_selector.zprobe_files(group, dir_type)
      zprobes = []
      # read all probe files into memory
      for k in zprobe_objects:
        zprobes.append(self.m_tool.read_ivector(str(k)))
      for model_id in model_ids:
        enrol_files = self.m_file_selector.enrol_files(model_id, group, dir_type)
        # Read enrol features
        enrol_features = []
        for k in enrol_files:        # processes one file
          if os.path.exists(str(k)):
            feature = self.m_tool.read_ivector(str(k))
            enrol_features.append(feature)
          else:
            print("Warning: something is wrong with this file: %s" %str(k))
        all_enrol_features.append(enrol_features)
      all_probe_features.append(zprobes)
      
      self.m_tool.plda_conveyor.enrol_samples(all_enrol_features, all_probe_features)
      # Compute the scores
      scores_B = self.m_tool.plda_conveyor.compute_log_likelihood_ratio('one-to-all')
      bob.io.save(scores_B, matrix_B)
  
  def __scores_c__(self, tmodel_ids, group, dir_type, force, preload_probes, scoring_type='plda'):
    """Computed C scores"""
    matrix_C = str(self.m_file_selector.no_norm_result_file(group)) + '-C.hdf5'
    print matrix_C
    if self.__check_file__(matrix_C, force):
      print("Score file '%s' already exists." % (matrix_C))
    else:   
      all_probe_objects = []
      all_enrol_features = []
      all_probe_features = []
      # probe files:
      probe_files = self.m_file_selector.probe_files(group, dir_type)
      # preload the probe files for a faster access (and fewer network load)
      
      print("Preloading probe files")
      probes = []
      # read all probe files into memory
      for k in probe_files:
        probes.append(self.__read_probe__(str(k)))
      print("Computing C matrix")
      # Computes the raw scores for the T-Norm model
      for tmodel_id in tmodel_ids:
        tenrol_files = self.m_file_selector.tenrol_files(tmodel_id, group, dir_type)
        tenrol_features = []
        for k in tenrol_files:        # processes one file
          if os.path.exists(str(k)):
            feature = self.m_tool.read_ivector(str(k))
            tenrol_features.append(feature)
          else:
            print("Warning: something is wrong with this file: %s" %str(k))
        all_enrol_features.append(tenrol_features)
      all_probe_features.append(probes)
      
      self.m_tool.plda_conveyor.enrol_samples(all_enrol_features, all_probe_features)
      # Compute the scores
      scores_C = self.m_tool.plda_conveyor.compute_log_likelihood_ratio('one-to-all')
      bob.io.save(scores_C, matrix_C)
      
  def __scores_d__(self, tmodel_ids, group, dir_type, force, preload_probes, scoring_type='plda'):
    # probe files:
        
    matrix_D = str(self.m_file_selector.no_norm_result_file(group)) + '-D.hdf5'
    print matrix_D
    if self.__check_file__(matrix_D, force):
      print("Score file '%s' already exists." % (matrix_D))
    else:   
      all_probe_objects = []
      all_enrol_features = []
      all_probe_features = []
      zprobe_objects = self.m_file_selector.zprobe_files(group, dir_type)
      zprobes = []
      # read all probe files into memory
      for k in zprobe_objects:
        zprobes.append(self.m_tool.read_ivector(str(k)))
      # Computes the raw scores for the T-Norm model
      for tmodel_id in tmodel_ids:
        tenrol_files = self.m_file_selector.tenrol_files(tmodel_id, group, dir_type)
        tenrol_features = []
        for k in tenrol_files:        # processes one file
          if os.path.exists(str(k)):
            feature = self.m_tool.read_ivector(str(k))
            tenrol_features.append(feature)
          else:
            print("Warning: something is wrong with this file: %s" %str(k))
        all_enrol_features.append(tenrol_features)
      all_probe_features.append(zprobes)
      
      self.m_tool.plda_conveyor.enrol_samples(all_enrol_features, all_probe_features)
      # Compute the scores
      scores_D = self.m_tool.plda_conveyor.compute_log_likelihood_ratio('one-to-all')
      bob.io.save(scores_D, matrix_D)

  def zt_norm(self, tool, groups = ['dev', 'eval']):
    """Computes ZT-Norm using the previously generated files. We suppose here that the Tnorm and Znorm sets are independent"""
    for group in groups:
      self.m_use_projected_ivector_dir = hasattr(tool, 'project_ivector')
      self.m_use_projected_ubm_dir = hasattr(tool, 'project_gmm')
      # list of models
      model_ids = self.m_file_selector.model_ids(group)
      tmodel_ids = self.m_file_selector.tmodel_ids(group)
      # first, normalize C and D scores
      #self.__scores_c_normalize__(model_ids, tmodel_ids, group)
      # and normalize it
      #self.__scores_d_normalize__(tmodel_ids, group)
      # load D matrices only once
      matrix_A = str(self.m_file_selector.no_norm_result_file(group)) + '-A.hdf5'
      matrix_B = str(self.m_file_selector.no_norm_result_file(group)) + '-B.hdf5'
      matrix_C = str(self.m_file_selector.no_norm_result_file(group)) + '-C.hdf5'
      matrix_D = str(self.m_file_selector.no_norm_result_file(group)) + '-D.hdf5'
      a = bob.io.load(matrix_A)
      b = bob.io.load(matrix_B)
      c = bob.io.load(matrix_C)
      d = bob.io.load(matrix_D)
      # no need to compute d_same_value since we consider that the 2 sets are idependent
      # d_same_value = bob.io.load(self.m_file_selector.d_same_value_matrix_file(group)).astype(bool)
      # Loops over the model ids
      for k in range(len(model_ids)):
        model_id = model_ids[k]
        # Loads probe objects to get information about the type of access
        probe_objects = self.m_file_selector.probe_objects_for_model(model_id, group)
        # Loads A, B, C, D and D_same_value matrices
        # compute zt scores
        #zt_scores = bob.machine.ztnorm(a, b, c, d, d_same_value)
        a_k = numpy.zeros([1,a.shape[1]])
        a_k[0,:] = a[k,:]
        b_k = numpy.zeros([1,b.shape[1]])
        b_k[0,:] = b[k,:]
        zt_scores[k,:] = bob.machine.ztnorm(a_k, b_k, c, d)
        # Saves to text file
        #self.__save_scores__(self.m_file_selector.zt_norm_file(model_id, group), zt_scores, probe_objects, self.m_file_selector.client_id(model_id))
      all_probe_objects = self.m_file_selector.probe_objects(group)
      self.__save_batch_scores__(self.m_file_selector.zt_norm_result_file(group), zt_scores, all_probe_objects, group, model_ids)
  
  
  def __mean_scores_d__(self, tmodel_ids, group):
    matrix_D = str(self.m_file_selector.no_norm_result_file(group)) + '-D.hdf5'
    D = bob.io.load(matrix_D)
    # initialize D mean and std matrice
    d_for_all = []
    for k in range(len(tmodel_ids)):
      tmp=D[k,:]
      tmp = sorted(tmp, reverse=True)
      tmp = tmp[0:1500]
      d_for_all.append([numpy.mean(tmp), numpy.std(tmp)])
    d_for_all = numpy.vstack(d_for_all)
    # Saves to files
    bob.io.save(d_for_all, str(self.m_file_selector.no_norm_result_file(group)) + '-D-stats.hdf5')


  def __mean_scores_b__(self, model_ids, group):
    matrix_B = str(self.m_file_selector.no_norm_result_file(group)) + '-B.hdf5'
    B = bob.io.load(matrix_B)
    # initialize B mean and std matrice
    b_for_all = []
    for k in range(len(model_ids)):
      tmp=B[k,:]
      tmp = sorted(tmp, reverse=True)
      tmp = tmp[0:1500]
      b_for_all.append([numpy.mean(tmp), numpy.std(tmp)])
    b_for_all = numpy.vstack(b_for_all)
    # Saves to files
    bob.io.save(b_for_all, str(self.m_file_selector.no_norm_result_file(group)) + '-B-stats.hdf5')


  def s_norm(self, tool, groups = ['dev', 'eval']):
    """Computes S-Norm using the previously generated files. We suppose here that the Tnorm and Znorm sets are independent"""
    for group in groups:
      score_file_S = self.m_file_selector.no_norm_result_file(group) + '-Snorm'
      self.m_use_projected_ivector_dir = hasattr(tool, 'project_ivector')
      self.m_use_projected_ubm_dir = hasattr(tool, 'project_gmm')
      # list of models
      model_ids = self.m_file_selector.model_ids(group)
      tmodel_ids = self.m_file_selector.tmodel_ids(group)
      
      self.__mean_scores_d__(tmodel_ids, group)
      self.__mean_scores_b__(model_ids, group)

      # load D matrices only once
      a = bob.io.load(str(self.m_file_selector.no_norm_result_file(group)) + '-A.hdf5')
      b = bob.io.load(str(self.m_file_selector.no_norm_result_file(group)) + '-B-stats.hdf5')
      d = bob.io.load(str(self.m_file_selector.no_norm_result_file(group)) + '-D-stats.hdf5')
      scores_S = numpy.ndarray(shape=(a.shape))

      # no need to compute d_same_value since we consider that the 2 sets are idependent
      # Loops over the model ids
      all_probe_objects = self.m_file_selector.probe_objects(group)
      for m in range(len(model_ids)):
        model_id = model_ids[m]
        # Loads probe objects to get information about the type of access
        probe_objects = self.m_file_selector.probe_objects_for_model(model_id, group)
        # compute s-norm scores
        for k in range(a.shape[1]):
          scores_S[m,k] = (a[m,k] - b[m,0])/b[m,1] + (a[m,k] -d[k,0])/d[k,1]
      # Saves to text file
      self.__save_batch_scores__(score_file_S, scores_S, all_probe_objects, group, model_ids)
        

  def symm_svm(self, tool, groups = ['dev', 'eval']):
    """Computes S-Norm using the previously generated files. We suppose here that the Tnorm and Znorm sets are independent"""
    for group in groups:
      # list of models
      model_ids = self.m_file_selector.model_ids(group)
      tmodel_ids = self.m_file_selector.tmodel_ids(group)
      
      self.__mean_scores_d__(tmodel_ids, group)
      self.__mean_scores_b__(model_ids, group)

      # load D matrices only once
      b = bob.io.load(self.m_file_selector.s_b_matrix_file(group))
      d = bob.io.load(self.m_file_selector.s_d_matrix_file(group))
      
      e_for_all = []
      for tmodel_id in tmodel_ids:
        tmp = bob.io.load(self.m_file_selector.s_e_file(tmodel_id, group))
        e_for_all.append(tmp)
      e_for_all = numpy.vstack(e_for_all)

      print e_for_all.shape
      e = e_for_all
      
      for m in range(len(model_ids)):
        model_id = model_ids[m]
        
        # Loads probe objects to get information about the type of access
        probe_objects = self.m_file_selector.probe_objects_for_model(model_id, group)
        # Loads A, B, C, D and D_same_value matrices
        a = bob.io.load(self.m_file_selector.s_a_file(model_id, group))
        symm_svm_scores = numpy.ndarray(shape=(a.shape))
        # compute s-norm scores
        for k in range(a.shape[1]):
          #print a[0,k], b[m,0], b[m,1], d[k,0], d[k,1]
          a[0,k] = ( a[0,k] + e[k,m] )/ 2.
          symm_svm_scores[0,k] = (a[0,k] - b[m,0])/b[m,1] + (a[0,k] -d[k,0])/d[k,1]
          #s_scores[0,k] = (a[0,k] - b[m,0]) + (a[0,k] -d[k,0])
          
          # beta
          #print a[0,k], b[m,0], b[m,1], d[k,0], d[k,1]
          #s_prime = (a[0,k] - b[m,0])/b[m,1] + (a[0,k] -d[k,0])/d[k,1]
          #s_scores[0,k] = (s_prime - b[m,2])/b[m,3] + (s_prime -d[k,2])/d[k,3]
          #s_scores[0,k] = (s_prime - b[m,2]) + (s_prime -d[k,2])
          
          
        # Saves to text file
        self.__save_scores__(self.m_file_selector.s_norm_file(model_id, group), symm_svm_scores, probe_objects, self.m_file_selector.client_id(model_id)) 
