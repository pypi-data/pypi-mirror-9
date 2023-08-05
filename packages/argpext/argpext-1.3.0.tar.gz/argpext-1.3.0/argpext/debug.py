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

#> Position 
class FrameRef(object):
    KEYS = keywords.KeyWords(['line','path','name','basename','smart_basename'])

    def __init__(self,up=0):
        self.frame = sys._getframe(1+up)

    def keys(self):
        return self.KEYS

    def __getitem__(self,key):
        "returns frame reference string"
        if self.KEYS(key) == 'line':
            return self.frame.f_lineno
        elif key == 'path':
            return self.frame.f_code.co_filename
        elif key == 'name':
            q = self.frame.f_code.co_name
            return q
        elif key == 'basename':
            return os.path.basename(self['path'])
        elif key == 'smart_basename':
            basename = self['basename']
            q = self['path']
            q = os.path.dirname(q)
            q = os.path.basename(q)
            dirbasename = q
            return os.path.join( * (([dirbasename] if basename.lower() == '__init__.py' else [])+[basename]) )
        else:
            raise KeyError()


def chainref(fstr='{name}[{smart_basename}:{line}]',sep='|',up=0,limit=None):
    "Return chain reference."
    i = 0
    L = []
    while 1:
        try:
            f = fstr.format( **FrameRef(up=1+up+i) )
        except ValueError:
            break
        L += [f]
        i += 1
        if limit is not None and i == limit: break
    return sep.join(L)


def status(**kwds):

    up = kwds.pop('up',0)
    s = kwds.pop('s',None)
    e = kwds.pop('e',None)
    n = kwds.pop('n',None)
    if len(kwds): raise KeyError('unrecognized keys: %s' % ( ','.join(kwds.keys()) ) )

    # Update the count
    F = sys._getframe(1+up)
    line = F.f_lineno
    key = '__argpext_DebugPrint_%s' % line
    count = F.f_globals.setdefault(key,-1)
    count += 1
    F.f_globals[key] = count

    live = True
    # Process the restrictions
    if s is not None and count < s: live = False
    if e is not None and count >= e: live = False

    # Process the permissions
    if n is not None and count == n: live = True

    return dict(live=live,count=count)


class DebugPrint(object):

    def __init__(self,active=True,format_spec='{smart_basename}:{line} [{count}]: {string}'):

        # First thing off, check the highest priority argument.
        if not isinstance(active,(bool,int)): raise TypeError()
        self.active = active
        if not active: return

        self.format_spec = format_spec


    KEYS = keywords.KeyWords(['sep','end','file','flush',
                                      's','e','n','exit'])

    def __call__(self,*args,**kwds):

        # First thing off, check the highest priority argument.
        if not self.active: return

        A = status(up=1,**dict([(k,kwds.pop(k,None)) for k in ['s','e','n']]))
        if not A['live']: return


        # print arguments
        sep = kwds.pop('sep',' ')
        end = kwds.pop('end','\n')
        exit = kwds.pop('exit',None)
        file = kwds.pop('file',sys.stdout)
        flush = kwds.pop('flush',False)

        if len(kwds): raise KeyError('unrecognized keys: %s' % ( ','.join(kwds.keys()) ) )

        frm = {}
        frm.update( FrameRef(up=1) )
        frm['count'] = A['count']


        string = sep.join([str(q) for q in args])

        def manage_multiline(string):
            q = string.splitlines()
            if len(q) > 1:
                q = '\n'.join(['multiline...']+q)
                return q
            return string

        string = manage_multiline(string)

        q = frm
        q.update(dict(string=string))
        line = self.format_spec.format(**q)+end



        file.write(line)
        if flush: file.flush()

        if exit is not None and A['count'] >= exit:
            file.write('Exit: %s' % ('{smart_basename}:{line}'.format(**frm)) +'\n')
            sys.exit()
