'''
Created on 2 oct. 2014

@author: coissac
'''

import re
import sys
import os

from distutils.version import StrictVersion          # @UnusedImport
from distutils.errors import DistutilsError
from distutils import log

from obidistutils.serenity.checkpip import get_a_pip_module

def is_installed(requirement,pip=None):

    if pip is None:
        pip = get_a_pip_module()
    
    get_installed_distributions=pip.util.get_installed_distributions
    
    requirement_project,requirement_relation,requirement_version = parse_package_requirement(requirement)
    
    package = [x for x in get_installed_distributions() if x.project_name==requirement_project]
    
    if len(package)==1:
        if requirement_version is not None and requirement_relation is not None:    
            rep = (len(package)==1) and eval("StrictVersion('%s') %s StrictVersion('%s')" % (package[0].version,
                                                                                           requirement_relation,
                                                                                           requirement_version)
                                             )
        else:
            rep=True
    else:
        rep=False
    
    if rep:
        if requirement_version is not None and requirement_relation is not None:        
            log.info("Look for package %s (%s%s) : ok version %s installed" % (requirement_project,
                                                                               requirement_relation,
                                                                               requirement_version,
                                                                               package[0].version))
        else:
            log.info("Look for package %s : ok version %s installed" % (requirement_project,
                                                                        package[0].version))
    else:
        if len(package)!=1:
            log.info("Look for package %s (%s%s) : not installed" % (requirement_project,
                                                                     requirement_relation,
                                                                     requirement_version))
        else:
            log.info("Look for package %s (%s%s) : failed only version %s installed" % (requirement_project,
                                                                                        requirement_relation,
                                                                                        requirement_version,
                                                                                        package[0].version))
        
    return rep


def get_requirements(pip=None):
    
    if pip is None:
        pip = get_a_pip_module()
        
    try:
        requirements = open('requirements.txt').readlines()
        requirements = [x.strip() for x in requirements]
        requirements = [x for x in requirements if x[0]!='-']
    
    except IOError:
        requirements = []
        
    return requirements
    
    
def install_requirements(skip_virtualenv=True,pip=None):
    
    if pip is None:
        pip = get_a_pip_module()
    
 
    try:
        requirements = open('requirements.txt').readlines()
        requirements = [x.strip() for x in requirements]
        requirements = [x for x in requirements if x[0]!='-']
    
        log.info("Required packages for the installation :")
        for x in requirements:
            if not skip_virtualenv or x[0:10]!='virtualenv':
                ok = is_installed(x,pip)
                if not ok:
                    log.info("  Installing requirement : %s" % x)
                    pip_install_package(x,pip=pip)
                
    except IOError:
        pass
 

def check_requirements(skip_virtualenv=True,pip=None):
    
    if pip is None:
        pip = get_a_pip_module()
    
    
    try:
        requirements = open('requirements.txt').readlines()
        requirements = [x.strip() for x in requirements]
        requirements = [x for x in requirements if x[0]!='-']
    
        log.info("Required packages for the installation :")
        for x in requirements:
            if not skip_virtualenv or x[0:10]!='virtualenv':
                ok = is_installed(x,pip)
                if not ok:
                    log.error("  Missing requirement : %s -- Package installation stopped" % x)
                    sys.exit(0)
                
    except IOError:
        pass
 


def parse_package_requirement(requirement):
    
    version_pattern = re.compile('[=><]+(.*)$')
    project_pattern  = re.compile('[^=><]+')
    relationship_pattern = re.compile('[=><]+')
    
    try:
        requirement_project = project_pattern.search(requirement).group(0)
        requirement_version = version_pattern.search(requirement)
        if requirement_version is not None:
            requirement_version=requirement_version.group(1)
        requirement_relation= relationship_pattern.search(requirement)
        if requirement_relation is not None:
            requirement_relation=requirement_relation.group(0)
    except:
        raise DistutilsError,"Requirement : %s not correctly formated" % requirement
    
    return requirement_project,requirement_relation,requirement_version
    

def get_package_requirement(package,pip=None):            
    if pip is None:
        pip = get_a_pip_module()
        
    requirements = get_requirements(pip)
    req = [x for x in requirements
             if x[0:len(package)]==package
          ]
    
    if len(req)==1:
        return req[0]
    else:
        return None
        
        
def pip_install_package(package,directory=None,pip=None):

    log.info('installing %s in directory %s' % (package,str(directory)))

    if 'http_proxy' in os.environ and 'https_proxy' not in os.environ:
        os.environ['https_proxy']=os.environ['http_proxy']

    if pip is None:
        pip = get_a_pip_module()
                
    args = ['install']
    
    if 'http_proxy' in os.environ:
        args.append('--proxy=%s' % os.environ['http_proxy'])
        
    if directory is not None:
        args.append('--target=%s' % directory)
    
    args.append(package)
        
    return pip.main(args)

