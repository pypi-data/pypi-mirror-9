'''
Created on 13 fevr. 2014

@author: coissac
'''

try:
    from Cython.Distutils import build_ext  as ori_build_ext  # @UnresolvedImport
except ImportError:
    from distutils.command.build_ext import build_ext as ori_build_ext 
from distutils.errors import DistutilsSetupError
import os


class build_ext(ori_build_ext):
    def modifyDocScripts(self):
        print >>open("doc/sphinx/build_dir.txt","w"),self.build_lib
        
    def initialize_options(self):
        ori_build_ext.initialize_options(self)  
        self.littlebigman = None
        self.built_files = None

    
    def finalize_options(self):
        ori_build_ext.finalize_options(self)

        self.set_undefined_options('littlebigman',
                                   ('littlebigman',  'littlebigman'))
        
        self.set_undefined_options('build_files',
                                   ('files',  'built_files'))

        self.cython_c_in_temp = 1
                   
        if self.littlebigman =='-DLITTLE_END':
            if self.define is None:
                self.define=[('LITTLE_END',None)]
            else:
                self.define.append('LITTLE_END',None)
        
    def substitute_sources(self,exe_name,sources):
        """
        Substitutes source file name starting by an @ by the actual
        name of the built file (see --> build_files)
        """
        sources = list(sources)
        for i in xrange(len(sources)):
            print exe_name,sources[i],
            if sources[i][0]=='@':
                try:
                    filename = self.built_files[sources[i][1:]]
                except KeyError:
                    tmpfilename = os.path.join(self.build_temp,sources[i][1:])
                    if os.path.isfile       (tmpfilename):
                        filename = tmpfilename
                    else:
                        raise DistutilsSetupError, \
                            ('The %s filename declared in the source '
                             'files of the program %s have not been '
                             'built by the installation process') % (sources[i],
                                                                     exe_name)
                sources[i]=filename
                print "changed to ",filename
            else:
                print " ok"

        return sources

    def build_extensions(self):
        # First, sanity-check the 'extensions' list
        
        for ext in self.extensions:
            ext.sources = self.substitute_sources(ext.name,ext.sources)
            
        self.check_extensions_list(self.extensions)

        for ext in self.extensions:
            print "#####>",ext.sources
            ext.sources = self.cython_sources(ext.sources, ext)
            self.build_extension(ext)

        
    def run(self):
        self.modifyDocScripts()
        ori_build_ext.run(self)
        
        
        


        