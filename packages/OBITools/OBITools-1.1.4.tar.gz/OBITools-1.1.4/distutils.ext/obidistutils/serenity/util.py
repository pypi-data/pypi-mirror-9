'''
Created on 2 oct. 2014

@author: coissac
'''

import sys 
import tempfile


from obidistutils.serenity.globals import tmpdir         # @UnusedImport
from obidistutils.serenity.globals import saved_args     # @UnusedImport

def get_serenity_dir():
    global tmpdir

    if not tmpdir:
        tmpdir.append(tempfile.mkdtemp())
    return tmpdir[0]
        
def save_argv():
    global saved_args

    del saved_args[:]
    saved_args.extend(list(sys.argv))

           
