# -*- coding: utf-8 -*-
"""
:Module: ````
:Author: `Adrian Letchford <http://www.dradrian.com>`_
:Organisation: `Warwick Business School <http://www.wbs.ac.uk/>`_, `University of Warwick <http://www.warwick.ac.uk/>`_.
:Created On: Sun Mar 22 18:42:12 2015
"""

# Import build in modules
import tarfile
from StringIO import StringIO
import hashlib
from os.path import isfile

# Import external modules
import cPickle as pickle

# Import custom modules

def string2name(string):
    """Converts a string to be written to the cache in a cache name."""
    name = hashlib.md5(string).hexdigest()
    return name
    

def function2name(function, *args, **kwargs):
    """
    Converts a function to a unique name. The idea is that each unique function 
    with unique parameters will produce a different string.
    
    This function simply packs the function identifier and parameters into a
    dictionary and then converts it to a string with pickle. This string is
    then converted to an MD5 checksum.
    """ 
    function_id = function.func_code.co_code
    dic = {'function':function_id, 'args':args, 'kwargs':kwargs}
    string = pickle.dumps(dic)
    return string2name(string)

class Cache(object):
    
    def __init__(self, filename):

        # Set read and writing modes
        self.rmode = 'r'
        self.amode = 'a'
        
        # set the file extension
        self.extension = '.tar'
        
        self.filename = filename + self.extension
        
    def _check_is_cache(self):
        if not isfile(self.filename): 
            raise IOError("No cache has been created! Try saving some data.")
            
    def save(self, name, obj):
        """Adds data to the cache."""
        
        data = pickle.dumps(obj)
        buf = StringIO(data)
        
        info = tarfile.TarInfo(name=name)
        info.size=len(buf.buf)
        
        archive = tarfile.open(self.filename, self.amode)
        archive.addfile(tarinfo=info, fileobj=buf)
        archive.close()
        
    def load(self, name):
        """Gets data from the cache."""

        self._check_is_cache()
        
        archive = tarfile.open(self.filename, self.rmode)
        data = archive.extractfile(name).read()
        archive.close()
        
        obj = pickle.loads(data)
        
        return obj
        
    def list_names(self):
        
        self._check_is_cache()
        
        archive = tarfile.open(self.filename, self.rmode)
        data_names = archive.getmembers()
        archive.close()
        
        return [t.name for t in data_names]
        
        
    def is_cached(self, name):
        """Returns true if there is cached data under the given name."""
        
        try:
            self._check_is_cache()
        except:
            return False
        
        return name in self.list_names()
        
        
    def run(self, function, *args, **kwargs):
        """Wraps a function call with caching."""
    
        name = function2name(function, *args, **kwargs)
        
        if self.is_cached(name):
            return self.load(name)
        
        data = function(*args, **kwargs)
        self.save(name, data)
        
        return data
    