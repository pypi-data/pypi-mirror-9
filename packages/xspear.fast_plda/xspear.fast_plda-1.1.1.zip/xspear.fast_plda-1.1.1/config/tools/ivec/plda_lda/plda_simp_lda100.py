#!/usr/bin/env python

import xspear
import bob

tool = xspear.fast_plda.tools.fastPLDA

# 2/ GMM Training
n_gaussians = 2048
iterk = 25
iterg_train = 25
end_acc = 0.0001
var_thd = 0.0001
update_weights = True
update_means = True
update_variances = True
norm_KMeans = True

# 3/ IVector Training
rt = 600
relevance_factor = 4
max_iterations = 25
n_iter_enrol = 1

# 4/ JFA Enrolment and scoring
iterg_enrol = 1
convergence_threshold = 0.0001
variance_threshold = 0.0001
relevance_factor = 4
responsibilities_threshold = 0


# 5/ PLDA training
# Common parameters
PLDA_TRAINING_ITERATIONS = 5 # Maximum number of iterations for the EM loop
INIT_SEED = 11 # seed for initializing

PLDA_DO_MD_STEP = True # indication whether to do a minimum-divergence step
PLDA_COMPUTE_LOG_LIKELIHOOD = True
FAST_PLDA_TYPE = 'simp' # 'std', 'simp', 'two-cov'
SUBSPACE_DIMENSION_OF_V = 100 # Size of subspace V
SUBSPACE_DIMENSION_OF_U = 0 # Size of subspace U
INIT_V_METHOD = 'random' # bob.trainer.PLDATrainer.BETWEEN_SCATTER
INIT_U_METHOD = 'random' # bob.trainer.PLDATrainer.WITHIN_SCATTER
INIT_SIGMA_METHOD = 'covariance' # 'covariance'
INIT_SIGMA_SCALE = 0.25 # Parameter to multiply initial noise matrix. It's
                       # advisible to have it less than 1, for strictly 
                       # increasing log-likelihood (empirical observation).

# Parameters for two-cov model
INIT_INV_B_METHOD = 'covariance' # Method to initialize matrix invB 
INIT_INV_W_METHOD = 'covariance' # Method to initialize matrix invW

# Two-stage PLDA parameters
TWO_STAGE_PLDA_TRAINING_ITERATIONS = 5
SUBSPACE_DIMENSION_OF_U2 = 100
INIT_U2_METHOD = 'random'

# 6/ LDA training
# LDA subspace; if not set, LDA subspace is not truncated
LDA_SUBSPACE_DIMENSION = 100

# cosine scoring? Default plda_scoring
scoring_type='plda'

# Full Matrix scores?
full_matrix_flag = False
