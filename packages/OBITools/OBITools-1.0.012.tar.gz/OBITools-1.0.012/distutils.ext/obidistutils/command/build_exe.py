'''
Created on 20 oct. 2012

@author: coissac
'''

import os

from distutils.core import Command
from distutils.sysconfig import customize_compiler
from distutils.errors import DistutilsSetupError
from distutils import log
from distutils.ccompiler import show_compilers

import subprocess

class build_exe(Command):
    
    description = "build an executable -- Abstract command "

    user_options = [
        ('build-cexe', 'x',
         "directory to build C/C++ libraries to"),
        ('build-temp', 't',
         "directory to put temporary build by-products"),
        ('debug', 'g',
         "compile with debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ('compiler=', 'c',
         "specify the compiler type"),
        ]

    boolean_options = ['debug', 'force']

    help_options = [
        ('help-compiler', None,
         "list available compilers", show_compilers),
        ]

    def initialize_options(self):
        self.build_cexe = None
        self.build_temp = None

        # List of executables to build
        self.executables = None

        # Compilation options for all libraries
        self.include_dirs = None
        self.define = None
        self.undef = None
        self.extra_compile_args = None
        self.debug = None
        self.force = 0
        self.compiler = None
        self.sse = None
        self.built_files=None

    def finalize_options(self):
        # This might be confusing: both build-cexe and build-temp default
        # to build-temp as defined by the "build" command.  This is because
        # I think that C libraries are really just temporary build
        # by-products, at least from the point of view of building Python
        # extensions -- but I want to keep my options open.
        self.set_undefined_options('build',
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('force', 'force'))

        if self.include_dirs is None:
            self.include_dirs = self.distribution.include_dirs or []
            
        if isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        self.sse = self.distribution.sse
        
        if self.sse is not None:
            if self.extra_compile_args is None:
                self.extra_compile_args=['-m%s' % self.sse]
            else:
                self.extra_compile_args.append('-m%s' % self.sse)

        # XXX same as for build_ext -- what about 'self.define' and
        # 'self.undef' ?

    def run(self):

        if not self.executables:
            return

        self.mkpath(self.build_cexe)

        # Yech -- this is cut 'n pasted from build_ext.py!
        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)

        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for (name,value) in self.define:
                self.compiler.define_macro(name, value)

        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)
                
        self.build_executables(self.executables)


    def check_executable_list(self, executables):
        """Ensure that the list of executables is valid.

        `executable` is presumably provided as a command option 'executables'.
        This method checks that it is a list of 2-tuples, where the tuples
        are (executable_name, build_info_dict).

        Raise DistutilsSetupError if the structure is invalid anywhere;
        just returns otherwise.
        """
        if not isinstance(executables, list):
            raise DistutilsSetupError, \
                  "'executables' option must be a list of tuples"

        for exe in executables:
            if not isinstance(exe, tuple) and len(exe) != 2:
                raise DistutilsSetupError, \
                      "each element of 'executables' must a 2-tuple"

            name, build_info = exe

            if not isinstance(name, str):
                raise DistutilsSetupError, \
                      "first element of each tuple in 'executables' " + \
                      "must be a string (the executables name)"
            if '/' in name or (os.sep != '/' and os.sep in name):
                raise DistutilsSetupError, \
                      ("bad executable name '%s': " +
                       "may not contain directory separators") % \
                      exe[0]

            if not isinstance(build_info, dict):
                raise DistutilsSetupError, \
                      "second element of each tuple in 'executables' " + \
                      "must be a dictionary (build info)"

    def get_executable_names(self):
        # Assume the executables list is valid -- 'check_executable_list()' is
        # called from 'finalize_options()', so it should be!
        if not self.executables:
            return None

        exe_names = []
        for (exe_name, build_info) in self.executables:
            exe_names.append(exe_name)
        return exe_names


    def get_source_files(self):
        self.check_executable_list(self.executables)
        filenames = []
        for (exe_name, build_info) in self.executables:
            sources = build_info.get('sources')
            if sources is None or not isinstance(sources, (list, tuple)):
                raise DistutilsSetupError, \
                      ("in 'executables' option (library '%s'), "
                       "'sources' must be present and must be "
                       "a list of source filenames") % exe_name

            filenames.extend(sources)
        return filenames
    
    def substitute_sources(self,exe_name,sources):
        return list(sources)

    def build_executables(self, executables):
        for (exe_name, build_info) in executables:
            sources = build_info.get('sources')
            if sources is None or not isinstance(sources, (list, tuple)):
                raise DistutilsSetupError, \
                      ("in 'executables' option (library '%s'), " +
                       "'sources' must be present and must be " +
                       "a list of source filenames") % exe_name
            sources = self.substitute_sources(exe_name,sources)

            log.info("building '%s' program", exe_name)

            # First, compile the source code to object files in the library
            # directory.  (This should probably change to putting object
            # files in a temporary build directory.)
            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')
            extra_args = self.extra_compile_args or []
            
            objects = self.compiler.compile(sources,
                                            output_dir=self.build_temp,
                                            macros=macros,
                                            include_dirs=include_dirs,
                                            extra_postargs=extra_args,
                                            debug=self.debug)

            # Now "link" the object files together into a static library.
            # (On Unix at least, this isn't really linking -- it just
            # builds an archive.  Whatever.)
            self.compiler.link_executable(objects, exe_name,
                                            output_dir=self.build_cexe,
                                            debug=self.debug)

