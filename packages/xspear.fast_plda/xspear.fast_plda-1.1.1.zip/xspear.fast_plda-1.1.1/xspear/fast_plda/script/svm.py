#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Sun 15 Apr 14:01:39 2012 
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
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


import argparse
import sys
import bob
import numpy
import os

def read_data(training_files, input_dir, input_ext='.hdf5'):
  data = []
  for client_files in training_files:
    # at least two files per client are required!
    data.append(numpy.vstack([bob.io.load(feature.make_path(input_dir, input_ext)).flatten() for feature in client_files]))

  # Returns the list of lists of arrays
  return data


def ensure_dir(d):
  if not os.path.exists(d):
    os.makedirs(d)

def svm(args, command_line_parameters):
  """SVM training and scoring"""

  input_dir = args.features_directory
  output_dir = args.output_directory
  protocol_dir = args.protocol_directory

  # Create database
  import xbob.db.verification.filelist
  input_ext = '.hdf5'
  db = xbob.db.verification.filelist.Database(protocol_dir)
 
  # Get training files
  training_list = db.objects(groups='world')
  training_list_male = [k for k in training_list if k.client_id == 'real']
  training_list_female = [k for k in training_list if k.client_id == 'synthetic']
  training_data = read_data([training_list_male, training_list_female], input_dir, input_ext)
  # Call training process
  print("Training SVM...")
  print("  %d classes" % len(training_data))
  print("  %d samples in class 0" % len(training_data[0]))
  print("  %d samples in class 1" % len(training_data[1]))
  t = bob.trainer.SVMTrainer(kernel_type=bob.machine.svm_kernel_type.LINEAR)
  print("  cost = %f" % float(args.cost))
  t.cost = float(args.cost)
  if args.use_rbf == True: 
    print("  using RBF kernel")
    t.kernel_type = bob.machine.svm_kernel_type.RBF
    print("  gamma = %f" % float(args.gamma))
    t.gamma = float(args.gamma)
  machine = t.train(training_data)
  print("Saving SVM...")
  ensure_dir(output_dir)
  machine.save(bob.io.HDF5File(os.path.join(output_dir, 'svm.hdf5'), 'w'))
  #machine = bob.machine.SupportVector(bob.io.HDF5File(os.path.join(output_dir, 'svm.hdf5')))

  for group in ['dev', 'eval']:
    # Get the list of training files
    print("Scoring and saving scores for group %s..." % group)
    probe_list = db.objects(groups=group, purposes='probe')
    filename = os.path.join(output_dir, 'scores-%s' %group)
    f = open(filename, 'w')
    for p in probe_list:
      probe = bob.io.load(p.make_path(input_dir, input_ext)).flatten()
      cl, score = machine.predict_class_and_scores(probe)
      if p.client_id == 'real':
        f.write('%s %s %s %f\n' % ('real', p.client_id, p.path, score))
        f.write('%s %s %s %f\n' % ('converted_imp', p.client_id, p.path, -score))
      else:
        f.write('%s %s %s %f\n' % ('real', p.client_id, p.path, score))
        f.write('%s %s %s %f\n' % ('converted_imp', p.client_id, p.path, -score))
    f.close()


def parse_args(command_line_parameters):
  """This function parses the given options (which by default are the command line options)."""
  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--features-directory', metavar = 'DIR', required = True,
      help = 'Directory where the input features are stored.')
  parser.add_argument('--protocol-directory', metavar = 'DIR', required = True,
      help = 'Directory where the protocol is stored.')
  parser.add_argument('--output-directory', metavar = 'DIR', required = True,
      help = 'Output directory, where the models and scores should be stored')
  parser.add_argument('--use-rbf', action='store_true', default=False, help='Use SVM with Gaussian RBF kernel')
  parser.add_argument('--gamma', default=0.0025,  help='Gamma value for the Gaussian RBF kernel parameter of the SVM')
  parser.add_argument('--cost', default=1.,  help='Cost of the SVM')

  return parser.parse_args(command_line_parameters) 


def main(command_line_parameters = sys.argv):
  """Main routine"""
  # do the command line parsing
  args = parse_args(command_line_parameters[1:])

  # perform SVM-based gender verification test
  svm(args, command_line_parameters)

if __name__ == "__main__":
  main()

