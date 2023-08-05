'''
Created on 20 oct. 2012

@author: coissac
'''

import os

from obidistutils.command.build_exe import build_exe
from obidistutils.serenity.checksystem import is_mac_system


class pidname(build_exe):
    
    description = "build the pidname executable returning the executable path from a PID on a mac"


    def initialize_options(self):
        build_exe.initialize_options(self)

        self.pidname = False


    def finalize_options(self):
        # This might be confusing: both build-cexe and build-temp default
        # to build-temp as defined by the "build" command.  This is because
        # I think that C libraries are really just temporary build
        # by-products, at least from the point of view of building Python
        # extensions -- but I want to keep my options open.
        
        build_exe.finalize_options(self)
        
        self.set_undefined_options('build',
                                   ('build_scripts', 'build_cexe'))

        # self.ctools = self.distribution.ctools
        
        if os.path.isfile("distutils.ext/src/pidname.c"):
            self.executables = [('pidname',{"sources":["distutils.ext/src/pidname.c"]})]
            self.check_executable_list(self.executables)
        else:
            self.executables = []


    def run(self):
        if is_mac_system():
            build_exe.run(self)
            self.pidname=True
        else:
            self.pidname=False
        