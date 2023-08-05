#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Thu Dec  6 12:28:25 CET 2012
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
import bob.io.base

class File(object):
  """Abstract base class that defines basic properties of File objects"""

  def __init__(self, client_id, path, file_id = None):
    """**Constructor Documentation**

    Initialize the File object with the minimum required data.

    Parameters:

    client_id : various type
      The id of the client, this file belongs to.
      The type of it is dependent on your implementation.
      If you use an SQL database, this should be an SQL type like Integer or String.

    path : str
      The path of this file, relative to the basic directory.
      If you use an SQL database, this should be the SQL type String.
      Please do not specify any file extensions.

    file_id : various type
      The id of the file.
      The type of it is dependent on your implementation.
      If you use an SQL database, this should be an SQL type like Integer or String.
      If you are using an automatically determined file id, you can skip selecting the file id.
    """

    # just copy the information
    self.client_id = client_id
    """The id of the client that belongs to this file."""
    self.path = path
    """The relative path including the file name, but excluding the file name extension"""
    # set file id only, when specified
    if file_id:
      self.id = file_id
      """A unique identifier of the file."""
    else:
      # check that the file id at least exists
      if not hasattr(self, 'id'):
        raise NotImplementedException("Please either specify the file id as parameter, or create an 'id' member variable in the derived class that is automatically determined (e.g. by SQLite)")

  def __lt__(self, other):
    """This function defines the order on the File objects. File objects are always ordered by their ID, in ascending order."""
    return self.id < other.id


  def __repr__(self):
    """This function describes how to convert a File object into a string.
    Overwrite it if you want more/other details of the File to be written."""
    return "<File('%s': '%s' -- '%s')>" % (str(self.id), str(self.client_id), str(self.path))


  def make_path(self, directory = None, extension = None):
    """Wraps the current path so that a complete path is formed

    Keyword parameters:

    directory : str or None
      An optional directory name that will be prefixed to the returned result.

    extension : str or None
      An optional extension that will be suffixed to the returned filename.
      The extension normally includes the leading ``.`` character as in ``.jpg`` or ``.hdf5``.

    Returns a string containing the newly generated file path.
    """
    # assure that directory and extension are actually strings
    if not directory: directory = ''
    if not extension: extension = ''
    # create the path
    return str(os.path.join(directory, self.path + extension))


  def save(self, data, directory = None, extension = '.hdf5', create_directories=True):
    """Saves the input data at the specified location and using the given extension.

    Keyword parameters:

    data : various types
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory : str or None
      If not empty or None, this directory is prefixed to the final file destination

    extension : str or None
      The extension of the filename.
      This extension will control the type of output and the codec for saving the input blob.

    create_directories : bool
      Should the directory structure be created (if necessary) before writing the data?
    """
    # get the path
    path = self.make_path(directory, extension)
    # use the bob API to save the data
    bob.io.base.save(data, path, create_directories=create_directories)


