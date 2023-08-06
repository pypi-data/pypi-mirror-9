'''
Created on 20 oct. 2012

@author: coissac
'''

import os

from distutils.core import Command
from obidistutils.command.build_exe import build_exe
from distutils.sysconfig import customize_compiler
from distutils.errors import DistutilsSetupError
from distutils import log

import subprocess

class littlebigman(build_exe):
    
    description = "build the littlebigman executable testing endianness of the CPU"


    def initialize_options(self):
        build_exe.initialize_options(self)

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

        # self.ctools = self.distribution.ctools
        
        if os.path.isfile("distutils.ext/src/littlebigman.c"):
            self.executables = [('littlebigman',{"sources":["distutils.ext/src/littlebigman.c"]})]
            self.check_executable_list(self.executables)
        else:
            self.executables = []


    def run_littlebigman(self):
        p = subprocess.Popen("'%s'" % os.path.join(self.build_temp,
                                                   'littlebigman'), 
                             shell=True, 
                             stdout=subprocess.PIPE)
        little = p.communicate()[0]
        return little

    def run(self):
        build_exe.run(self)
        self.littlebigman=self.run_littlebigman()
        log.info("Your CPU is in mode : %s" % self.littlebigman)
        
        