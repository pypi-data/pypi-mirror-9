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
from argpext.prints import *



class Stream(object):
    KEYS = KeyWords(['stdout','null'])
    def __init__(self,name):
        self._name = self.KEYS(name)
    def write(self,r):
        if self._name == 'stdout':
            sys.stdout.write( str(r) )
        elif self._name == 'null':
            pass
        else:
            raise KeyError()



class Doc(object):
    def __init__(self,value):
        self.value = value
    def __call__(self,short=False,label=None):
        "Doc string presentation"
        if self.value is None: return
        R = self.value
        if short is True:
            R = re.split('[\.;]',R)[0]

        debug = False
        if debug:
            R += '[%(position)s%(label)s]' % \
                 { 'position' : '%(basename)s:%(line)s' % FrameRef(up=1)
                   ,'label' : ('(%s)' % label  if label is not None else '') 
                 }

        return R



class BaseNode(object):

    def __init__(self,upper={}):
        self._upper = upper

    def upper(self):
        return self._upper

    def _history_update(self,prog,args):
        "Update the history log file, if the latter is defined."
        filename = histfile()

        if not len(args): return

        if filename is not None:

            # Generate the logline
            def get_logline():
                timestr = time.strftime('%Y%m%d-%H:%M:%S', time.localtime())
                path = os.getcwd()
                cmd = ' '.join([prog]+args)
                logline = ','.join([ timestr, path, cmd ])+'\n'
                return logline

            def updatelog(filename,logline):
                MAX_LINESIZE = 1024
                MAX_FILESIZE = 1024*1024
                RETAIN_FILESIZE = MAX_FILESIZE/2

                def truncated_line(line,dots,size):
                    if len(line) > size:
                        dots = dots[0:size]
                        line = line[0:size]
                        line = line[0:(len(line)-len(dots))]+dots
                    return line

                def truncate_file(filename,max_filesize,retain_filesize):
                    if not ( 0 <= retain_filesize <= max_filesize ): raise ValueError()
                    initsize = os.stat(filename).st_size
                    cmlsize = 0
                    remove_trigger = ( initsize-max_filesize > 0)
                    retain_lines = []
                    if remove_trigger:
                        minimum_remove_size = initsize-retain_filesize
                        with open(filename) as fh:
                            for line in fh:
                                cmlsize += len(line)
                                if cmlsize >= minimum_remove_size:
                                    retain_lines += [line]
                            with open(filename,'w') as fh:
                                for line in retain_loines:
                                    fh.write( line )

            LINESEP = '\n'
            logline = get_logline()
            with open(filename,'a') as fh: fh.write( logline )
            updatelog(filename, logline)

    def tdigest(self,args=None,prog=None,stream=None,display=True,unfold=True):
        if prog is None: prog = os.path.basename( sys.argv[0] )
        if args is None: args = sys.argv[1:]
        if stream is None: stream=Stream('stdout')
        return self.idigest(prog=prog,args=args,stream=stream,unfold=unfold,display=display)

    def sdigest(self,args=[],prog=None,stream=None,display=False,unfold=False):
        if prog is None: prog = '%s.%s().sdigest(...) <-' % ( inspect.getmodule(self).__name__, type(self).__name__ )
        if stream is None: stream = Stream('stdout')
        return self.idigest(prog=prog,args=args,stream=stream,unfold=unfold,display=display)



def s2m(func):
    @functools.wraps(func)
    def wrapper(*args,**kwds):
        self = args[0]
        args = args[1:]
        return func(*args,**kwds)
    return wrapper


def customize(tostring=None):
    "Hook customization."
    assert(tostring is None or hasattr(tostring,'__call__'))

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            self = args[0]
            args = args[1:]
            assert(isinstance(self,BaseNode))
            #if inspect.ismethod(func):
            # The above does not work; using a workaround:
            r = func(self,*args,**kwargs)

            self._tostring = tostring
            return r
        return wrapper

    return decorator


def execution(basenode,stream,args,kwds,unfold,end,display):
    assert(isinstance(display,bool))

    elements = basenode.hook(*args,**kwds)

    tostring = getattr(basenode,'_tostring',None)
    display &= tostring is not None

    def output(x):
        if display:
            stream.write( tostring(x) )
            stream.write( end )

    def interwine():
        # When elements is a generator, unfold it optionally,
        # and interpserse with outputs.
        if inspect.isgenerator(elements):
            if unfold:
                L = []
                for el in elements:
                    output(el)
                    L += [el]
                return L
            else:
                @functools.wraps(interwine)
                def wrapper():
                    for el in elements:
                        output(el)
                        yield el
                return wrapper()
        else:
            output(elements)
            return elements

    return interwine()


# Task

class Task(BaseNode):
    """Base class for command line interface to a Python function."""

    def __init__(self,upper={}):
        BaseNode.__init__(self,upper=upper)

    # Members to be overloaded by the user
    def hook(self):
        """This method should be overloaded by user. """
        raise NotImplementedError()

    def populate(self,parser):
        """This method should be overloaded by user. """
        pass

    def _docstring(self):
        q = self.__doc__
        # Infer a callable instance based on hook
        if q is None: 
            q = getattr(type(self),'hook')
            if sys.version_info[0:2] <= (2, 7,): q = q.__func__
            q = q.__doc__
        q = Doc( q )
        return q

    def idigest(self,prog,args,stream,unfold,display):
        "Execute Task, based on command line arguments."

        if isinstance(args,str): args = shlex.split(args)
        assert(isinstance(args,(list,tuple)))


        try:

            # Assign the default values of arguments.

            # Update the history
            BaseNode._history_update(self,prog=prog,args=args)
        
            # Find: docstring
            docstr = self._docstring()

            # Find keyword args to pass to function, based on command line arguments.
            def get_kwds(args):
                q = argparse.ArgumentParser(prog=prog,  description=docstr(label='description') )
                self.populate( q )
                K = vars(argparse.ArgumentParser.parse_args(q,args))
                return K

            kwds = get_kwds(args)

            "Any Task class object."
            return execution( basenode=self, stream=stream, args=(), kwds=kwds, unfold=unfold, end='\n', display=display )

        except argparse.ParserExit:
            pass

        except:
            raise


_EXTRA_KWD = '_ARGPEXT_EXTRA_KWD'


class Node(BaseNode):
    "Command line interface for a node."

    def __init__(self,upper={}):
        BaseNode.__init__(self,upper=upper)

    SUBS = []

    def populate(self,parser):
        """This method should be overloaded by user. """
        pass


    def _get_deleg(self,prog,unfold):

        Y = None

        parser = argparse.ArgumentParser( prog=prog, description=Doc(self.__doc__)(label='description')  )
        nodes = {}
        for name,subtask in getattr(self,'SUBS',[]):

            if name in nodes: raise ValueError('repeated key %s' % name)

            if Y is None: Y = parser.add_subparsers(help='Description')

            if inspect.isfunction(subtask):
                # Find: subtask, the class of the task.
                subtask = type('_'+subtask.__name__.capitalize(), 
                               (Task,) , 
                               {'hook' : customize()( s2m(subtask) )
                            })

            nodes[name] = subtask

            if issubclass(subtask,Task):

                X = subtask(upper=self._upper)

                docstr = X._docstring()

                S = Y.add_parser(name,help=docstr(label='help',short=True),description=docstr(label='description') )
                X.populate( S )


                S.set_defaults( ** { _EXTRA_KWD : X } )

            elif issubclass(subtask,Node):

                X = subtask(upper=self._upper)
                X._disable_history = True

                docstr = Doc(getattr(subtask,'__doc__',None))

                S = Y.add_parser(name,help=docstr(label='help',short=True),description=docstr(label='description') )
                S.set_defaults( ** { _EXTRA_KWD : X } )

            else:
                raise TypeError('invalid type (%s) for sub-command "%s" of %s' % ( subtask.__name__, name, type(self).__name__ ) )

        return dict(parser=parser,nodes=nodes)


    def _parserdict(self,prog,args,kwds,unfold):
        deleg = self._get_deleg(prog=prog,unfold=unfold)
        self.populate( deleg['parser'] )
        namespace = argparse.ArgumentParser.parse_args( deleg['parser'], args )

        def type_info():
            T = {}
            for a in deleg['parser']._actions:
                if isinstance(a,argparse._StoreAction):
                    if a.type is not None:
                        T[a.dest] = a.type
            return T

        T = type_info()

        D = vars(namespace)
        # Overwrite values defined by parser with explicitly given keyword arguments.

        for key,val in kwds.items():
            if key not in D: raise ValueError("dest='%s' is not defined by parser" % key)
            D[key] = T.get(key,str)(val)

        return D

    def idigest(self,prog,args,stream,unfold,display):
        "Execute Node, based on command line arguments."

        if isinstance(args,str): args = shlex.split(args)
        assert(isinstance(args,(list,tuple)))

        try:

            if not hasattr(self,'_disable_history'):
                BaseNode._history_update(self,prog=prog,args=args)

            # Split arguments into two parts: shallow, and deep.
            def argsplit(args,keys):
                L = []
                R = []
                ptr = L
                for i,arg in enumerate(args):
                    if len(R) or arg in keys:
                        ptr = R
                    ptr += [arg]
                return L,R

            deleg = self._get_deleg(prog=prog,unfold=unfold)

            shallowargs,rightargs = argsplit(args=args,keys=deleg['nodes'].keys())

            # Update tree-wide namespace
            self._upper.update( self._parserdict(prog=prog,args=shallowargs,kwds={},unfold=unfold) )

            if len(rightargs):

                ctrkey = rightargs[0]

                def delegate():
                    delegargs = rightargs[1:]
                    node = deleg['nodes'][ ctrkey ]
                    parser = deleg['parser']

                    if inspect.isfunction(node) or inspect.isgenerator(node):
                        raise NotImplementedError()
                    elif issubclass(node,Task):
                        x = argparse.ArgumentParser.parse_args( parser, [ctrkey]+delegargs )
                        f = getattr(x,_EXTRA_KWD)
                        return f.idigest(prog='%s %s' % (prog,ctrkey), args=delegargs, stream=stream, unfold=unfold, display=display )
                    elif issubclass(node,Node):
                        q = argparse.ArgumentParser.parse_args( parser, [ctrkey] )
                        # Chaining
                        return getattr(q,_EXTRA_KWD).idigest( prog='%s %s' % (prog,ctrkey), args=delegargs, stream=stream, unfold=unfold, display=display )
                    else:
                        raise TypeError

                return delegate()

        except argparse.ParserExit:
            pass
        except:
            raise




def histfile():
    "Returns file path of the hierarchical subcommand history file"
    q = 'ARGPEXT_HISTORY'
    q = os.getenv(q)
    return q



class Main(Task):
    "Show command line history."

    def hook(self,unique):
        q = histfile()
        if not os.path.exists(q): 
            sys.stderr.write(('History file ("%s") not found' % q)+os.linesep)
        else:
            lastcommand = None
            with open(q) as fhi:
                for line in fhi:
                    date,path,command = line.split(',',2)
                    if unique and lastcommand is not None and command == lastcommand: continue
                    sys.stdout.write(line.rstrip()+os.linesep)
                    lastcommand = command

    def populate(self,parser):
        parser.add_argument('-u',dest='unique',default=False,action='store_true',
                            help='Do not show repeating commands')




