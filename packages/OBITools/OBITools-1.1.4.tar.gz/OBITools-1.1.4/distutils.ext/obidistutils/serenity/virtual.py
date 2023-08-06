'''
Created on 2 oct. 2014

@author: coissac
'''

import imp
import importlib
import os
import sys

from distutils.errors import DistutilsError
from distutils.version import StrictVersion  
from distutils import log       

from obidistutils.serenity.globals import PIP_MINVERSION, \
                                          local_virtualenv  # @UnusedImport

from obidistutils.serenity.checkpip import get_a_pip_module

from obidistutils.serenity.checkpackage import get_package_requirement
from obidistutils.serenity.checkpackage import parse_package_requirement
from obidistutils.serenity.checkpackage import is_installed
from obidistutils.serenity.checkpackage import pip_install_package

from obidistutils.serenity.checkpython import is_a_virtualenv_python
from obidistutils.serenity.checkpython import which_virtualenv
from obidistutils.serenity.checkpython import is_good_python27

from obidistutils.serenity.util import get_serenity_dir


def get_a_virtualenv_module(pip=None):
    
    global local_virtualenv

    if not local_virtualenv:
        if pip is None:
            pip = get_a_pip_module()
         
        
        virtualenv_req = get_package_requirement('virtualenv',pip)
        if virtualenv_req is None:
            virtualenv_req='virtualenv'
        
        requirement_project,requirement_relation,minversion = parse_package_requirement(virtualenv_req)  # @UnusedVariable
        
        if virtualenv_req is None or not is_installed(virtualenv_req, pip):
            tmpdir = get_serenity_dir()
            
            ok = pip_install_package(virtualenv_req,directory=tmpdir,pip=pip)
            
            log.debug('temp install dir : %s' % tmpdir)
                
            if ok!=0:
                raise DistutilsError, "I cannot install a virtualenv package"
    
            f, filename, description = imp.find_module('virtualenv', [tmpdir])
            
            vitualenvmodule = imp.load_module('virtualenv', f, filename, description)
            
            if minversion is not None:
                assert StrictVersion(vitualenvmodule.__version__) >= minversion, \
                       "Unable to find suitable version of pip get %s instead of %s" % (vitualenvmodule.__version__,
                                                                                        minversion)
    
        else:
            vitualenvmodule = importlib.import_module('virtualenv') 
            
        local_virtualenv.append(vitualenvmodule)
           
    return local_virtualenv[0]

        

    
    
def serenity_virtualenv(envname,package,version,minversion=PIP_MINVERSION,pip=None):
    
    
    #
    # Checks if we are already running under the good virtualenv
    #
    if is_a_virtualenv_python():
        ve = which_virtualenv(full=True)
        if ve == os.path.realpath(envname) and is_good_python27():
            return sys.executable
        
    #
    # We are not in the good virtualenv
    #
    
    if pip is None:
        pip = get_a_pip_module(minversion)
     
    #
    # Check if the virtualenv exist
    # 
        
    python = None
    
    if os.path.isdir(envname):
        python = os.path.join(envname,'bin','python')
        ok = (is_good_python27(python) and 
              is_a_virtualenv_python(python))
        
        #
        # The virtualenv already exist but it is not ok
        #
        if not ok:
            raise DistutilsError, "A virtualenv %s already exists but not with the required python"
                 
    else:
        ok = False
        
        
    #
    # Creates a new virtualenv
    #
    if not ok:
        virtualenv = get_a_virtualenv_module(pip)
        
        if virtualenv is not None:
            virtualenv.create_environment(envname)
        
            # check the newly created virtualenv
            return serenity_virtualenv(envname,package,version,minversion,pip)
    
    return os.path.realpath(python)
    
    
    