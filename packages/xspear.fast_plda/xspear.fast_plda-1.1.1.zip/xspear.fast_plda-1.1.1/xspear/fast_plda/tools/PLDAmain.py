import numpy as np
import bob
import os

from spear.tools import IVecTool 

from fastPLDA import *
from . import TwoCovPLDA
from . import TwoStagePLDA

class fastPLDA (IVecTool):
    ########### PLDA training ############
    def train_plda_enroler(self, all_train_files, plda_enroler_file):
        """Trains PLDA model"""
        # load GMM stats from training files
        all_training_features = []
        for train_files in all_train_files:
            training_features = self.load_ivectors_by_client(train_files)
            all_training_features.append(training_features)
        input_dimension = all_training_features[0][0].shape[1]
        
        print("  -> Training PLDA base machine")

        # Check how many filelists were provided. If there are two of them -
        # run two-stage PLDA
        if len(all_train_files) == 2:
            ## TWO-STAGE PLDA
            # create trainer
            t = TwoStagePLDA.TwoStagePLDATrainer((self.m_config.PLDA_TRAINING_ITERATIONS, 
                self.m_config.TWO_STAGE_PLDA_TRAINING_ITERATIONS), self.m_config)
            # train machine
            self.m_pldabase = TwoStagePLDA.TwoStagePLDABase(input_dimension, self.m_config.SUBSPACE_DIMENSION_OF_V, self.m_config.SUBSPACE_DIMENSION_OF_U)
            t.train(self.m_pldabase, all_training_features[0], all_training_features[1])
            # write machines to file
            self.m_pldabase.save(plda_enroler_file)
            # initialize the conveyor for plda scoring
            self.plda_conveyor = TwoStagePLDA.TwoStagePLDAConveyor(self.m_pldabase)
            
        elif len(all_train_files) == 1:
  
            if self.m_config.FAST_PLDA_TYPE == 'two-cov':
                # create trainer
                t = TwoCovPLDA.twoCovTrainer(self.m_config.PLDA_TRAINING_ITERATIONS, 
                                             self.m_config)
                # train machine
                self.m_pldabase = TwoCovPLDA.twoCovBase(input_dimension)
                t.train(self.m_pldabase, all_training_features[0])
                # write machines to file
                self.m_pldabase.save(plda_enroler_file)
                # initialize the conveyor for plda scoring
                self.plda_conveyor = TwoCovPLDA.twoCovConveyor(self.m_pldabase)          
            else:
                # create trainer
                t = fastPLDATrainer(self.m_config.PLDA_TRAINING_ITERATIONS, self.m_config)
                # train machine
                self.m_pldabase = fastPLDABase(input_dimension, self.m_config.SUBSPACE_DIMENSION_OF_V, self.m_config.SUBSPACE_DIMENSION_OF_U)
                t.train(self.m_pldabase, all_training_features[0])
                # write machines to file
                self.m_pldabase.save(plda_enroler_file)
                # initialize the conveyor for plda scoring
                self.plda_conveyor = fastPLDAConveyor(self.m_pldabase)
        else:
            raise RuntimeError('Too many filelists')

   
    def load_plda_enroler(self, plda_enroler_file):
        """Reads the PLDA model from file"""

        f = bob.io.HDF5File(plda_enroler_file)
        if self.m_config.FAST_PLDA_TYPE == 'two-cov':
            dim_d = f.read('dim_d') 
            if f.read('type') == 'TwoCovPLDA':
                self.m_pldabase = TwoCovPLDA.twoCovBase(dim_d) 
                self.m_pldabase.invW = f.read('invW')
            elif f.read('type') == 'TwoStageTwoCovPLDA':
                self.m_pldabase = TwoStageTwoCovPLDA.TwoStageTwoCovBase(dim_d)
                self.m_pldabase.invW1 = f.read('invW1')
                self.m_pldabase.invW2 = f.read('invW2')
                
            self.m_pldabase.invB = f.read('invB')
            self.m_pldabase.mu = f.read('mu')
            
            if f.read('type') == 'TwoCovPLDA':
                self.plda_conveyor = TwoCovPLDA.twoCovConveyor(self.m_pldabase)

        else:
            dim_d = f.read('dim_d')
            dim_V = f.read('dim_V')
            dim_U = f.read('dim_U')
            if f.read('type') == 'fastPLDA':
                self.m_pldabase = fastPLDABase(dim_d, dim_V, dim_U)
            elif f.read('type') == 'TwoStagePLDA':
                self.m_pldabase = TwoStagePLDA.TwoStagePLDABase(dim_d, dim_V, dim_U)
            # Select one-stage or two-stage model
            if f.has_key('V'):
                self.m_pldabase.V = f.read('V')
            if f.has_key('V1'):
                self.m_pldabase.V1 = f.read('V1')
            if f.has_key('V2'):
                self.m_pldabase.V2 = f.read('V2')
            
            if f.has_key('U'):
                self.m_pldabase.U = f.read('U')
            elif f.has_key('U1'):
                self.m_pldabase.U1 = f.read('U1')
            else:
                self.m_pldabase.U1 = np.zeros((dim_d,0))
            if f.has_key('U2'):
                self.m_pldabase.U2 = f.read('U2')
            
            if f.has_key('mu'):
                self.m_pldabase.mu = f.read('mu')
            else:
                self.m_pldabase.mu1 = f.read('mu1')
                self.m_pldabase.mu2 = f.read('mu2')
            
            if f.has_key('Sigma'):
                self.m_pldabase.Sigma = f.read('Sigma')
            if f.has_key('Sigma1'):
                self.m_pldabase.Sigma1 = f.read('Sigma1')
            if f.has_key('Sigma2'):
                self.m_pldabase.Sigma2 = f.read('Sigma2')
                
            self.m_pldabase.dim_d = dim_d
            self.m_pldabase.dim_V = dim_V
            self.m_pldabase.dim_U = dim_U
            
            if f.has_key('V'): # One-stage model
                self.plda_conveyor = fastPLDAConveyor(self.m_pldabase)
            elif f.has_key('V1') and f.has_key('V2'):
                self.plda_conveyor = TwoStagePLDA.TwoStagePLDAConveyor(self.m_pldabase)
                    
