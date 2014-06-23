'''
Created on 23-Jun-2014

@author: rjoyce
'''

class Service(object):
    """Encapsulates a Space Service"""

    def __init__(self, rest_end_point):
        self._rest_end_point = rest_end_point
        self._collections = {}
        self._methods = {}

    def __getattr__(self, attr):
        if attr in self._collections:
            return self._collections[attr]
        elif attr in self._methods:
            return self._methods[attr]
        else:
            raise AttributeError

