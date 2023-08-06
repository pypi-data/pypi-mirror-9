"""This file implements functionality for the two-cov PLDA model"""

import numpy as np
import bob
import os
import pdb

from spear import utils

class twoCovBase(object):
    """This class stores the parameters for the two-covariance model.
    
    Attributes:
        dim_d: Dimensionality of the input feature vectors.
        invB: Covariance matrix of between speaker variability.
        invW: Covariance matrix of within speaker variability.
        mu: The mean vector of the latent speaker variables.
    """
    
    def __init__(self, dim_d):
        """
        Args:
            dim_d: Dimensionality of the input feature vectors.
        """
        self.dim_d = dim_d
        self.invB = None
        self.invW = None
        self.mu = None
      
    def save(self, hdf5file):
        """ Save twoCovBase instance to the hdf5 file.
        
        Args:
            hdf5file: A path to the hdf5 file to store the data.
        """
        utils.ensure_dir(os.path.dirname(hdf5file))
        f = bob.io.HDF5File(str(hdf5file), 'w')
        f.set('dim_d', self.dim_d)
        f.set('invB', self.invB)
        f.set('invW', self.invW)
        f.set('mu', self.mu)
        f.set('type', 'TwoCovPLDA')
    
    def compute_log_likelihood(self, data):
        """Comute the log likelihood for the whole dataset.
        
        Args:
            data: An array of the shape (number_of_features, number_of_samples).
        """
        (D, N) = data.shape

        centered_data = data - self.mu
            
        # Total covariance matrix for the model with integrated out latent 
        # variables
        Sigma_tot = self.invB + self.invW
        
        # Compute log-determinant of the Sigma_tot matrix
        E, junk = np.linalg.eig(Sigma_tot)
        log_det = np.sum(np.log(E))
        
        return -0.5*(N*D*np.log(2*np.pi) + N*log_det + 
               np.sum(np.sum(np.dot(centered_data.T,np.linalg.inv(Sigma_tot)) *
               centered_data.T, axis=1)))
        
class twoCovTrainer(object):
    """This class trains a two-covariance model.
    
    Attributes:
        training_iterations: Maximum number of the training iterations.
        seed: Seed for the random number generator.
        init_invB_method: Method to initialize invB matrix.
        init_invW_method: Method to initialize invW matrix.
        training_threshold: Threshold for ending the EM loop.
        compute_log_likelihood: Indication whether to compute a log-likelihood
                                of the training data during EM-algorithm
    """

    def __init__(self, training_iterations, config=None):
        """
        Args:
            training_iterations: Maximum number of the training iterations.
            config: A class with the following fields: 
                INIT_SEED: Seed for the random number generator.
                INIT_INV_B_METHOD: Method to initialize invB matrix.
                INIT_INV_W_METHOD: Method to initialize invW matrix.
                PLDA_TRAINING_THRESHOLD: Threshold for ending the EM loop.
                PLDA_COMPUTE_LOG_LIKELIHOOD: Indicator for the LL computation.
        """
        self.training_iterations = training_iterations
        if config is not None:
            self.seed = config.INIT_SEED
            np.random.seed(self.seed)  # set the seed for the randomizer
                    
            self.init_invB_method = config.INIT_INV_B_METHOD
            self.init_invW_method = config.INIT_INV_W_METHOD      
            self.compute_log_likelihood = config.PLDA_COMPUTE_LOG_LIKELIHOOD

    def train(self, pldabase, data):
        """Train the parameters for the PLDA model.
        
        Args:
            pldabase: An instance of twoCovBase class.
            data: A list of ndarrays. Each person has its own list item of the 
                  shape (number_of_samples, number_of_features).
        """
        data, pooled_data, N, f, S, mu  = self._preprocessing(data)
        # Initialize PLDA parameters
        self.__initialize(pldabase, cov=S/N-np.dot(mu, mu.T), mu=mu) 

        for i in xrange(self.training_iterations):
            T, R, Y = self._e_step(pldabase, data, N, f, S)
            self.__m_step(pldabase, T, R, Y, N, S)
            # Print current progress
            self._print_progress(pldabase, pooled_data, i)
    
    def _preprocessing(self, data):
        """Apply preprocessing necessary for the EM-algorithm.
        
        Args:
            data: A list of ndarrays. Each person has its own list item of the 
                  shape (number_of_samples, dim_d).
        Returns:
            data: Transposed and sorted input list.
            pooled_data: An array, containing all the data. It has the shape:
                         (dim_d, total_number_of_samples).
            N: Global zero order statistic of the data - the total number of 
               files.
            f: First order statistics of the data. It has the following shape:
               (dim_d, number_of_speakers).
            S: Global second order statstic of the data. It has the following 
               shape: (dim_d, dim_d).
            mu: Sample mean value.
        """
        # Transform the data to the normal column format
        data = [spk_data.T for spk_data in data] 
        
        # Sort the speakers by the number of utterances for the faster E-step
        data.sort(key=lambda x: x.shape[1]) 
    
        # Pool all the data for the more efficient M-step
        pooled_data = np.hstack(data)
        
        N = pooled_data.shape[1]  # total number of files
        
        mu = pooled_data.mean(axis=1)[:, np.newaxis]
        
        # Calc first and second moments
        f = [spk_data.sum(axis=1) for spk_data in data]
        f = np.asarray(f).T
        S = np.dot(pooled_data, pooled_data.T)
        return (data, pooled_data, N, f, S, mu)
          
    def __initialize(self, pldabase, cov=None, mu=None):
        """Initialize the parameters for the two-covariance model.
        
        Args:
            pldabase: An instance of the twoCovBase class.
            cov: Sample covariance matrix.
            mu: Sample mean vector.
        """
        if mu is None:
            raise RuntimeError('Define mean vector to initialize mu')
        else:
            pldabase.mu = mu
            
        if (self.init_invB_method == 'covariance'):
            if cov is None:
                raise RuntimeError('Define covariance matrix to initialize invB')
            pldabase.invB = cov
        else: raise RuntimeError('Unknown init_invB_method')
        
        if (self.init_invW_method == 'covariance'):
            if cov is None:
                raise RuntimeError('Define covariance matrix to initialize invW')
            pldabase.invW = cov
        else: raise RuntimeError('Unknown init_invW_method')
     
    def _e_step(self, pldabase, data, N, f, S):
        """Perform E-step for the two-covariance learning.
        
        Args:
            pldabase: An instance of twoCovBase class.
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
               samples. It has the following shape: (dim_d, dim_d).
            R: A posterior covariance matrix between speaker latent variables of
               the shape (dim_d, dim_d).
            Y: Aggregated vector of the posterior expectation values for each
               sample. It has the size (dim_d, 1).
        """
        dim_d = pldabase.dim_d 
        
        B = np.linalg.inv(pldabase.invB)
        W = np.linalg.inv(pldabase.invW)
        mu = pldabase.mu
        
        K = len(data) # number of individuals
        
        # Initialize output matrices
        T = np.zeros((dim_d, dim_d))
        R = np.zeros((dim_d, dim_d))
        Y = np.zeros((dim_d, 1))
        
        # Set auxiliary matrix
        Bmu = np.dot(B, mu)

        n_previous = 0  # number of utterances for a previous person
        for i in range(len(data)):
            n = data[i].shape[1]  # number of utterances for a particular person
            if n != n_previous: 
                # Update matrix that is dependent on the number of utterances
                invL_i = np.linalg.inv(B + n*W)
                n_previous = n
            
            gamma_i = Bmu + np.dot(W,f[:,[i]])
            Ey_i = np.dot(invL_i, gamma_i) 
            T += np.dot(Ey_i, f[:,[i]].T)
            R += n*(invL_i + np.dot(Ey_i,Ey_i.T))
            Y += n*Ey_i

        return (T, R, Y)
    
    def __m_step(self, pldabase, T, R, Y, N, S):
        """Performs M-step for the PLDA learning.
        
        Args:
            pldabase: An instance of twoCovBase class.
            T: A matrix with the summed multiplication between the posterior 
               expectations of the latent variables and the corresponding data 
               samples. It has the following shape: (dim_d, dim_d).
            R: A posterior covariance matrix between speaker latent variables of
               the shape (dim_d, dim_d).
            Y: Aggregated vector of the posterior expectation values for each
               sample. It has the size (dim_d, 1).
            N: Global zero order statistic of the data - the total number of 
               files.
            S: Global second order statstic of the data. It has the following 
               shape: (dim_d, dim_d).
        """
        pldabase.mu = Y / N
        pldabase.invB = (R - np.dot(Y, Y.T)/N)/N
        pldabase.invW = (S - (T + T.T) + R)/N

    def _print_progress(self, pldabase, pooled_data, cur_iter):
        """Print the current progress of the PLDA learing.
        
        Args:
            pldabase: An instance of twoCovBase class.
            pooled_data: An array with the training data of the shape 
                         (number_of_features, number_of_samples).
            cur_iter: A current iteration of the learining alogrithm.
        """
        progress_message = '%d-th\titeration out of %d.' % (cur_iter+1,
                           self.training_iterations)
        if self.compute_log_likelihood:
            progress_message += ('  Log-likelihood is %f' % 
            pldabase.compute_log_likelihood(pooled_data))
        print progress_message
        
class twoCovConveyor(object):
    """This class performs scroing operations on the pooled data.
    
    Attributes:
        plda_base: An instance of the twoCovBase class, specifying parameters 
                   for the PLDA model.
        model_data: A list of ndarrays with the model i-vectors. Each person has 
                    its own list item of the shape.
                    number_of_elements x number_of_features.
        test_data: A list of ndarrays with the test i-vectors. Each person has 
                   its own list item of the shape 
                   number_of_elements x number_of_features.
    """
    
    def __init__(self, pldabase):
        """
        Args:
            plda_base: An instance of the twoCovBase class, specifying 
                       parameters for the two-covariance model
        """
        self.plda_base = pldabase
    
    def save(self, config):
        """Save twoCovConveyor instance to the hdf5 file.
        
        Args:
            config: A path to the hdf5 file to store the data.
        """
        raise RuntimeError('twoCovConveyor.save() is not implemented yet')
        
    def load(self, config):
        """Load twoCovConveyor instance from the hdf5 file.
        
        Args:
            config: A path to the hdf5 file to load the data.
        """
        raise RuntimeError('twoCovConveyor.load() is not implemented yet')
        
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
        
        mu = self.plda_base.mu
        # Transform the data to the normal column format and substract a mean
        self.model_data  = [np.asarray(spk).T - mu for spk in model_data] 
        self.test_data   = [np.asarray(spk).T - mu for spk in test_data]
        
    def compute_log_likelihood_ratio(self, full_matrix = True, 
                                     enrol_type='averaged'):
        """Compute two-covariance scores between enrollment data and test data.
        
        Args:
            full_matrix: This indicator specifies whether we need a full matrix 
                         of scores or only one-to-one comparisons.
            enrol_type: Defines how we treat models which have several 
                        utterances. It could take the following values
                        'averaged': Average all ivectors for each model.
                        'by-the-book-scoring': Apply two-covariance scoring
                                               formula to the multiple samples.
        
        Returns:
            An array with the scores.
        """
        
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
            
            Sigma_wc = self.plda_base.invW
            Sigma_ac = self.plda_base.invB
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
