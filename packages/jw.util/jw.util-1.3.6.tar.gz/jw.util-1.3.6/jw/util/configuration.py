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
This module contains the Configuration class.
"""

from . import file
import yaml

class Dict(dict):
    """
    This custom dict class emulates an object. Configuration attributes can be access with member access, eg. `config.key`
    instead of just item access (`config['key']`).
    """
    def __getattr__(self, name):
        """
        Object attribute

        :param name:
        :type name: str
        :return: config attribute
        :rtype: object
        """
        return self[name]

    def __setattr__(self, name, value):
        """
        Set object attribute

        :param name:
        :type name: str
        :param value:
        :type value: object
        """
        self[name] = value

def construct_yaml_map(self, node):
    """
    Construct a Dict object instead of a dict.
    """
    data = Dict()
    yield data
    value = self.construct_mapping(node)
    data.update(value)

yaml.Loader.add_constructor(u'tag:yaml.org,2002:map', construct_yaml_map)

class Configuration(Dict):
    """
    Configuration
    """

    # def __init__(self):
    #     """
    #     Create a Configuration object
    #
    #     Use the from... functions to create Configuration objects and load a data into it.
    #     """

    # def __getitem__(self, item):
    #     """
    #     Get configuration item
    #
    #     :param item: config item name
    #     :type item: str
    #
    #     Gets a configuration item on a single level. This can be used to manually navigate the configuration tree.
    #     """
    #     if isinstance(self.config, dict):
    #         return self.config[item]
    #     else:
    #         raise KeyError(item)

    def get(self, item, default=None):
        """
        Get configuration item

        :param item: config item name
        :type item: str
        :param default:
        :type default:

        Gets a configuration item on a single level. This can be used to manually navigate the configuration tree.
        """
        if isinstance(self, dict):
            return self.get(item)
        else:
            return None

    # def __setitem__(self, key, value):
    #     """
    #     Set configuration item
    #
    #     :param key:
    #     :param value:
    #
    #     Sets a configuration item on a single level.
    #     """
    #     if not isinstance(self.config, dict):
    #         self.config = {key: value}
    #     else:
    #         self.config[key] = value

    # def __delitem__(self, item):
    #     """
    #     Delete configuration item
    #
    #     :param item: config item name
    #     :type item: str
    #     """
    #     del self.config[item]

    def delete(self, *path):
        """
        Delete configuration item

        :param path: path to item
        :type path: items ...
        """
        if len(path) == 1:
            del self[path[0]]
        else:
            item = self(*path[:-1])
            del item[path[-1]]

    def __call__(self, *path, **kw):
        """
        Get configuration item

        :param path: path to configuration item
        :type path: iterable
        :param kw: keyword arguments, currently only ``default``
        :type kw: dict
        :return: configuration item

        If the configuration item is not found, the value of the ``default`` keyword argument (or None if not present) is taken
        """
        result = self
        for element in path:
            if element in result:
                result = result[element]
            else:
                return kw.get('default')
        return result

    def at(self, path, default=None, separator='.'):
        """
        Get configuration item by path string

        :param path: path string, like ``path.to.config.item``
        :type path: str
        :param default: default value (in case item is not found)
        :param separator: separator to split path (default: '.')
        :type separator: str
        :return: configuration item
        """
        return self(*path.split(separator), default=default)

def FromString(yamlString):
    """
    Load configuration from string

    :param yamlString: YAML definition of model
    :type yamlString: str
    :rtype: Configuration
    """
    c = Configuration(yaml.load(yamlString))
    return c

def FromStream(yamlStream):
    """
    Load configuration from stream

    :param yamlStream: stream with YAML definition of model
    :type yamlStream: stream
    :rtype: Configuration
    """
    # This is the same code as FromString() since yaml.load() can take a str or a file
    c = Configuration(yaml.load(yamlStream))
    return c

def FromFile(yamlFilename):
    """
    Load configuration from named file

    :param yamlFilename: path to file with YAML definition of model
    :type yamlFilename: str
    :rtype: Configuration
    """
    c = Configuration(yaml.load(open(yamlFilename)))
    return c

def ToFile(config, yamlFilename, backup=True):
    """
    Save configuration in file

    :param config:
    :param yamlFilename: path to file
    :type yamlFilename: str
    :param backup: Whether to back up the old file
    :type backup: bool or int
    """
    file.Backup(yamlFilename, backup)()
    with open(yamlFilename, 'w') as stream:
        yaml.dump(config, stream, default_flow_style=False, indent=4)