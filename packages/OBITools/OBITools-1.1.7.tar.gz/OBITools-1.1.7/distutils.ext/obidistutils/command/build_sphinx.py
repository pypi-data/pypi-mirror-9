'''
Created on 10 mars 2015

@author: coissac
'''

from distutils import log

try:
    from sphinx.setup_command import BuildDoc as ori_build_sphinx
    
    class build_sphinx(ori_build_sphinx):
        '''
        Build Sphinx documentation in html, epub and man formats 
        '''
    
        description = __doc__
    
        def run(self):
            self.builder='html'
            self.finalize_options()
            ori_build_sphinx.run(self)
            self.builder='epub'
            self.finalize_options()
            ori_build_sphinx.run(self)
            self.builder='man'
            self.finalize_options()
            ori_build_sphinx.run(self)
except ImportError:
    from distutils.core import Command

    class build_sphinx(Command):
        '''
        Build Sphinx documentation in html, epub and man formats 
        '''
    
        description = __doc__
    
        def run(self):
            log.info("Sphinx not installed documentation will not be generated")
            
    