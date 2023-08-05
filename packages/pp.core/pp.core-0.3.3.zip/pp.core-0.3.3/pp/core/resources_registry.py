
################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################
""" 
Resources registry for templates, styles etc.
"""

import os
from fs.osfs import OSFS
from pp.core.logger import  LOG
from pp.core.resource import Resource

# mapping name -> directory
_resources_registry = dict()

def registerResource(name, directory):
    if not os.path.exists(directory):
        raise IOError('Directory "{0:2}" does not exit'.format(directory))
    if name in _resources_registry:
        raise KeyError('A resource "{0:2}" is already registered'.format(name))
    _resources_registry[name] = Resource(OSFS(directory))
    LOG.info('Registered resource directory "{0:2}" as "{0:2}"'.format(directory, name))

def getResource(resource):
    return _resources_registry[resource]

def getResourceNames():
    return _resources_registry.keys()

