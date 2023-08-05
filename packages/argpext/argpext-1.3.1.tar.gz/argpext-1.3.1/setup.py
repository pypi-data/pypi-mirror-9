

from distutils.core import setup

setup(
    name='argpext'
    , version='1.3.1' # Fix the version number at conf.py, and argparse/__init__.py too
    , description = 'Argpext: hierarchical extension of sub-commands in argparse.'
    , author='Alexander Shirokov'
    , author_email='alexander.shirokov@gmail.com'
    , packages=['argpext']
    #, scripts = ['argpext.py']
    , py_modules=['argpext']
    , license='OSI Approved'
    , long_description="""Argpext provides hierarchical, or multilevel, subcommand
implementation that allows one to quickly expose any required callable
objects, such as functions, generators, to a DOS/Linux command line.

Hierarchical sub-commands implementation: Class "Task" is used to
define the interface between a specific callable object and the
command line. When python module contains more than one "task", class
"Node" may be used in order to populate all the required "tasks" onto
a tree structure.  Any such task may then individually be executed from a UNIX/DOS
command line prompt, by passing a script name followed a sequence of command line arguments, followed by the command line arguments used to specify the arguments of the
task, if required.  Using the "--help" results in a help message. Passing the
sequence of arguments complete with the task arguments results in the
actual execution of the task.

Acknowledgements: Hierarchical subcommands feature internally relies on the argparse module.

Release v1.3.0 - substantial new features.  

Release v1.3.1 - Compatibility with Python 2 is established.

"""
    , classifiers = [
        'Development Status :: 4 - Beta'
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

