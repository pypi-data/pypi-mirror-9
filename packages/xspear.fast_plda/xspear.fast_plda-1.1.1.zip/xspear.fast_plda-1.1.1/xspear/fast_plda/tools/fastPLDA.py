#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Aleksandr Sizov <sizov@cs.uef.fi>
# Elie Khoury <Elie.Khoury@idiap.ch>
# Tomi Kinnunen <tkinnu@cs.uef.fi>
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
"""This file implements functionality for the fast PLDA model"""

import numpy as np
import bob
import os

from spear import utils

import pdb
      
class fastPLDABase(object):
    """This calss stores the parameters for the PLDA model in the new format.
    
    Attributes:
        dim_d: Dimensionality of the input feature vectors.
        dim_V: Dimensionality of the V subspace/matrix of the PLDA model.
        dim_U: Dimensionality of the U subspace/matrix of the PLDA model.
        V: The matrix of between speaker variability.
        U: The matrix of within speaker variability.
        Sigma: Covariance noise matrix.
        mu: The mean vector of the PLDA model.
    """
    
    def __init__(self, dim_d, dim_V, dim_U):
      """
      Args:
          dim_d: Dimensionality of the input feature vectors.
          dim_V: Dimensionality of the V subspace/matrix of the PLDA model.
          dim_U: Dimensionality of the U subspace/matrix of the PLDA model.
      """
      self.dim_d = dim_d
      self.dim_V = dim_V
      self.dim_U = dim_U
        
    def save(self, hdf5file):
      """ Save fastPLDABase instance to the hdf5 file. """
      utils.ensure_dir(os.path.dirname(hdf5file))
      f = bob.io.HDF5File(str(hdf5file), 'w')
      f.set('V', self.V)
      if self.dim_U > 0:
        f.set('U', self.U)
      f.set('mu', self.mu)
      f.set('Sigma', self.Sigma)
      f.set('dim_d', self.dim_d)
      f.set('dim_V', self.dim_V)
      f.set('dim_U', self.dim_U)
      f.set('type', 'fastPLDA')
      
    def compute_log_likelihood(self, data, remove_mu=True):
        """Comute the log likelihood for the whole dataset.
        
        Args:
            data: An array of the shape (number_of_features, number_of_samples).
            remove_mu: An indicator whether to substract PLDA mean value from 
                       the data.
        """
        (D, N) = data.shape
        
        if remove_mu: 
            centered_data = data - self.mu
        else:
            centered_data = data
            
        # Total covariance matrix for the model with integrated out latent 
        # variables
        Sigma_tot = (np.dot(self.V, self.V.T) + np.dot(self.U, self.U.T) + 
                     self.Sigma)
        
        # Compute log-determinant of the Sigma_tot matrix
        E, junk = np.linalg.eig(Sigma_tot)
        log_det = np.sum(np.log(E))
        
        return -0.5*(N*D*np.log(2*np.pi) + N*log_det + 
               np.sum(np.sum(np.dot(centered_data.T,np.linalg.inv(Sigma_tot)) *
               centered_data.T, axis=1)))
        
class fastPLDATrainer(object):
    """This class trains a new PLDA model.
    
    If u has rank 0 then train simplified PLDA model, otherwise train
    standard PLDA model
    
    Attributes:
        training_iterations: Maximum number of the training iterations.
        seed: Seed for the random number generator.
        init_V_method: Method to initialize V matrix.
        init_U_method: Method to initialize U matrix.
        init_Sigma_method: Method to initialize Sigma matrix.
        training_threshold: Threshold for ending the EM loop.
        do_md_step: Indicator for the minimum-divergence step.
        compute_log_likelihood: Indication whether to compute a log-likelihood
                                of the training data during EM-algorithm
        Sigma_scale: Parameter that multiplies initial Sigma matrix
        plda_type: it could be either
                    'std' - standard PLDA
                    'simp' - simplified PLDA
    """

    def __init__(self, training_iterations, config=None):
        """
        Args:
            training_iterations: Maximum number of the training iterations.
            config: A class with the following fields: 
                INIT_SEED: Seed for the random number generator.
                INIT_V_METHOD: Method to initialize V matrix.
                INIT_U_METHOD: Method to initialize U matrix.
                INIT_SIGMA_METHOD: Method to initialize Sigma matrix.
                PLDA_TRAINING_THRESHOLD: Threshold for ending the EM loop.
                PLDA_DO_MD_STEP: Indicator for the minimum-divergence step.
                PLDA_COMPUTE_LOG_LIKELIHOOD: Indicator for the LL computation.
                INIT_SIGMA_SCALE: Parameter that multiplies initial Sigma matrix
                FAST_PLDA_TYPE: Type of the PLDA model
        """
        self.training_iterations = training_iterations
        if config is not None:
            self.seed = config.INIT_SEED
            np.random.seed(self.seed) # set the seed for the randomizer
            
            self.init_V_method = config.INIT_V_METHOD
            self.init_U_method = config.INIT_U_METHOD
            self.init_Sigma_method = config.INIT_SIGMA_METHOD
            self.do_md_step = config.PLDA_DO_MD_STEP            
            self.compute_log_likelihood = config.PLDA_COMPUTE_LOG_LIKELIHOOD
            self.Sigma_scale = config.INIT_SIGMA_SCALE
            self.plda_type = config.FAST_PLDA_TYPE
            
    def train(self, pldabase, data):
        """Train the parameters for the PLDA model.
        
        Args:
            pldabase: An instance of fastPLDABase class.
            data: A list of ndarrays. Each person has its own list item of the 
                  shape (number_of_samples, number_of_features)
        """
        data, pooled_data, N,f,S = self._preprocessing(pldabase, data)
            
        # Initialize PLDA parameters
        self.__initialize(pldabase, Sigma=S*(self.Sigma_scale/N)) 

        for i in xrange(self.training_iterations):
            T_y, T_x, R_yy, R_yx, R_xx, Y_md = self._e_step(pldabase, data, N, 
                                                             f, S)
            self.__m_step(pldabase, R_yy, R_yx, R_xx, T_y, T_x, N, S)
            if self.do_md_step:
                self.__md_step(pldabase, R_yy, R_yx, R_xx, Y_md, N) 
            # Print current progress
            self._print_progress(pldabase, pooled_data, i, 
                                    self.training_iterations)
    
    def _preprocessing(self, pldabase, data):
        """Apply preprocessing necessary for the EM-algorithm.
        
        Args:
            pldabase: An instance of fastPLDABase class.
            data: A list of ndarrays. Each person has its own list item of the 
                  shape (number_of_samples, dim_d).
        Returns:
            data: Transposed, sorted and centered input list.
            pooled_data: An array, containing all the data. It has the shape:
                         (dim_d, total_number_of_samples).
            N: Global zero order statistic of the data - the total number of 
               files.
            f: First order statistics of the data. It has the following shape:
               (dim_d, number_of_speakers).
            S: Global second order statstic of the data. It has the following 
               shape: (dim_d, dim_d).
        """
        # Transform the data to the normal column format
        data = [spk_data.T for spk_data in data] 
        
        # Sort the speakers by the number of utterances for the faster E-step
        data.sort(key=lambda x: x.shape[1]) 
    
        # Pool all the data for the more efficient M-step
        pooled_data = np.hstack(data)
        
        N = pooled_data.shape[1]  # total number of files
        
        # Substract global mean from the data
        if not hasattr(pldabase, 'mu'):
            pldabase.mu = pooled_data.mean(axis=1)[:, np.newaxis]
        pooled_data -= pldabase.mu
        data = [spk - pldabase.mu for spk in data]
        
        # Calc first and second moments
        f = [spk_data.sum(axis=1) for spk_data in data]
        f = np.asarray(f).T
        S = np.dot(pooled_data, pooled_data.T)
        return (data, pooled_data, N,f,S) 
        
    def __initialize(self, pldabase, V=None, U=None, Sigma=None):
        """Initialize the parameters for the PLDA model.
        
        Args:
            pldabase: An instance of the fastPLDABase class.
            V: A matrix to initialize V (between-speaker variability) subspace 
               of the PLDA model. By default it is initialized by random values.
            U: A matrix to initialize U (within-speaker variability) subspace 
               of the PLDA model. By default it is initialized by random values.
            Sigma: A matrix to initialize a noise covariance matrix.
        """
        if V is not None:
            pldabase.V = V
        else:
            pldabase.V = np.random.randn(pldabase.dim_d, pldabase.dim_V)
            
        if U is not None:
            pldabase.U = U
        else:
            pldabase.U = np.random.randn(pldabase.dim_d, pldabase.dim_U)
            
        if self.init_Sigma_method == 'random':
            S = np.random.randn(pldabase.dim_d, pldabase.dim_d) / pldabase.dim_d
            pldabase.Sigma = np.dot(S, S.T)
        elif (self.init_Sigma_method == 'covariance'):
            if Sigma is None:
                raise RuntimeError('Define covariance matrix to init Sigma')
            pldabase.Sigma = Sigma
        else: raise RuntimeError('Unknown init_Sigma_method')
            
        if self.plda_type == 'std':  # standard PLDA -> diagonilize                       
            pldabase.Sigma = np.diag(np.diagonal(pldabase.Sigma))
     
    def _e_step(self, pldabase, data, N, f, S):
        """Perform E-step for the PLDA learning.
        
        Args:
            pldabase: An instance of fastPLDABase class.
            data: A list of centered ndarrays. Each person has its own list item
                  of the shape (dim_d, number_of_samples).
            N: Global zero order statistic of the data - the total number of 
               files.
            f: First order statistics of the data. It has the following shape:
               (dim_d, number_of_speakers).
            S: Global second order statstic of the data. It has the following 
               shape: (dim_d, dim_d).
        Returns:
            T: A matrix with the summed multiplication between the posterior 
               expectations of the latent variables and the corresponding data 
               samples. It has the following shape: (dim_V+dim_U, dim_d).
            R_yy: A posterior covariance matrix between 'y' variables of the 
                  shape (dim_V, dim_V).
            R_yx: A posterior covariance matrix between 'y' and 'x' variables of 
                  the shape (dim_V, dim_U).
            R_xx: A posterior covariance matrix between 'x' variables of the 
                  shape (dim_U, dim_U).
            Y_md: An auxiliary matrix for the minimum-divergence step of the
                  shape (dim_V, dim_V).
        """
        dim_d = pldabase.dim_d 
        dim_V = pldabase.dim_V 
        dim_U = pldabase.dim_U
        
        V = pldabase.V
        U = pldabase.U
        
        Lambda = np.linalg.inv(pldabase.Sigma)
        
        K = len(data) # number of speakers
        
        # Set auxiliary matrices
        T = np.zeros((dim_V+dim_U, dim_d))
        R_yy = np.zeros((dim_V, dim_V))
        Ey = np.zeros((dim_V, K))
        Y_md = np.zeros((dim_V, dim_V))
        
        if pldabase.dim_U > 0:
            Q = np.linalg.inv(reduce(np.dot, [U.T, Lambda, U]) + np.eye(dim_U))
            J = reduce(np.dot, [U.T, Lambda, V])
            H = V - reduce(np.dot, [U, Q, J])
        else:
            H = V
        
        LH = np.dot(Lambda, H)
        VLH = np.dot(V.T, LH)
        
        n_previous = 0  # number of utterances for a previous person
        for i in range(len(data)):
            n = data[i].shape[1]  # number of utterances for a particular person
            if n != n_previous: 
                # Update matrices that are dependent on the number of utterances
                M_i = np.linalg.inv(n*VLH + np.eye(dim_V))
                n_previous = n
            Ey[:, [i]] = np.dot(M_i, np.dot(LH.T, f[:, [i]]))
            Eyy = np.dot(Ey[:, [i]], Ey[:, [i]].T)
            Y_md += M_i + Eyy   # it's for the MD-step
            R_yy += n*(M_i + Eyy)

        Y_md = Y_md / K
        
        T_y = np.dot(Ey, f.T)  # T_y = Ey * f'
        
        if pldabase.dim_U > 0:
            # T_x = Q * (U'*Lambda*S - J*T_y)
            T_x = np.dot(Q, reduce(np.dot, [U.T, Lambda, S]) - np.dot(J, T_y))
            # R_yx = (T_y*Lambda*U - R_yy*J')*Q 
            R_yx = np.dot(reduce(np.dot, [T_y, Lambda, U]) - 
                   np.dot(R_yy, J.T), Q) 
            
            # Auxiliary matrices
            W1 = np.dot(Lambda, U)
            W2 = np.dot(J, T_y)
            
            # R_xx = Q*(W1'*S*W1 - W1'*W2' - W2*W1 + J*R_yy*J')*Q + N*Q;
            W3 = (reduce(np.dot, [W1.T, S, W1]) - np.dot(W1.T, W2.T) -
                    np.dot(W2,W1) + reduce(np.dot, [J, R_yy, J.T]) )
            R_xx = reduce(np.dot, [Q, W3, Q]) + N*Q 
        else:
            T_x = None
            R_yx = None
            R_xx = None
        return (T_y, T_x, R_yy, R_yx, R_xx, Y_md)
    
    def __m_step(self, pldabase, R_yy, R_yx, R_xx, T_y, T_x, N, S):
        """Performs M-step for the PLDA learning.
        
        Args:
            pldabase: An instance of fastPLDABase class.
            R_yy: A posterior covariance matrix between 'y' variables of the 
                  shape (dim_V, dim_V).
            R_yx: A posterior covariance matrix between 'y' and 'x' variables of 
                  the shape (dim_V, dim_U).
            R_xx: A posterior covariance matrix between 'x' variables of the 
                  shape (dim_U, dim_U).
            T: A matrix with the summed multiplication between the posterior 
               expectations of the latent variables and the corresponding data 
               samples. It has the following shape: (dim_V+dim_U, dim_d).
            N: Global zero order statistic of the data - the total number of 
               files.
            S: Global second order statstic of the data. It has the following 
               shape: (dim_d, dim_d).
        """
        dim_V = pldabase.dim_V
        dim_U = pldabase.dim_U
        
        if T_x is not None:
            T = np.vstack([T_y, T_x])
        else:
            T = T_y
        # R = [R_yy, R_yx; R_yx', R_xx];
        if pldabase.dim_U > 0:
            R = np.vstack([np.hstack([R_yy, R_yx]), np.hstack([R_yx.T, R_xx])])
        else:
            R = R_yy
        
        VU = np.linalg.solve(R.T, T).T  # VU = T'/R;

        pldabase.V = VU[:, :dim_V].copy()
        pldabase.U = VU[:, dim_V:].copy()
        
        Sigma = (S - np.dot(VU, T)) / N
        
        # Check for the PLDA type
        if self.plda_type == 'std':
            pldabase.Sigma = np.diag(np.diagonal(Sigma))
        else:
            pldabase.Sigma = Sigma
    
    @staticmethod     
    def __md_step(pldabase, R_yy, R_yx, R_xx, Y_md, N):
        """Performs minimum-divergence step for the PLDA learning.
        
        Args:
            pldabase: An instance of fastPLDABase class.
            R_yy: A posterior covariance matrix between 'y' variables of the 
                  shape (dim_V, dim_V).
            R_yx: A posterior covariance matrix between 'y' and 'x' variables of 
                  the shape (dim_V, dim_U).
            R_xx: A posterior covariance matrix between 'x' variables of the 
                  shape (dim_U, dim_U).
            Y_md: An auxiliary matrix for the minimum-divergence step of the
                  shape (dim_V, dim_V).
            N: Total number of files.
        """
        if pldabase.dim_U > 0:
            G = np.linalg.solve(R_yy.T, R_yx).T  # G = R_yx' / R_yy;
            X_md = (R_xx - np.dot(G, R_yx)) / N
            pldabase.U = np.dot(pldabase.U, np.linalg.cholesky(X_md))
            #pdb.set_trace()
            pldabase.V = (np.dot(pldabase.V, np.linalg.cholesky(Y_md)) +
                          np.dot(pldabase.U, G))
        else:
            pldabase.V = np.dot(pldabase.V, np.linalg.cholesky(Y_md))
        
    def _print_progress(self, pldabase, pooled_data, cur_iter, max_iter, 
            remove_mu=False):
        """Print the current progress of the PLDA learing.
        
        Args:
            pldabase: An instance of fastPLDABase class.
            pooled_data: An array with the training data of the shape 
                         (number_of_features, number_of_samples).
            cur_iter: A current iteration of the learining alogrithm.
            max_iter: Total number of iterations.
            remove_mu: An indicator whether to substract PLDA mean value from 
                       the data.
        """
        progress_message = '%d-th\titeration out of %d.' % (cur_iter+1, 
                            max_iter)
        if self.compute_log_likelihood:
            progress_message += ('  Log-likelihood is %f' % 
            pldabase.compute_log_likelihood(pooled_data, remove_mu))
        print progress_message    

        
        
class fastPLDAConveyor(object):
    """This class performs scroing operations on the pooled data.
    
    Attributes:
        pldabase: An instance of the fastPLDABase class, specifying parameters 
                   for the PLDA model
        model_data: A list of ndarrays with the model i-vectors. Each person has 
                    its own list item of the shape 
                    number_of_elements x number_of_features
        test_data: A list of ndarrays with the test i-vectors. Each person has 
                   its own list item of the shape 
                   number_of_elements x number_of_features
    """
    
    def __init__(self, pldabase):
        """
        Args:
            pldabase: An instance of the fastPLDABase class, specifying 
                       parameters for the PLDA model
        """
        self.pldabase = pldabase
    
    def save(self, config):
        """Save fastPLDAConveyor instance to the hdf5 file.
        
        Args:
            config: A path to the hdf5 file to store the data.
        """
        raise RuntimeError('fastPLDAConveyor.save() is not implemented yet')
        
    def load(self, config):
        """Load fastPLDAConveyor instance from the hdf5 file.
        
        Args:
            config: A path to the hdf5 file to load the data.
        """
        raise RuntimeError('fastPLDAConveyor.load() is not implemented yet')
        
    def enrol_samples(self, model_data, test_data):
        """Enrol model and test samples.
        
        Args:
            model_data: A list of ndarrays with model ivectors. Each person has 
                        its own list item of the shape 
                        (number_of_samples, number_of_features)
            test_data: A list of ndarrays with test ivectors. Each claimed 
                       person has its own list item of the shape 
                       (number_of_samples, number_of_features)
        """
        
        mu = self.pldabase.mu
        
        # Transform the data to the normal column format and substract a mean
        self.model_data  = [np.asarray(spk).T - mu for spk in model_data] 
        self.test_data   = [np.asarray(spk).T - mu for spk in test_data]
        
    def compute_log_likelihood_ratio(self, full_matrix = True, 
                                     enrol_type='averaged'):
        """Compute PLDA scores between enrollment data and test data.
        
        Args:
            full_matrix: This indicator specifies whether we need a full matrix 
                         of scores or only one-to-one comparisons.
            enrol_type: Defines how we treat models which have several 
                        utterances. It could take the following values
                        'averaged': Average all ivectors for each model.
                        'by-the-book-scoring': Apply the standard PLDA scoring
                                               formula the to multiple samples.
        
        Returns:
            An array with the scores.
        """
        V = self.pldabase.V
        if hasattr(self.pldabase, 'U'):
            U = self.pldabase.U
        else:
            U = np.zeros((self.pldabase.dim_d,0))
        Sigma = self.pldabase.Sigma
        
        if enrol_type == 'averaged':
            model_data_avr_list = [spk.mean(axis=1) for spk in self.model_data]
            model_data_avr = np.asarray(model_data_avr_list).T
            
            # Arrange enrollment data to pair test data
            model_data = np.zeros(model_data_avr.shape) # init
            i = 0
            for j in range(len(self.model_data)):
                # number of test samples for i-th person
                k = 1 # self.test_data[0].shape[1]
                # duplicate 'k' times the corresponding model data
                model_data[:, i:i+k] = np.tile(model_data_avr[:, [j]], (1, k))
                i += k 
            
            Sigma_wc = np.dot(U, U.T) + Sigma
            Sigma_ac = np.dot(V, V.T)
            Sigma_tot = Sigma_wc + Sigma_ac
            
            Lambda = 0.25*(-np.linalg.inv(Sigma_wc + 2*Sigma_ac) + 
                          np.linalg.inv(Sigma_wc))
            Gamma = 0.25*(-np.linalg.inv(Sigma_wc + 2*Sigma_ac) - 
                     np.linalg.inv(Sigma_wc) + 2*np.linalg.inv(Sigma_tot))
            
            # Transpose the data for convenience
            model_data = model_data.T
            test_data = np.hstack(self.test_data).T
            
            Gamma11 = np.sum( np.dot(model_data, Gamma)*model_data, axis=1)
            Gamma22 = np.sum( np.dot(test_data, Gamma)*test_data, axis=1)
            
            scores = 2*reduce(np.dot, [model_data, Lambda, test_data.T])
            scores += Gamma11[:, np.newaxis]
            scores += Gamma22[np.newaxis, :]
            
            ## Calculating 'k' piece-by-piece:
            
            #k = (np.log(np.linalg.det(Sigma_tot)) - 
                #0.5*np.log(np.linalg.det(Sigma_wc + 2*Sigma_ac)) - 
                #0.5*np.log(np.linalg.det(Sigma_wc)))
            
            # Compute log-determinant of the Sigma_tot matrix (first line)
            E, junk = np.linalg.eig(Sigma_tot)
            log_det_first = np.sum(np.log(E))    
            
            # Compute log-determinant of the second-line matrix
            E, junk = np.linalg.eig(Sigma_wc + 2*Sigma_ac)
            log_det_second = np.sum(np.log(E))    
            
            # Compute log-determinant of the third-line matrix
            E, junk = np.linalg.eig(Sigma_wc)
            log_det_third = np.sum(np.log(E))    
            
            # Put it all together
            k = log_det_first - 0.5*log_det_second - 0.5*log_det_third
            
            scores += k
            
            if not full_matrix:
                scores = np.diagonal(scores)
            
        elif enrol_type == 'by-the-book-scoring':
            raise RuntimeError('By-the-book scoring is not implemented yet')
        else:
            raise RuntimeError('Unknown enrol_type')
            
        return scores
