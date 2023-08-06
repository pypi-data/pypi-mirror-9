#!/usr/bin/env python

import spear
import numpy

feature_extractor = spear.feature_extraction.Cepstral

# Cepstral parameters
win_length_ms = 20 # The window length of the cepstral analysis in milliseconds
win_shift_ms = 10 # The window shift of the cepstral analysis in milliseconds
n_filters = 24 # The number of filter bands
dct_norm = False # A factor by which the cepstral coefficients are multiplied
f_min = 0.0 # The minimal frequency of the filter bank
f_max = 4000 # The maximal frequency of the filter bank
delta_win = 2 # The integer delta value used for computing the first and second order derivatives
mel_scale = False # Tell whether cepstral features are extracted on a linear (LFCC) or Mel (MFCC) scale
withEnergy = True
withDelta = True
withDeltaDelta = True
withDeltaEnergy = True
withDeltaDeltaEnergy = True
n_ceps = 19 # 0-->18 # The number of cepstral coefficients
pre_emphasis_coef = 0.95 # The coefficient used for the pre-emphasis
features_mask = numpy.arange(0,60) # Cepstral features + Energy + 1st and 2nd derivatives


# Normalization
normalizeFeatures = True # The flag to enable or disable the zero means and unit variance normalization

