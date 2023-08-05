#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Wed Nov 13 11:56:53 CET 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import bob.core
import logging
logger = logging.getLogger("bob")

_idiap_annotations = {
  1 : 'reyeo',
  2 : 'reyet',
  3 : 'reyep',
  4 : 'reyeb',
  5 : 'reyei',
  6 : 'leyei',
  7 : 'leyet',
  8 : 'leyep',
  9 : 'leyeb',
  10: 'leyeo',
  11: 'rbrowo',
  12: 'rbrowi',
  13: 'lbrowi',
  14: 'lbrowo',
  15: 'noser',
  16: 'noset',
  17: 'nosel',
  18: 'mouthr',
  19: 'moutht',
  20: 'mouthb',
  21: 'mouthl',
  22: 'chin'
}


def read_annotation_file(file_name, annotation_type):
  """This function provides default functionality to read annotation files.
  It returns a dictionary with the keypoint name as key and the position (y,x) as value, and maybe some additional annotations.

  Keyword Parameters:

  file_name : str
    The full path of the annotation file to read

  annotation_type : str
    The type of the annotation file that should be read.
    The following annotation_types are supported:

    * 'eyecenter': The file contains a single row with four entries: 're_x re_y le_x le_y'
    * 'named': The file contains named annotations, one per line, e.g.: 'reye re_x re_y'
    * 'idiap': The file contains enumerated annotations, one per line, e.g.: '1 key1_x key1_y', and maybe some additional annotations like gender, age, ...
  """

  if not file_name:
    return None

  if not os.path.exists(file_name):
    raise IOError("The annotation file '%s' was not found"%file_name)

  annotations = {}

  with open(file_name, 'r') as f:

    if str(annotation_type) == 'eyecenter':
      # only the eye positions are written, all are in the first row
      line = f.readline()
      positions = line.split()
      assert len(positions) == 4
      annotations['reye'] = (float(positions[1]),float(positions[0]))
      annotations['leye'] = (float(positions[3]),float(positions[2]))

    elif str(annotation_type) == 'named':
      # multiple lines, no header line, each line contains annotation and position
      for line in f:
        positions = line.split()
        assert len(positions) == 3
        annotations[positions[0]] = (float(positions[2]),float(positions[1]))

    elif str(annotation_type) == 'idiap':
      # Idiap format: multiple lines, no header, each line contains an integral keypoint identifier, or other identifier like 'gender', 'age',...
      for line in f:
        positions = line.rstrip().split()
        if positions:
          if positions[0].isdigit():
            # position field
            assert len(positions) == 3
            id = int(positions[0])
            annotations[_idiap_annotations[id]] = (float(positions[2]),float(positions[1]))
          else:
            # another field, we take the first entry as key and the rest as values
            annotations[positions[0]] = positions[1:]
      # finally, we add the eye center coordinates as the center between the eye corners; the annotations 3 and 8 are the pupils...
      if 'reyeo' in annotations and 'reyei' in annotations:
        annotations['reye'] = ((annotations['reyeo'][0] + annotations['reyei'][0])/2., (annotations['reyeo'][1] + annotations['reyei'][1])/2.)
      if 'leyeo' in annotations and 'leyei' in annotations:
        annotations['leye'] = ((annotations['leyeo'][0] + annotations['leyei'][0])/2., (annotations['leyeo'][1] + annotations['leyei'][1])/2.)

    else:
      raise ValueError("The given annotation type '%s' is not known, choose one of ('eyecenter', 'named', 'idiap')" % annotation_type)

  if 'leye' in annotations and 'reye' in annotations and annotations['leye'][1] < annotations['reye'][1]:
    logger.warn("The eye annotations in file '%s' might be exchanged!" % file_name)

  return annotations
