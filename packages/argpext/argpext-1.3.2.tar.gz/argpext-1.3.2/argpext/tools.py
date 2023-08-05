"""

Argpext: Hierarchical argument processing based on argparse.

Copyright (c) 2012,2014,2015 by Alexander V. Shirokov. This material
may be distributed only subject to the terms and conditions
set forth in the Open Publication License, v1.0 or later
(the latest version is presently available at
http://www.opencontent.org/openpub ).


"""


import argpext
from argpext import *

class ChDir(object):
    def __init__(self,path):
        self.initdir = os.getcwd()
        if not os.path.exists(path): os.makedirs(path)
        os.chdir(path)
        self.targetdir = os.getcwd()

    def __enter__(self):
        return self
    def __exit__(self,exc_type,exc_value,traceback):
        os.chdir(self.initdir)
        return False

    def __del__(self):
        try:
            os.chdir(self.initdir)
        except TypeError:
            pass
        except AttributeError:
            pass


