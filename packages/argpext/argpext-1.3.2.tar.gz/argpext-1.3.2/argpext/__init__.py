#!/usr/bin/env python

"""

Argpext: Hierarchical argument processing based on argparse.

Copyright (c) 2012,2014,2015 by Alexander V. Shirokov. This material
may be distributed only subject to the terms and conditions
set forth in the Open Publication License, v1.0 or later
(the latest version is presently available at
http://www.opencontent.org/openpub ).


"""

import sys
import time
import re
import os
import warnings
import inspect
import collections
import functools
import inspect
import shlex

VERSION = (1,3,2)

from . import argparse

from . import tools
from argpext.tools import ChDir

from . import keywords
from argpext.keywords import KeyWords

from . import debug
from argpext.debug import FrameRef,chainref,DebugPrint

from . import prints

from . import cllu
from argpext.cllu import Stream,customize,s2m,Task,Node,Main


__all__ = [

    # Global variable
    'VERSION',

    # tools
    'ChDir',

    # keywords
    'KeyWords',

    # debug
    'FrameRef','chainref','DebugPrint',

    # tasks
    'Stream','customize','s2m','Task','Node','Main',

    ]

from . import rst


class Main(Node):
    SUBS = [('cllu', cllu.Main),
            ('rst', rst.Main)
            ]

