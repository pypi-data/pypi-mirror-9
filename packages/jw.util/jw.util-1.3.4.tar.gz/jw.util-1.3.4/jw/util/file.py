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
File operations
"""
import os

class Backup(object):
    """
    File backup

    Organizes file 'backup' by renaming it and it's old backups recursively.
    """

    def __init__(self, filename, mode=True):
        """
        Create Backup object

        :param mode: backup mode (see table)
        :type mode: various

        Renames a file according to ``mode``. Previous renamed versions are recursively renamed as well. The filename
        suffixes and the number of generations are set as follows:

        +---------------+-----------+---------------+
        | mode          | suffix    | generations   |
        +===============+===========+===============+
        | False         |           | 0             |
        +---------------+-----------+---------------+
        | True          | ~         | 1             |
        +---------------+-----------+---------------+
        | str           | str       | 1             |
        +---------------+-----------+---------------+
        | int           | .i        | n             |
        +---------------+-----------+---------------+
        | (str, int)    | str       | n             |
        +---------------+-----------+---------------+

        A generations specifier of -1 means unlimited. Integer-based generations are generated as a dot plus the integer (eg.
        filename.1, filename.2 etc). String-based generations are generated as multiple concatenations of the string (eg.
        filename~, filename~~ etc).
        """
        self.filename = filename
        # noinspection PySimplifyBooleanCheck
        if mode in (False, None):
            self.generations = 0
            self.string = '?'
            self.suffix = self._stringSuffix
        elif mode is True:
            self.generations = 1
            self.string = '~'
            self.suffix = self._stringSuffix
        elif isinstance(mode, int):
            self.generations = mode
            self.suffix = self._intSuffix
        elif isinstance(mode, (str, unicode)):
            self.generations = 1
            self.suffix = self._stringSuffix
            self.string = mode
        elif isinstance(mode, (tuple, list)) and isinstance(mode[0], (str, unicode)) and isinstance(mode[1], int):
            self.generations = mode[1]
            self.suffix = self._stringSuffix
            self.string = mode[0]

    def _stringSuffix(self, level):
        return level * self.string

    def _intSuffix(self, level):
        return '.%d' % level if level else ''

    def __call__(self):
        """
        Perform backup
        """
        self._run(0)

    def _run(self, level):
        """
        Backup level

        :param level:
        :type level: int
        """
        if self.generations == -1 or level < self.generations:
            oldName = self.filename + self.suffix(level)
            if os.path.exists(oldName):
                newName = self.filename + self.suffix(level + 1)
                if os.path.exists(newName):
                    self._run(level + 1)
                os.rename(oldName, newName)