#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
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

"""A few checks at the MNIST database.
"""

import unittest
import bob.db.mnist

def test_query():
  db = bob.db.mnist.Database()

  f = db.labels()
  assert len(f) == 10 # number of labels (digits 0 to 9)
  for i in range(0,10):
    assert i in f

  f = db.groups()
  assert len(f) == 2 # Two groups
  assert 'train' in f
  assert 'test' in f

  # Test the number of samples/labels
  d, l = db.data(groups='train')
  assert d.shape[0] == 60000
  assert d.shape[1] == 784
  assert l.shape[0] == 60000
  d, l = db.data(groups='test')
  assert d.shape[0] == 10000
  assert d.shape[1] == 784
  assert l.shape[0] == 10000
  d, l = db.data()
  assert d.shape[0] == 70000
  assert d.shape[1] == 784
  assert l.shape[0] == 70000


def test_download():
  # tests that the files are downloaded *and stored*, when the directory is specified
  import tempfile, os, shutil
  temp_dir = tempfile.mkdtemp(prefix='mnist_db_test_')
  db = bob.db.mnist.Database(temp_dir)
  del db
  assert os.path.exists(temp_dir)

  # check that the database works when data is downloaded already
  db = bob.db.mnist.Database(temp_dir)
  assert db.data() is not None
  del db

  shutil.rmtree(temp_dir)
