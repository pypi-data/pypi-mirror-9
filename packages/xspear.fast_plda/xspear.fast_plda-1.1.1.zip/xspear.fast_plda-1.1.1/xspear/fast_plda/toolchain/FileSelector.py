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
from spear.toolchain import FileSelector as FileSelectorBase

class FileSelector(FileSelectorBase):
  """This class includes functionalities for an I-Vector tool chain to produce verification scores"""
 
  def training_feature_list_by_clients_new(self, dir_type, step):
    """Returns the list of training features, which is split up by the client ids."""
    # get the type of directory that is required
    cur_dir = self.select_dir(dir_type)
    # if requested, define the subset of training data to be used for this step
    if step == 'train_plda_enroler':
      groups = ['world']
      if 'optional_world_1' in self.m_db.groups():
        groups.append('optional_world_1')
      cur_world_options = self.__options__('world_enroler_options')
    
    all_training_filenames = []
    for group in groups:  
        # iterate over all training clients
        features_by_clients_options = {}
        if 'subworld' in cur_world_options: features_by_clients_options['subworld'] = cur_world_options['subworld']
        features_by_clients_options.update(self.__options__('features_by_clients_options'))
        train_clients = self.m_db.clients(groups=group, protocol=self.m_config.protocol, **features_by_clients_options)
        training_filenames = {}
        for m in train_clients:
          # collect training features for current client id
          files = self.sort(self.m_db.objects(protocol=self.m_config.protocol, groups=group, model_ids=(m.id,), **cur_world_options))
          known = set()
          directory=cur_dir
          extension=self.m_config.default_extension
          train_data_m = [file.make_path(directory, extension) for file in files if file.path not in known and not known.add(file.path)]

          # add this model to the list
          training_filenames[m] = train_data_m
        # return the list of features which is grouped by client id
        all_training_filenames.append(training_filenames)
    return all_training_filenames

