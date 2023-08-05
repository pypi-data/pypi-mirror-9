#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Wed Nov 13 12:46:06 CET 2013
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

import os, shutil
import unittest
import bob.io.base
import bob.io.base.test_utils
import bob.db.verification.utils
import tempfile

regenerate_database = False

from sqlalchemy import Column, Integer, String
dbfile = bob.io.base.test_utils.datafile("test_db.sql3", "bob.db.verification.utils")

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class TestFile (Base, bob.db.verification.utils.File):
  __tablename__ = "file"
  id = Column(Integer, primary_key=True)
  client_id = Column(Integer, unique=True)
  path = Column(String(100), unique=True)
  def __init__(self):
    bob.db.verification.utils.File.__init__(self, client_id=5, path="test/path")

def create_database():
  if os.path.exists(dbfile):
    os.remove(dbfile)
  import bob.db.base.utils
  engine = bob.db.base.utils.create_engine_try_nolock('sqlite', dbfile, echo=True)
  Base.metadata.create_all(engine)
  session = bob.db.base.utils.session('sqlite', dbfile, echo=True)
  session.add(TestFile())
  session.commit()
  session.close()
  del session
  del engine


class TestDatabase (bob.db.verification.utils.ZTDatabase, bob.db.verification.utils.SQLiteDatabase):
  def __init__(self):
    bob.db.verification.utils.ZTDatabase.__init__(self)
    bob.db.verification.utils.SQLiteDatabase.__init__(self, dbfile, TestFile, original_directory = "original/directory", original_extension = ".orig")

  def groups(self, protocol=None):
    return ['group']
  def model_ids(self, groups=None, protocol=None):
    return [5]
  def objects(self, groups=None, protocol=None, purposes=None, model_ids=None):
    return list(self.query(TestFile))
  def tmodel_ids(self, groups=None, protocol=None):
    return self.model_ids()
  def tobjects(self, groups=None, protocol=None, model_ids=None):
    return self.objects()
  def zobjects(self, groups=None, protocol=None):
    return self.objects()
  def annotations(self, file):
    assert isinstance(file, TestFile)
    return {'key' : (42, 180)}



def test01_annotations():
  # tests the annotation IO functionality provided by this utility class

  # check the different annotation types
  for annotation_type in ('eyecenter', 'named', 'idiap'):
    # get the annotation file name
    annotation_file = bob.io.base.test_utils.datafile("%s.pos" % annotation_type, 'bob.db.verification.utils')
    # read the annotations
    annotations = bob.db.verification.utils.read_annotation_file(annotation_file, annotation_type)
    # check
    assert 'leye' in annotations
    assert 'reye' in annotations
    assert annotations['leye'] == (20,40)
    assert annotations['reye'] == (20,10)

def test02_database():
  # check that the database API works
  if regenerate_database:
    create_database()

  db = TestDatabase()

  def check_file(fs):
    assert len(fs) == 1
    f = fs[0]
    assert isinstance(f, TestFile)
    assert f.id == 1
    assert f.client_id == 5
    assert f.path == "test/path"

  check_file(db.objects())
  check_file(db.tobjects())
  check_file(db.zobjects())
  check_file(db.all_files())
  check_file(db.training_files())
  check_file(db.test_files())
  check_file(db.enroll_files())
  check_file(db.probe_files())
  check_file(db.t_enroll_files(None,5))
  check_file(db.z_probe_files(None,5))
  check_file(db.files([1]))
  check_file(db.reverse(["test/path"]))

  model_ids = db.model_ids()
  assert len(model_ids) == 1
  assert model_ids[0] == 5
  tmodel_ids = db.tmodel_ids()
  assert len(tmodel_ids) == 1
  assert tmodel_ids[0] == 5

  file = db.objects()[0]
  assert db.original_file_name(file, check_existence=False) == "original/directory/test/path.orig"
  assert db.file_names([file], "another/directory", ".other")[0] == "another/directory/test/path.other"
  assert db.paths([1], "another/directory", ".other")[0] == "another/directory/test/path.other"

  annots = db.annotations(file)
  assert len(annots) == 1
  assert 'key' in annots.keys()
  assert (42, 180) in annots.values()

  # try file save
  temp_dir = tempfile.mkdtemp(prefix="bob_db_test_")
  data = [1., 2., 3.]
  file.save(data, temp_dir)
  assert os.path.exists(file.make_path(temp_dir, ".hdf5"))
  read_data = bob.io.base.load(file.make_path(temp_dir, ".hdf5"))
  for i in range(3):
    assert data[i] == read_data[i]
  shutil.rmtree(temp_dir)

