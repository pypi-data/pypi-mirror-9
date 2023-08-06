'''
Created on 20 oct. 2012

@author: coissac
'''


from distutils.dist import Distribution as ori_Distribution

class Distribution(ori_Distribution):
    
    def __init__(self,attrs=None):
        self.executables = None
        self.ctools = None
        self.files = None
        self.build_cexe  = None
        self.deprecated_scripts = None
        self.zip_safe=False
        self.sse = None
        self.serenity=attrs['serenity']
        
        ori_Distribution.__init__(self, attrs)
        
        self.global_options.insert(0,('serenity', None, "install or build the package in a python virtualenv "
                                                       "without polluting the installed python and with many "
                                                       "checks during the installation process"
                                     ))
        self.global_options.insert(0,('virtualenv', None, "if the installation is done using the serenity mode "
                                                        "this option allows for specifying the virtualenv name. "
                                                        "By default the name is PACKAGE-VERSION"
                                     ))
        
        
    def has_executables(self):
        return self.executables is not None and self.executables
        
    def has_ctools(self):
        return self.ctools is not None and self.ctools
        
    def has_files(self):
        return self.files is not None and self.files
        
    def has_deprecated_scripts(self):
        return self.deprecated_scripts is not None and self.deprecated_scripts

    