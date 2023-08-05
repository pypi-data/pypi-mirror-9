"""

Argpext: Hierarchical argument processing based on argparse.

Copyright (c) 2012,2015 by Alexander V. Shirokov. This material
may be distributed only subject to the terms and conditions
set forth in the Open Publication License, v1.0 or later
(the latest version is presently available at
http://www.opencontent.org/openpub ).


"""


import shlex
import stat
import shutil
import os
import io
import sys
import subprocess
import code
import xml, xml.dom.minidom

import argpext
from argpext.prints import *


XMLTAGS = argpext.KeyWords(['input'])

INPUTATTR = argpext.KeyWords(['action','content','linenos','read','directory','flags'])

CONTENT = argpext.KeyWords(['python','shell'])
ACTIONS = argpext.KeyWords(['show','execute','test-execute'])
FLAGS = argpext.KeyWords(['show_filename'])


class Debug(object):
    KEYS = argpext.KeyWords(['p','k','t'])
    def __init__(self,key=None):
        K = set([Debug.KEYS(k) for k in key]) if key is not None else set()
        self.show_position = 'p' in K
        self.enable_test = 't' in K


class Immerse(object):
    def __init__(self,directory):
        self.initdir = os.getcwd()
        self.directory = os.path.abspath(directory)
        self.PATH_INI = os.environ['PATH']
        self.PYTHONPATH_INI = os.environ.get('PYTHONPATH')

    def __enter__(self):
        extra_paths = [os.getcwd()]
        os.chdir(self.directory)
        extra_paths += [os.getcwd()]
        os.environ['PATH'] = os.path.pathsep.join(extra_paths+[self.PATH_INI])
        os.environ['PYTHONPATH'] = os.path.pathsep.join(extra_paths+([] if self.PYTHONPATH_INI is None else [self.PYTHONPATH_INI]))


    def __exit__(self,exc_type,exc_value,tp):
        # Restore paths
        os.environ['PATH'] = self.PATH_INI
        if self.PYTHONPATH_INI is not None:
            os.environ['PYTHONPATH'] = self.PYTHONPATH_INI
        else:
            del os.environ['PYTHONPATH']
        os.chdir(self.initdir)
        return False



class __NoDefault: pass

def get_nodeattr(node,key,default=__NoDefault()):
    if isinstance(default,__NoDefault):
        q = node.attributes.get(key)
        if q is None: raise ValueError('mandatory key value missing for %s' % key)
        return getattr(q,'value')
    else:
        return getattr(node.attributes.get(key),'value', default)


class Reconnect(object):
    def __init__(self,stdout,stderr):
        self._so = sys.stdout
        self._se = sys.stderr
        sys.stdout = stdout
        sys.stderr = stderr

    def __enter__(self): pass

    def __exit__(self,exc_type, exc_value, traceback):
        sys.stdout = self._so
        sys.stderr = self._se
        return True # Suppresses the exception


def filter_out_tr(q):
    "Filter out the traceback messages"
    L = []
    if len(q):
        q = q.splitlines()
        for q in q:
            if q.startswith('Traceback '): continue
            if q.startswith(' '): continue
            L += [q]
    q = os.linesep.join(L)
    return q



def process_show(text,node):

    text = text.lstrip()

    flags = set(filter(None,get_nodeattr(node,INPUTATTR('flags'),'').split(',')))
    content = CONTENT(get_nodeattr(node,INPUTATTR('content')))

    if 'show_filename' in flags:
        comment = {'python' : '#','shell' : '::'}[content]+' File "%s"' % get_nodeattr(node,INPUTATTR('read'))
        text = '\n'.join([comment,"",text ])


    return dict(ierr=0,output=text)

def process_shell(text,node):

    text = text.lstrip()

    output_all = []
    for command in text.splitlines():

        def prn(line,file):
            file.write(line)
            file.write(os.linesep)

        # When passing with shell=True, you do not need to split the command into list.
        proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True )
        proc.wait()
        #ierr = proc.returncode

        L = []

        # Deal with stdout
        so = ''
        q = proc.stdout.read().decode()
        if len(q):
            q = q.splitlines()
            for i,q in enumerate(q):
                q = q.replace('usage: ./','usage: ')
                so += ('' if i == 0 else os.linesep)+q

        # Deal with stderr
        se = ''
        q = proc.stderr.read().decode()
        q = filter_out_tr(q)
        for line in q.splitlines():
            se += (line+os.linesep)

        outputs = so+se

        output = '~$ '+command+('\n'+outputs if len(outputs) else '') 

        output_all += [output]


    return dict(output='\n'.join(output_all))


class TextStream():
    def __init__(self):
        self.s = ''
    def write(self,s):
        self.s = self.s+s
    def __str__(self):
        return self.s


def process_python(text,node):

    def consinit():
        cons = code.InteractiveConsole()

        start = [
            "__name__ = '__main__'"
            ,"import sys"
            ,"sys.argv = ['excode.py']"
            ,'del sys'
        ]
        for q in start:
            cons.push(q)
        return cons


    class Console:
        def __init__(self):
            self.cons = consinit()
            self.status = 0
            self.R = []
            self.i = 0

        def push(self,line):
            #for line in text.rstrip('\n').splitlines()+['\n']:
            #line = line.rstrip()
            sys.stdout.write('line: %s\n' % line)

            stdout = TextStream()
            stderr = TextStream()

            with Reconnect(stdout=stdout,stderr=stderr):
                self.i += 1
                sys.__stdout__.write('pushing %d {%s}|size:%d\n' % ( self.i, line,len(line)) )
                try:
                    self.status_next = self.cons.push(line)
                except:
                    sys.stdout.write('[Python console is terminated at this point]\n')
                    self.cons = consinit()

            so_raw = str(stdout)
            se_raw = str(stderr)

            prompt = '... ' if self.status else '>>> '

            prm = '%s%s' % ( prompt, line )+os.linesep

            def pnl(q):
                if len(q): q += os.linesep
                return q

            so = so_raw
            se = pnl(filter_out_tr(se_raw))

            output = '{prompt}{line}{nl}{so}{se}'.format(
                prompt=prompt
                ,line=line
                ,nl=os.linesep

                ,so=so
                #,so='+'
                ,se=se
                #,se='*'
                )

            sys.__stdout__.write('output: {%s}\n\n' % output)
            self.R += [output]
            self.status = self.status_next
            return self.status

    text = text.lstrip()

    C = Console()
    status = False
    for line in text.splitlines():
        status = C.push( line )

    # Complete unfinished statements
    i = 0
    while 1:
        if status: break
        status = C.push("")
        i += 1
        if i == 2: break
    C.push("")


    return dict(output=''.join(C.R))


def parse_node(node,debug):
    content = CONTENT(get_nodeattr(node,INPUTATTR('content')))
    action = ACTIONS(get_nodeattr(node,INPUTATTR('action')))
    directory = get_nodeattr(node,INPUTATTR('directory'))


    def gettext():
        if len(node.childNodes):
            assert( len(node.childNodes) == 1 )
            text = node.childNodes[0].data.lstrip()
        else:
            with open(os.path.join(directory,get_nodeattr(node,INPUTATTR('read')))) as fhi:
                text = fhi.read()
        return text

    text = gettext()


    with Immerse(directory):

        if action == "show":
            q = process_show(text,node=node)
        elif action in set(["execute","test-execute"]):
            if action == "test-execute" and not debug.enable_test:
                q = {'output' : '',
                     'skip' : True
                }
            else:
                q = {'shell' :  process_shell, 
                     'python' : process_python}
                q = q[content](text,node=node)
        else:
            raise KeyError()

        text = q['output']

        return q



def xmlgen(inputfile,outputfile,debug):

    inputfile = os.path.abspath(inputfile)
    outputfile = os.path.abspath(outputfile)

    def process(iline,text,prior_ident):
        sys.stdout.write('processing....\n')
        try:
            dom = xml.dom.minidom.parseString(text)
        except:
            sys.stderr.write(text+'\n')
            raise ValueError('XML not well-formed, see above')

        node = dom.childNodes[0]
        content = CONTENT(get_nodeattr(node,INPUTATTR('content')))
        linenos = {"false" : False, "true" : True}[get_nodeattr(node,INPUTATTR('linenos'),default="false")]

        q = parse_node(node,debug)
        text = q['output']
        skip = q.get('skip',False)


        def f(text):
            T = []
            current_ident = prior_ident+' '*2
            # Start the block
            T += [prior_ident+('.. code-block:: {content}'.format(content=content))]
            if linenos:
                T += [current_ident+':linenos:']
            T += [current_ident]
            for line in text.splitlines():
                T += [current_ident+line]
            if debug.show_position:
                T += [current_ident]
                T += [current_ident+'# File %s, line %d' % (os.path.basename(inputfile), iline)]
            #T += [prior_ident+'..']
            T += [prior_ident]
            T = '\n'.join(T)
            return T

        text = f(text)
        if skip: text = ''

        #pri(text,exit=2)

        return text



    def simple_parse():
        chunk = []


        with open(outputfile,'w') as fho:

            write = (lambda x: fho.write(str(x)+'\n'))

            for iline,line in enumerate(open(inputfile),1):
                line = line.rstrip('\r\n')


                dump = None
                textline = None

                if len(chunk) == 0:
                    q = line.find('<%s' % XMLTAGS('input'))
                    if q != -1:
                        prior_ident = ' '*q
                        pri(q)
                        pri('BI[%s]' % prior_ident)
                        chunk += [line]
                        if line.endswith('/>') :
                            dump = chunk
                            chunk = []
                    else:
                        textline = line
                else:
                    chunk += [line]
                    if line.startswith('</%s>' % XMLTAGS('input') ):
                        dump = chunk
                        chunk = []

                sys.stdout.write('[%d %s]\n' % ( iline, line) )

                if dump is not None:
                    pri('[%s]' % prior_ident)
                    q = process(iline,'\n'.join(dump),prior_ident)
                    write( q )
                    del prior_ident

                if textline is not None:
                    write(line)

    simple_parse()


    




class Main(argpext.Task):

    hook = argpext.s2m(xmlgen)

    def populate(self,parser):
        parser.add_argument(dest='inputfile',default='doc.rst',
                            help='Input .rst file. The default is "%(default)s"')
        parser.add_argument(dest='outputfile',default='index.rst', 
                            help='Output file. The default value is "%(default)s".')
        parser.add_argument('-d',dest='debug',type=Debug,default=Debug(),help="Debug mode")





