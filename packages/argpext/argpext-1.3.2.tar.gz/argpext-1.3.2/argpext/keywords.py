"""

Argpext: Hierarchical argument processing based on argparse.

Copyright (c) 2012,2014 by Alexander V. Shirokov. This material
may be distributed only subject to the terms and conditions
set forth in the Open Publication License, v1.0 or later
(the latest version is presently available at
http://www.opencontent.org/openpub ).


"""

import argpext
from argpext import *


class KeyWords(object):
    "List of unique, ordered keywords"

    def __iadd__(self,keywords):
        for key in keywords:
            if not isinstance(key,str): raise TypeError()
            if key in self._dct: raise ValueError("repeating keyword: '%s'" % key)
            self._dct[key] = True # This value is always true

    def __init__(self,keywords=[]):
        self._dct = collections.OrderedDict()
        self += keywords

    def __len__(self):
        return len(self._dct)

    def __iter__(self):
        return self._dct.keys().__iter__()

    def __contains__(self,key):
        return self._dct.__contains__(key)

    def __call__(self,key):
        "Keyword lookup"
        if key in self._dct: return key
        else: raise KeyError('invalid key: "%s"' % key)

    def verify(self,keys):
        for key in keys:
            if key not in self: 
                raise KeyError("unrecognized key: '%s'" % key)


    def __str__(self):
        f = argpext.debug.FrameRef(up=1)
        brief = (f['basename'] == 'argparse.py' and f['name'] == '_expand_help')
        if not brief:
            q = list([ ("'%s'" % k) for k in self._dct.keys() ])
            q = '%s([%s])' % ( type(self).__name__, ','.join(q) )
        else:
            q = list([ ("'%s'" % k) for k in self._dct.keys() ])
            if len(q) > 2:
                q[-1] = 'and '+q[-1]
            q = ', '.join(q)

        return q

