import sys

from distutils import util
from distutils import sysconfig
from distutils import log
from distutils.version import LooseVersion, StrictVersion
import glob
import os
import subprocess
import re 
from distutils.errors import DistutilsError
import urllib2
import tempfile

import importlib
import imp
import zipimport

import argparse

import base64

from checkpython import is_mac_system_python, \
                        is_python27, \
                        is_a_virtualenv_python, \
                        which_virtualenv, \
                        is_good_python27
                        
                        
from obidistutils.serenity.rerun import  enforce_good_python
from obidistutils.serenity.rerun import rerun_with_anothe_python

from obidistutils.serenity.virtual import serenity_virtualenv
                        
from obidistutils.serenity.checksystem import is_mac_system, \
                                              is_windows_system
                        
from obidistutils.serenity.checkpackage import install_requirements
from obidistutils.serenity.checkpackage import check_requirements

from obidistutils.serenity.util import save_argv
                        
from obidistutils.serenity.snake import snake

from obidistutils.serenity.globals import PIP_MINVERSION
                            
    
def serenity_snake(envname,package,version,minversion=PIP_MINVERSION):
    old = log.set_threshold(log.INFO)

    log.info("Installing %s (%s) in serenity mode" % (package,version))

    print >>sys.stderr,snake
    sys.stderr.flush()

    enforce_good_python()

    virtualpython=serenity_virtualenv(envname,package,version,minversion=minversion)
    
    if virtualpython!=os.path.realpath(sys.executable):
        log.info("Restarting installation within the %s virtualenv" % (envname))
        rerun_with_anothe_python(virtualpython)
        
    log.info("%s will be installed with python : %s" % (package,virtualpython))
        
    install_requirements()
    
    log.set_threshold(old)
    
def serenity_assert(version,minversion=PIP_MINVERSION):
    check_requirements()



def serenity_mode(package,version):
    
    save_argv()

    
    from obidistutils.serenity.globals import saved_args
    

    old = log.set_threshold(log.INFO)
    
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument('--serenity',
                           dest='serenity', 
                           action='store_true',
                           default=False, 
                           help='Switch the installer in serenity mode. Everythings are installed in a virtualenv')

    argparser.add_argument('--virtualenv',
                           dest='virtual', 
                           type=str,
                           action='store',
                           default="%s-%s" % (package,version), 
                           help='Specify the name of the virtualenv used by the serenity mode [default: %s-%s]' % (package,version))    
    
    args, unknown = argparser.parse_known_args()
    sys.argv = [sys.argv[0]] + unknown
    
    if args.serenity:
        serenity_snake(args.virtual,package,version)
    else:
        pass
        # serenity_assert(package,version)
        
    
    log.set_threshold(old)
    
    return args.serenity
    
    
