# Copyright 2014 Johnny Wezel
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
Test file operations
"""
import glob
import os
import tempfile
import uuid
import unittest

from jw.util import file

def tmpfile():
    """
    """
    return tempfile.mktemp(uuid.uuid4().hex)

class TestBackup(unittest.TestCase):

    def setUp(self):
        self.filename = tmpfile()

    def tearDown(self):
        for f in glob.glob(self.filename + '*'):
            os.remove(f)

    def test001(self):
        """
        Test Backup(False)
        """
        open(self.filename, 'w')
        assert len(glob.glob(self.filename + '*')) == 1
        file.Backup(self.filename, False)()
        self.assertEqual(glob.glob(self.filename + '*'), [self.filename])

    def test002(self):
        """
        Test Backup(True)
        """
        open(self.filename, 'w')
        assert len(glob.glob(self.filename + '*')) == 1
        file.Backup(self.filename, True)()
        g = glob.glob(self.filename + '*')
        self.assertEqual(g, [self.filename + '~'])

    def test003(self):
        """
        Test Backup("!")
        """
        open(self.filename, 'w')
        assert len(glob.glob(self.filename + '*')) == 1
        file.Backup(self.filename, '!')()
        g = glob.glob(self.filename + '*')
        self.assertEqual(g, [self.filename + '!'])
        open(self.filename, 'w')
        file.Backup(self.filename, '!')()
        g = glob.glob(self.filename + '*')
        self.assertEqual(g, [self.filename + '!'])

    def test004(self):
        """
        Test Backup(1)
        """
        open(self.filename, 'w')
        assert len(glob.glob(self.filename + '*')) == 1
        file.Backup(self.filename, 1)()
        g = glob.glob(self.filename + '*')
        self.assertEqual(g, [self.filename + '.1'])

    def test005(self):
        """
        Test Backup(2)
        """
        open(self.filename, 'w')
        assert len(glob.glob(self.filename + '*')) == 1
        file.Backup(self.filename, 2)()
        g = glob.glob(self.filename + '*')
        self.assertEqual(g, [self.filename + '.1'])
        open(self.filename, 'w')
        file.Backup(self.filename, 2)()
        g = sorted(glob.glob(self.filename + '*'))
        self.assertEqual(g, [self.filename + '.1', self.filename + '.2'])
        open(self.filename, 'w')
        file.Backup(self.filename, 2)()
        g = sorted(glob.glob(self.filename + '*'))
        self.assertEqual(g, [self.filename + '.1', self.filename + '.2']) # No op, limit reached

    def test006(self):
        """
        Test Backup("!", 2)
        """
        open(self.filename, 'w')
        assert len(glob.glob(self.filename + '*')) == 1
        file.Backup(self.filename, ('!', 2))()
        g = glob.glob(self.filename + '*')
        self.assertEqual(g, [self.filename + '!'])
        open(self.filename, 'w')
        file.Backup(self.filename, ('!', 2))()
        g = sorted(glob.glob(self.filename + '*'))
        self.assertEqual(g, [self.filename + '!', self.filename + '!!'])
        open(self.filename, 'w')
        file.Backup(self.filename, ('!', 2))()
        g = sorted(glob.glob(self.filename + '*'))
        self.assertEqual(g, [self.filename + '!', self.filename + '!!']) # No op, limit reached
