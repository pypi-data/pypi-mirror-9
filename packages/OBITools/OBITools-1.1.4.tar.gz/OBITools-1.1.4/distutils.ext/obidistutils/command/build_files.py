'''
Created on 20 oct. 2012

@author: coissac
'''

import os.path

from distutils.core import Command
from distutils.util import convert_path
from distutils import log, sysconfig
from distutils.dep_util import newer
from distutils import log



class build_files(Command):
            
    def initialize_options(self):
        self.files=None
        self.ctools=None
        self.build_temp=None
        self.build_cexe=None

    def finalize_options(self):
        
        self.set_undefined_options('build_ctools',
                                   ('ctools',  'ctools'),
                                   ('build_temp','build_temp'),
                                   ('build_cexe','build_cexe'),
                                   )
        
        self.files = {}
        
    def run(self):
        
        for dest,prog,command in self.distribution.files:
            destfile = os.path.join(self.build_temp,dest)
            if prog in self.ctools:
                progfile = os.path.join(self.build_cexe,prog)
            else:
                progfile = prog 
                
            log.info("Building file : %s" % dest)
            
            commandline = command % {'prog' : progfile,
                                     'dest' : destfile}

            log.info("    --> %s" % commandline)
            
            os.system(commandline)
            self.files[dest]=destfile
            
            log.info("Done.\n")
            
            
            
        
