'''
Created on 2 oct. 2014

@author: coissac
'''

import sys
import os

from distutils import log
from distutils.errors import DistutilsError


from obidistutils.serenity.globals import saved_args
from obidistutils.serenity.checkpython import is_good_python27, \
                                              lookfor_good_python27


def rerun_with_anothe_python(path):
        
    if saved_args:
        args = saved_args
    else:
        args = list(sys.argv)
        
          
    assert is_good_python27(path), \
           'the selected python is not adapted to the installation of this package'
                   
    args.insert(0, path)
        
    sys.stderr.flush()
    sys.stdout.flush()
    

    os.execv(path,list(args))

def enforce_good_python():
    if is_good_python27():
        return True
    
    goodpython = lookfor_good_python27()
    
    if not goodpython:
        raise DistutilsError,'No good python identified on your system'

    goodpython=goodpython[0]
    
    log.warn("========================================")    
    log.warn("")
    log.warn("    Switching to python : %s" % goodpython)
    log.warn("")
    log.warn("========================================")    

    rerun_with_anothe_python(goodpython)
