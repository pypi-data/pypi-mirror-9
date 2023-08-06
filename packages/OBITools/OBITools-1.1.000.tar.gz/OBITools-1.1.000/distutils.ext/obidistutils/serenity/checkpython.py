'''
Created on 2 oct. 2014

@author: coissac
'''

import subprocess
import sys
import os
import glob

from distutils.version import StrictVersion
from distutils import sysconfig

from obidistutils.serenity.checksystem import is_mac_system, \
                                              is_windows_system
                        


def is_python27(path=None):
    '''
    Checks that the python is a python2.7 
    
        @param path: if None consider the running python
                     otherwise the python pointed by the path
                     
        @return: True if the python is a 2.7
        @rtype: bool
    '''
    if path is None:
        pythonversion = StrictVersion(sysconfig.get_python_version())
    else:
        command = """'%s' -c 'from distutils import sysconfig; """ \
                  """print sysconfig.get_python_version()'""" % path
                  
        p = subprocess.Popen(command, 
                             shell=True, 
                             stdout=subprocess.PIPE)
        pythonversion = StrictVersion(p.communicate()[0])
                
    return     pythonversion >=StrictVersion("2.7") \
           and pythonversion < StrictVersion("2.8") 
           
           
           
def is_mac_system_python(path=None):
    '''
    Checks on a mac platform if the python is the original 
    python provided with the systems
    .
    
        @param path: if None consider the running python
                     otherwise the python pointed by the path
                     
        @return: True if the python is the system one
        @rtype: bool
    '''
    if path is None:
        path = sys.executable
    
    p1 = '/System/Library/Frameworks/Python.framework'
    p2 = '/usr/bin'
    
    return path[0:len(p1)]==p1 or \
           path[0:len(p2)]==p2
 

def is_a_virtualenv_python(path=None):
    '''
    Check if the python is belonging a virtualenv
    
        @param path: the path pointing to the python executable.
                     if path is None then the running python is
                     considered.
        @param path: str or None 
                     
        @return: True if the python belongs a virtualenv
                 False otherwise
        @rtype: bool
                 
    '''
    if path is None:
        rep = hasattr(sys, 'real_prefix')
    else:
        command = """'%s' -c 'import sys; print hasattr(sys,"real_prefix")'""" % path
        p = subprocess.Popen(command, 
                             shell=True, 
                             stdout=subprocess.PIPE)
        rep = eval(p.communicate()[0])
        
    return rep


def which_virtualenv(path=None,full=False):
    '''
    Returns the name of the virtualenv.
        @param path: the path to a python binary or None
                     if you want to consider the running python
        @type path: str or None
                     
        @param full: if set to True, returns the absolute path,
                     otherwise only return a simple directory name
        @type full: bool
                 
        @return: the virtual environment name or None if the
                 path does not belong a virtualenv
        @rtype: str or None
    '''
    if path is None:
        path = sys.executable
    
    if is_a_virtualenv_python(path):
        parts = path.split(os.sep)
        try:
            if full:
                rep = os.sep.join(parts[0:parts.index('bin')])
                rep = os.path.realpath(rep)
            else:
                rep = parts[parts.index('bin')-1]
        except ValueError:
            rep = None
    else:
        rep=None
        
    return rep

def is_good_python27(path = None):    
    '''
    Checks if the python is usable for the package install.
    
    Actually the python must be a 2.7 version and not being the
    default python included with the system on a mac.
    
        @param path: the path to a python binary or None
                     if you want to consider the running python
        @type path: str or None

        @return: True if the python is ok
                 False otherwise
        @rtype: bool
                 
    '''
    rep = is_python27(path) and \
          (not is_mac_system() or \
           not is_mac_system_python(path) \
          )
    
    return rep
    
def lookfor_good_python27():
    exe = []
    if not is_windows_system():
        paths = os.environ['PATH'].split(os.pathsep)
        for p in paths:
            candidates = glob.glob(os.path.join(p,'python2.7')) + \
                         glob.glob(os.path.join(p,'python2')) + \
                         glob.glob(os.path.join(p,'python'))
            pexe = []
            for e in candidates:
                if os.path.islink(e):
                    e = os.path.realpath(e)
                if os.path.isfile(e) and \
                   os.access(e, os.X_OK) and \
                   is_good_python27(e) and \
                   not is_a_virtualenv_python(e):
                    pexe.append(e)
            exe.extend(set(pexe))
        
    return exe

