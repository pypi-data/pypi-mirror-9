'''
Created on 20 oct. 2012

@author: coissac
'''

import os


from obidistutils.command.build_exe import build_exe
from distutils.sysconfig import customize_compiler
from distutils.errors import DistutilsSetupError
from distutils import log

class build_ctools(build_exe):
    description = "build C/C++ executable not distributed with Python extensions"

    def initialize_options(self):
        build_exe.initialize_options(self)
        
        # List of built tools
        self.ctools = None
        self.littlebigman = None


    def finalize_options(self):
        # This might be confusing: both build-cexe and build-temp default
        # to build-temp as defined by the "build" command.  This is because
        # I think that C libraries are really just temporary build
        # by-products, at least from the point of view of building Python
        # extensions -- but I want to keep my options open.
            
        build_exe.finalize_options(self)
        
        
        self.set_undefined_options('build',
                                    ('build_temp', 'build_cexe'))

        self.set_undefined_options('littlebigman',
                                   ('littlebigman',  'littlebigman'))
                   
        self.executables = self.distribution.ctools
        self.check_executable_list(self.executables)
        
        if self.littlebigman =='-DLITTLE_END':
            if self.define is None:
                self.define=[('LITTLE_END',None)]
            else:
                self.define.append('LITTLE_END',None)

        self.ctools = set()

    def run(self):
        
        build_exe.run(self)
        for e,p in self.executables:
            self.ctools.add(e)
            


