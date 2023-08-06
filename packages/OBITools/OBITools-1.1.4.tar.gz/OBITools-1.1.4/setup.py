#! /usr/bin/env python
#
# Install script
#
#

import sys
import os
import os.path
import re
import glob

from os import path

#
# Add to the python path the directory containing the extensions
# of distutils
#


PACKAGE = "OBITools"
VERSION = "1.1.4"
AUTHOR  = 'Eric Coissac'
EMAIL   = 'eric@coissac.eu'
URL     = 'metabarcoding.org/obitools'
LICENSE = 'CeCILL-V2'

SRC       = 'src'
CSRC      = None

sys.path.append('distutils.ext')

if __name__=="__main__":

    from obidistutils.serenity import serenity_mode
    
    serenity=serenity_mode(PACKAGE,VERSION)
    
    from obidistutils.core import setup
    from obidistutils.core import CTOOLS
    from obidistutils.core import CEXES
    from obidistutils.core import FILES
    
    DEPRECATED_SCRIPTS=["fastaComplement", "fastaUniq","fasta2tab","fastaAnnotate",
                    "fastaSample","fastaGrep","fastaCount","fastaLength",
                    "fastaHead","fastaTail","fastaSplit","fastaStrand",
                    "fastaLocate","solexaPairEnd","ecoTag","obijoinpairedend"
                       ]

    setup(name=PACKAGE,
          description="Scripts and library for sequence analysis",
          classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'License :: Other/Proprietary License',
            'Operating System :: Unix',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Utilities',
          ],
          version=VERSION,
          author=AUTHOR,
          author_email=EMAIL,
          license=LICENSE,
          url=URL,
          python_src=SRC,
          sse='sse2',
          serenity=serenity)


