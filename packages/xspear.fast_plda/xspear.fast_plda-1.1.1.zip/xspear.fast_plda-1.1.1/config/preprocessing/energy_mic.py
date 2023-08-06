#!/usr/bin/env python

import spear

preprocessor = spear.preprocessing.Energy

# Cepstral parameters
win_length_ms = 30
win_shift_ms = 15

# VAD parameters
alpha = 2 
max_iterations = 50
smoothing_window = 4
