'''
Created on 2 oct. 2014

@author: coissac
'''

#import urllib2
import os
#import imp
#import base64
#import zipimport
import importlib

from distutils.version import StrictVersion
#from distutils.errors import DistutilsError
from distutils import log


from obidistutils.serenity.globals import PIP_MINVERSION, \
                                          local_pip                       # @UnusedImport
                    
                    
from obidistutils.serenity.util import get_serenity_dir
import sys
import pkgutil


def is_pip_installed(minversion=PIP_MINVERSION):
    try:
        log.info("Try to load pip module...")
        pipmodule = importlib.import_module('pip')
        if hasattr(pipmodule,'__version__'):
            ok = StrictVersion(pipmodule.__version__) >= StrictVersion(minversion)
            log.info("Pip installed version %s" % pipmodule.__version__)
        else:
            ok = False
            log.info("A too old version of pip is installed on your system")

        # We clean up the imported pip module for test purpose
        for m in [x for x in sys.modules if x.startswith('pip.')]:
            del sys.modules[m]

        del sys.modules['pip']
        

    except:
        ok = False
        log.info("No pip installed on your system")
        
    return ok

def get_a_pip_module(minversion=PIP_MINVERSION):
    
    global local_pip

    tmpdir = get_serenity_dir()
    
    if not local_pip:    
        serenity = importlib.import_module('obidistutils.serenity')
        sys.path.insert(0, os.path.dirname(serenity.__file__))
        pip = importlib.import_module('pip')

        local_pip.append(pip)
    else:
        pip = local_pip[-1]
    
    # Prepare the CERT certificat for https download
            
    cert_path = os.path.join(tmpdir, "cacert.pem")
        
    certificate = pkgutil.get_data("pip._vendor.requests", "cacert.pem")

    with open(cert_path, "wb") as cert:
        cert.write(certificate)
           
    os.environ.setdefault("PIP_CERT", cert_path)
          
    assert hasattr(pip,'__version__') and StrictVersion(pip.__version__) >= StrictVersion(minversion), \
               "Unable to find suitable version of pip"
       
    return local_pip[0]
            
