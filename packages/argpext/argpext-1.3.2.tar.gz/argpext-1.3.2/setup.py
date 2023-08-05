

from distutils.core import setup

setup(
    name='argpext'
    , version='1.3.2' # Fix the version number at conf.py, and argparse/__init__.py too
    , description = 'Argpext: multilevel command line interface.'
    , author='Alexander Shirokov'
    , author_email='alexander.shirokov@gmail.com'
    , packages=['argpext']
    #, scripts = ['argpext.py']
    , py_modules=['argpext']
    , license='OSI Approved'
    , long_description="""Argpext provides methods to quickly expose any required callable
objects, such as function, or generator, to a 
DOS/Linux command line hereby defining a task.

Argpext provides method to organize multiple tasks conveniently into a tree structure.

Each task of such tree can then be executed by passing the proper sequence
of command line arguments that is necessary to identify the task to
be executed; the remaining arguments, if any, specify the values of the arguments
argument passed to the task (if any). 

Help messages, which are mostly based on the docstrings, are
automatically produced when the --help (or -h) flag is passed.

The return values of the functions and the values yielded by the
generators are treated differently.  Full-featured return value
objects are available at the point of execution in
Python. Customizable return value display option is available for
execution under Linux/DOS command prompt.

A thorough documentation (with numerous examples) is provided at the link above.

"""
    , classifiers = [
        'Development Status :: 5 - Production/Stable'
        ,'Environment :: Console'
        ,'Intended Audience :: Developers'
        ,'Intended Audience :: Information Technology'
        ,'Intended Audience :: Science/Research'
        ,'Intended Audience :: End Users/Desktop'
        ,'Operating System :: MacOS :: MacOS X'
        ,'Operating System :: Microsoft :: Windows'
        ,'Operating System :: POSIX'
        ,'Programming Language :: Python :: 2'
        ,'Programming Language :: Python :: 3'

        ,'Topic :: Software Development :: User Interfaces'
        ,'Topic :: Software Development :: Interpreters'        
        ,'Topic :: Utilities'
    ]
)

