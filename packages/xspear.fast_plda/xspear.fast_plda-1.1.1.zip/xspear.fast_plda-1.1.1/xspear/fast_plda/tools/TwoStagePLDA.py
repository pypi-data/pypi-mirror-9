"""This file implements functionality for the two-stage PLDA model"""

import numpy as np
import pdb

from spear import utils
from fastPLDA import *

class TwoStagePLDABase(fastPLDABase):
    """ Contains extended list of parameters for the two-stage model
    
    Attributes:
        dim_d: Dimensionality of the input feature vectors.
        dim_V: Dimensionality of the V subspace/matrix of the PLDA model.
        dim_U: Dimensionality of the U subspace/matrix of the PLDA model.
        V1: The matrix of between speaker variability for the first stage.
        V2: The matrix of between speaker variability for the second stage.
        U1: The matrix of within speaker variability.
        U2: The matrix of vocoder artifacts variability.
        Sigma1: Covariance noise matrix for the first stage.
        Sigma2: Covariance noise matrix for the second stage.
        mu: The mean vector of the PLDA model.
    """
        
    def save(self, hdf5file):
        """ Save TwoStagePLDABase instance to the hdf5 file. """
        utils.ensure_dir(os.path.dirname(hdf5file))
        f = bob.io.HDF5File(str(hdf5file), 'w')
        f.set('V1', self.V1)
        f.set('V2', self.V2)
        if self.U1.shape[1] > 0: #it is not singular
            f.set('U1', self.U1)
        f.set('U2', self.U2)
        f.set('mu1', self.mu1)
        f.set('mu2', self.mu2)
        f.set('Sigma1', self.Sigma1)
        f.set('Sigma2', self.Sigma2)
        f.set('dim_d', self.dim_d)
        f.set('dim_V', self.dim_V)
        f.set('dim_U', self.dim_U)
        f.set('type', 'TwoStagePLDA')
      
    def compute_log_likelihood(self, data, remove_mu=True, V_idx=1, Sigma_idx=1, U_idx=1):
        """Comute the log likelihood for the whole dataset.
        
        Args:
            data: An array of the shape (number_of_features, number_of_samples).
            remove_mu: An indicator whether to substract PLDA mean value from 
                       the data.
            V_idx: An index of the V matrix to use.
            Sigma_idx: An index of the Sigma matrix to use.
        """
        if remove_mu: 
            centered_data = data - self.mu
        else:
            centered_data = data
            
        # Select appropriate V matrix
        if hasattr(self, 'V'): # Model training is in progress
            V = self.V
        elif V_idx == 1:
            V = self.V1
        else:
            V = self.V2
        
        # Select appropriate Sigma matrix
        if hasattr(self, 'Sigma'): # Model training is in progress
            Sigma = self.Sigma
        elif Sigma_idx == 1:
            Sigma = self.Sigma1
        else:
            Sigma = self.Sigma2
            
        if hasattr(self, 'U'): # Model training is in progress
            U = self.U
        elif U_idx == 1:
            U = self.U1
        else:
            U = self.U2
            
        # Total covariance matrix for the model with integrated out latent 
        # variables
        Sigma_tot = (np.dot(V, V.T) + np.dot(U, U.T) + Sigma)
        
        # Compute log-determinant of the Sigma_tot matrix
        E, junk = np.linalg.eig(Sigma_tot)
        log_det = np.sum(np.log(E))
        
        (D, N) = data.shape
                
        return -0.5*(N*D*np.log(2*np.pi) + N*log_det + 
               np.sum(np.sum(np.dot(centered_data.T,np.linalg.inv(Sigma_tot)) *
               centered_data.T, axis=1)))

class TwoStagePLDATrainer(fastPLDATrainer):
    """Train the PLDA model with an additional subspace for a second stage.
    
    Attributes:
        training_iterations: Maximum number of the training iterations for the
                             first stage.
        training_iterations2: Maximum number of the training iterations for the
                              second stage.
        seed: Seed for the random number generator.
        init_V_method: A method to initialize V matrix.
        init_U_method: A method to initialize U matrix for the first stage.
        init_U2_method: A method to initialize U matrix for the second stage.
        init_Sigma_method: A method to initialize Sigma matrix.
        training_threshold: Threshold for ending the EM loop.
        do_md_step: Indicator for the minimum-divergence step.
        compute_log_likelihood: Indication whether to compute a log-likelihood
                                of the training data during EM-algorithm
        Sigma_scale: Parameter that multiplies initial Sigma matrix
    """
    def __init__(self, training_iterations, config=None):
        """
        Args:
            training_iterations: A tuple, containing the maximum number of the 
                                 training iterations for both stages.
            config: A class with the following fields: 
                INIT_SEED: A seed for the random number generator.
                INIT_V_METHOD: A method to initialize V matrix.
                INIT_U_METHOD: A method to initialize U matrix for the first 
                                stage.
                INIT_U2_METHOD: A method to initialize U matrix for the second 
                                stage.
                INIT_SIGMA_METHOD: A method to initialize Sigma matrix.
                PLDA_TRAINING_THRESHOLD: A threshold for ending the EM loop.
                PLDA_DO_MD_STEP: An indicator for the minimum-divergence step.
                PLDA_COMPUTE_LOG_LIKELIHOOD: An indicator for the log-likelihood
                                             computation.
                INIT_SIGMA_SCALE: A parameter that multiplies initial Sigma 
                                  matrix.
                SUBSPACE_DIMENSION_OF_U2: A number of dimension of U matrix for
                                          the second stage of learning.
        """
        self.training_iterations2 = training_iterations[1]
        fastPLDATrainer.__init__(self, training_iterations[0], config)
        
        if config is not None:
            self.init_U2_method = config.INIT_U2_METHOD
            self.dim_U2 = config.SUBSPACE_DIMENSION_OF_U2
            
    def train(self, pldabase, data1, data2):
        """Train the parameters for the two-stage PLDA model.
        
        Args:
            pldabase: An instance of newPLDABase class to store the parameters.
            data1: A list of ndarrays for the first stage. Each person has its 
                   own list item of the shape 
                   (number_of_samples, number_of_features)
            data2: A list of ndarrays for the first stage. Each person has its 
                   own list item of the shape 
                   (number_of_samples, number_of_features)
        """
        ## FIRST STAGE
        print 'Training of the first stage with %d identities' % len(data1)
        fastPLDATrainer.train(self, pldabase, data1)
        
        ## SECOND STAGE
        print 'Training of the second stage with %d identities' % len(data2)
        
        # Initialize PLDA parameters
        self.__initialize(pldabase)
        
        data, pooled_data, N, f, S = self._preprocessing(pldabase, data2)
        
        for i in xrange(self.training_iterations2):
            junk, T_x, R_yy, R_yx, R_xx, junk = self._e_step(pldabase, data, N, 
                                                            f, S)
            self.__m_step(pldabase, R_yx, R_xx, T_x)
            if self.do_md_step:
                self.__md_step(pldabase, R_yy, R_yx, R_xx, N) 
            
            # Print current progress
            self._print_progress(pldabase, pooled_data, i, 
                                self.training_iterations2)
        
        self.__finalize(pldabase)
    
    def __initialize(self, pldabase):
        """Initialize the parameters for the second stage of the two-stage
        PLDA model.
        
        Args:
            pldabase: An instance of the TwoStagePLDABase class.
        """
        # Save the matrices of the first stage
        pldabase.V1 = np.copy(pldabase.V)
        pldabase.Sigma1 = np.copy(pldabase.Sigma)
        pldabase.U1 = np.copy(pldabase.U)
        
        pldabase.mu1 = np.copy(pldabase.mu)
        del(pldabase.mu)
        
        # Integrate out channel latent variable and set the model to be
        # simplified one.

        pldabase.Sigma += np.dot(pldabase.U, pldabase.U.T)
        self.plda_type = 'simp'
        
        pldabase.dim_U = self.dim_U2
        if self.init_U2_method == 'random':
            pldabase.U = np.random.randn(pldabase.dim_d, pldabase.dim_U)
        else:
            raise RuntimeError('Unknown init_U2_method')
    
    @staticmethod    
    def __m_step(pldabase, R_yx, R_xx, T_x):
        """Performs M-step for the second stage of the two-stage PLDA learning.
        
        Args:
            pldabase: An instance of TwoStagePLDABase class.
            R_yx: A posterior covariance matrix between 'y' and 'x' variables of 
                  the shape (dim_V, dim_U).
            R_xx: A posterior covariance matrix between 'x' variables of the 
                  shape (dim_U, dim_U).
            T_x: A matrix with the summed multiplication between the posterior 
                 expectations of the latent channel variables and the 
                 corresponding data samples. It has the following shape: 
                 (dim_U, dim_d).
        """
        pldabase.U = np.linalg.solve(R_xx, T_x - np.dot(pldabase.V, R_yx).T).T
    
    @staticmethod
    def __md_step(pldabase, R_yy, R_yx, R_xx, N):
        """Performs minimum-divergence step for the two-stage PLDA learning.
        
        Args:
            pldabase: An instance of TwoStagePLDABase class.
            R_yy: A posterior covariance matrix between 'y' variables of the 
                  shape (dim_V, dim_V).
            R_yx: A posterior covariance matrix between 'y' and 'x' variables of 
                  the shape (dim_V, dim_U).
            R_xx: A posterior covariance matrix between 'x' variables of the 
                  shape (dim_U, dim_U).
            N: Total number of files.
        """
        G = np.linalg.solve(R_yy.T, R_yx).T  # G = R_yx' / R_yy;
        X_md = (R_xx - np.dot(G, R_yx)) / N
        pldabase.U = np.dot(pldabase.U, np.linalg.cholesky(X_md))
        pldabase.V += np.dot(pldabase.U, G)
    
    def __finalize(self, pldabase):
        """Finalize training of the two-stage model
        
        Args:
            pldabase: An instance of TwoStagePLDABase class.
        """
        pldabase.V2 = np.copy(pldabase.V)
        del(pldabase.V)
        
        pldabase.Sigma2 = np.copy(pldabase.Sigma)
        del(pldabase.Sigma)
        
        pldabase.U2 = np.copy(pldabase.U)
        del(pldabase.U)
        
        pldabase.mu2 = np.copy(pldabase.mu)
        del(pldabase.mu)

class TwoStagePLDAConveyor(fastPLDAConveyor):
    """This class performs scroing operations on the pooled data for the 
    two-stage model.
    
    Attributes:
        pldabase: An instance of the TwoStagePLDABase class, specifying 
                   parameters for the PLDA model
        model_data: A list of ndarrays with the model i-vectors. Each person has 
                    its own list item of the shape 
                    number_of_elements x number_of_features
        test_data: A list of ndarrays with the test i-vectors. Each person has 
                   its own list item of the shape 
                   number_of_elements x number_of_features
    """
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
        self.model_data  = model_data
        self.test_data   = test_data
        
    def compute_standalone_cm_scores(self):
        """Compute anti-spoofing scores using both V1 and V2 matrices
        
        Returns:
            An array with the scores.
        """
        
        V1 = self.pldabase.V1
        V2 = self.pldabase.V2
        U2 = self.pldabase.U2
        Sigma2 = self.pldabase.Sigma2 # Sigma2 = Sigma1 + np.dot(U1,U1.T)
        mu1 = self.pldabase.mu1
        mu2 = self.pldabase.mu2
        
        testdata_1   = [np.asarray(spk).T - mu1 for spk in self.test_data]
        testdata_2   = [np.asarray(spk).T - mu2 for spk in self.test_data]
        
        test_data_1 = np.hstack(testdata_1).T
        test_data_2 = np.hstack(testdata_2).T
        
        #test_data = np.hstack(self.test_data).T
                    
        Sigma_human = np.dot(V1, V1.T) + Sigma2 # Covariance for "human" PLDA
        # Covariance for "synthesis" PLDA:
        Sigma_synth = np.dot(V2, V2.T) + np.dot(U2, U2.T) + Sigma2
        # Auxilary matrices to find the ratio:
        #Lambda = np.linalg.inv(Sigma_human) - np.linalg.inv(Sigma_synth)
        Lambda_1 = np.linalg.inv(Sigma_human)
        Lambda_2 = np.linalg.inv(Sigma_synth)
        
        E_1, junk = np.linalg.eig(Sigma_human)
        E_2, junk = np.linalg.eig(Sigma_synth)
        sigma_lr = np.sum(np.log(E_2)) - np.sum(np.log(E_1))
        
        #sigma_lr = np.sqrt(np.linalg.det(Sigma_synth) / np.linalg.det(Sigma_human))
        
        scores = 0.5*(sigma_lr 
                 + np.sum( np.dot(test_data_2, Lambda_2)*test_data_2, axis=1) 
                 - np.sum( np.dot(test_data_1, Lambda_1)*test_data_1, axis=1))
              
        return scores
    
    def __compute_log_probs__(self, A, B, model_data, test_data):
        """Compute log probability for the hypothesis with A and B as blocks of its
        covariance matrix
        
        For more details see pages I.58-60 in my notebook
        """
        invA = np.linalg.inv(A)
        
        M = np.linalg.inv(A - reduce(np.dot, [B, invA, B]))
        
        #log_det_Omega = np.log(np.linalg.det(A) * np.linalg.det(M))
        E_1, junk = np.linalg.eig(A)
        E_2, junk = np.linalg.eig(M)
        log_det_Omega = np.sum(np.log(E_1)) + np.sum(np.log(E_2))
        
        Lambda = reduce(np.dot, [invA, B, M])
        
        Gamma11 = np.sum( np.dot(model_data, M)*model_data, axis=1)
        Gamma22 = np.sum( np.dot(test_data, M)*test_data, axis=1)
        
        log_probes = -2*reduce(np.dot, [model_data, Lambda, test_data.T])
        log_probes += Gamma11[:, np.newaxis]
        log_probes += Gamma22[np.newaxis, :]
        log_probes += log_det_Omega
        log_probes += test_data.shape[1] * np.log(2*np.pi)
        log_probes *= -0.5
        return log_probes
        
    def compute_log_likelihood_ratio(self):
        """Compute scores between enrolment and test data for two-stage PLDA.
        
        The likelihood for the negative hypothesis is a maximum of the 
        likelihoods for zero-effort impostor and spoofing hypotheses.
        
        Returns:
            An array with the scores.
        """
        # Copy PLDA parameters
        V1 = self.pldabase.V1
        V2 = self.pldabase.V2
        U2 = self.pldabase.U2
        Sigma1 = self.pldabase.Sigma1
        Sigma2 = self.pldabase.Sigma2
        mu1 = self.pldabase.mu1
        mu2 = self.pldabase.mu2
        
        # Prepare data
        # Substract means
        model_data_1  = [np.asarray(spk).T - mu1 for spk in self.model_data] 
        testdata_1   = [np.asarray(spk).T - mu1 for spk in self.test_data]
        
        model_data_2  = [np.asarray(spk).T - mu2 for spk in self.model_data] 
        testdata_2   = [np.asarray(spk).T - mu2 for spk in self.test_data]
        
        model_data_avr_list_1 = [spk.mean(axis=1) for spk in model_data_1]
        model_data_1 = np.asarray(model_data_avr_list_1)
        test_data_1 = np.hstack(testdata_1).T
        
        model_data_avr_list_2 = [spk.mean(axis=1) for spk in model_data_2]
        model_data_2 = np.asarray(model_data_avr_list_2)
        test_data_2 = np.hstack(testdata_2).T
        
        # Precompute auxilary matrices
        B1 = np.dot(V1,V1.T)
        A1 = B1 + Sigma2
        log_probs1 = self.__compute_log_probs__(A1, B1, model_data_1, test_data_1)
        
        A2 = A1
        B2 = np.zeros(A2.shape)
        log_probs2 = self.__compute_log_probs__(A2, B2, model_data_2, test_data_2)
        
        B3 = np.dot(V2, V2.T)
        A3 = B3 + np.dot(U2, U2.T) + Sigma2
        log_probs3 = self.__compute_log_probs__(A3, B3, model_data_2, test_data_2)
        
        A4 = np.dot(V2, V2.T) + np.dot(U2, U2.T) + Sigma2
        B4 = np.zeros(A4.shape)
        log_probs4 = self.__compute_log_probs__(A4, B4, model_data_2, test_data_2)

        log_negative_probs = reduce(np.maximum, [log_probs2, log_probs4])
        
        # return log_probs1 - log_negative_probs
        
        ## NEW stuff
        #B5 = np.dot(V2, V2.T) + np.dot(U2, U2.T)
        #A5 = B5 + Sigma2
        #log_probs5 = self.__compute_log_probs__(A1, B1, model_data, test_data)
        #log_negative_probs = reduce(np.maximum, [log_probs2, log_probs5])
        
        return log_probs1 - log_negative_probs
        
        
        
        
