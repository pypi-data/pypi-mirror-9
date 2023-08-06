#!/usr/bin/env python

import spear
import numpy

feature_extractor = spear.feature_extraction.Cepstral

# Cepstral parameters
win_length_ms = 30 # The window length of the cepstral analysis in milliseconds
win_shift_ms = 15 # The window shift of the cepstral analysis in milliseconds
n_filters = 31  # The number of filter bands
dct_norm = False # A factor by which the cepstral coefficients are multiplied
f_min = 0.0 # The minimal frequency of the filter bank
f_max = 8000 # The maximal frequency of the filter bank
delta_win = 2 # The integer delta value used for computing the first and second order derivatives
mel_scale = True # Tell whether cepstral features are extracted on a linear (LFCC) or Mel (MFCC) scale
withEnergy = False
withDelta = True
withDeltaDelta = True
withDeltaEnergy = False
withDeltaDeltaEnergy = False
n_ceps = 30 # The number of cepstral coefficients
pre_emphasis_coef = 0.97 # The coefficient used for the pre-emphasis
features_mask = numpy.arange(0,90) # Cepstral features + Energy + 1st and 2nd derivatives


# Normalization
normalizeFeatures = False # The flag to enable or disable the zero means and unit variance normalization
