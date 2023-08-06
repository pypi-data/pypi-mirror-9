'''
Created on 20 oct. 2012

@author: coissac
'''

from os import path
import os.path
import glob
import sys
from obidistutils.command.sdist import sdist


try:
    from setuptools import setup as ori_setup
    has_setuptools = True
except ImportError:
    from distutils.core import setup as ori_setup
    has_setuptools = False

from distutils.extension import Extension


from obidistutils.command.build import build
from obidistutils.command.littlebigman import littlebigman
from obidistutils.command.build_cexe import build_cexe
from obidistutils.command.build_sphinx import build_sphinx
from obidistutils.command import build_ext
from obidistutils.command.build_ctools import build_ctools
from obidistutils.command.build_files import build_files
from obidistutils.command.build_scripts import build_scripts
from obidistutils.command.install_scripts import install_scripts
from obidistutils.command.install_sphinx import install_sphinx
from obidistutils.command.install import install
from obidistutils.command.pidname import pidname

from obidistutils.dist import Distribution


def findPackage(root,base=None):
    modules=[]
    if base is None:
        base=[]
    for module in (path.basename(path.dirname(x)) 
                   for x in glob.glob(path.join(root,'*','__init__.py'))):
        modules.append('.'.join(base+[module]))
        modules.extend(findPackage(path.join(root,module),base+[module]))
    return modules
    
def findCython(root,base=None,pyrexs=None):
    setupdir = os.path.dirname(sys.argv[0])
    pyrexs=[]

    if base is None:
        base=[]
    for module in (path.basename(path.dirname(x)) 
                   for x in glob.glob(path.join(root,'*','__init__.py'))):
                       
                
        for pyrex in glob.glob(path.join(root,module,'*.pyx')):
            pyrexs.append(Extension('.'.join(base+[module,path.splitext(path.basename(pyrex))[0]]),[pyrex]))
            try:
                cfiles = os.path.splitext(pyrex)[0]+".cfiles"
                cfilesdir = os.path.dirname(cfiles)
                cfiles = open(cfiles)
                cfiles = [os.path.relpath(os.path.join(cfilesdir,y),setupdir).strip() 
                          if y[0] !='@' else y.strip()
                          for y in cfiles]
                
                print "@@@@>",cfiles
                incdir = set(os.path.dirname(x) for x in cfiles if x[-2:]==".h")
                cfiles = [x for x in cfiles if x[-2:]==".c"]                
                pyrexs[-1].sources.extend(cfiles)
                pyrexs[-1].include_dirs.extend(incdir)
                pyrexs[-1].extra_compile_args.extend(['-msse2'])
                
            except IOError:
                pass
            pyrexs[-1].sources.extend(glob.glob(os.path.splitext(pyrex)[0]+'.ext.*.c'))
            print pyrexs[-1].sources
            # Main.compile([pyrex],timestamps=True)
            
        pyrexs.extend(findCython(path.join(root,module),base+[module]))
    return pyrexs
    
def findC(root,base=None,pyrexs=None):
    setupdir = os.path.dirname(sys.argv[0])
    pyrexs=[]
    if base is None:
        base=[]
    for module in (path.basename(path.dirname(x)) 
                   for x in glob.glob(path.join(root,'*','__init__.py'))):
                
        for pyrex in glob.glob(path.join(root,module,'*.c')):
            if '.ext.' not in pyrex:
                pyrexs.append(Extension('.'.join(base+[module,path.splitext(path.basename(pyrex))[0]]),[pyrex]))
                try:
                    cfiles = os.path.splitext(pyrex)[0]+".cfiles"
                    cfilesdir = os.path.dirname(cfiles)
                    cfiles = open(cfiles)
                    cfiles = [os.path.relpath(os.path.join(cfilesdir,y),setupdir).strip() 
                              if y[0] !='@' else y.strip()
                              for y in cfiles]
                    incdir = set(os.path.dirname(x) for x in cfiles if x[-2:]==".h")
                    cfiles = [x for x in cfiles if x[-2:]==".c"]                
                    pyrexs[-1].sources.extend(cfiles)
                    pyrexs[-1].include_dirs.extend(incdir)
                    pyrexs[-1].extra_compile_args.extend(['-msse2'])
                except IOError:
                    pass
                pyrexs[-1].sources.extend(glob.glob(os.path.splitext(pyrex)[0]+'.ext.*.c'))
                print pyrexs[-1].sources
       
        pyrexs.extend(findC(path.join(root,module),base+[module]))
    return pyrexs

def rootname(x):
    return os.path.splitext(x.sources[0])[0]

COMMANDS = {'build':build,
            'littlebigman':littlebigman,
            'pidname':pidname,
            'build_ctools':build_ctools, 
            'build_files':build_files,
            'build_cexe':build_cexe, 
            'build_ext': build_ext,
            'build_scripts':build_scripts, 
            'build_sphinx':build_sphinx, 
            'install_scripts':install_scripts,
            'install_sphinx':install_sphinx,
            'install':install,
            'sdist':sdist}

CTOOLS =[]
CEXES  =[]
FILES  =[]

def setup(**attrs):
    
    if has_setuptools:
        try:
            
            requirements = open('requirements.txt').readlines()
            requirements = [x.strip() for x in requirements]
            requirements = [x for x in requirements if x[0]!='-']
        
            if 'install_requires' not in attrs:
                attrs['install_requires']=requirements
            else:
                attrs['install_requires'].extend(requirements)
        except IOError:
            pass

    if 'distclass' not in attrs:
        attrs['distclass']=Distribution

    if 'python_src' not in attrs:
        SRC = 'src'
    else:
        SRC = attrs['python_src']
        del(attrs['python_src'])
    
    if 'scripts' not in attrs:
        attrs['scripts'] = glob.glob('%s/*.py' % SRC)

    if 'package_dir' not in attrs:
        attrs['package_dir'] = {'': SRC}

    if 'packages' not in attrs:
        attrs['packages'] = findPackage(SRC)
    
    if 'cmdclass' not in attrs:
        attrs['cmdclass'] = COMMANDS

    if 'ctools' not in attrs:
        attrs['ctools'] = CTOOLS
    
    if 'executables' not in attrs:
        attrs['executables'] = CEXES
        
    if 'files' not in attrs:
        attrs['files'] = FILES
        
    if 'sse' not in attrs:
        attrs['sse']=None
        
    if 'serenity' not in attrs:
        attrs['serenity']=False
    

    EXTENTION=findCython(SRC)
    CEXTENTION=findC(SRC)
    cython_ext = set(rootname(x) for x in EXTENTION)
    EXTENTION.extend(x for x in CEXTENTION 
                     if rootname(x) not in cython_ext)
    
    if 'ext_modules' not in attrs:
        attrs['ext_modules'] = EXTENTION
    
    ori_setup(**attrs)
