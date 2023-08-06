# cython: profile=True

from obitools.utils._utils cimport progressBar

from obitools.utils import universalOpen
from obitools.utils import universalTell
from obitools.utils import fileSize
from obitools.ecopcr.sequence import EcoPCRDBSequenceIterator
from glob import glob 
from logging import debug
import sys

cdef extern from "stdio.h":
    ctypedef unsigned int off_t "unsigned long long"
    
    
cdef class CurrentFileStatus:
    cdef public bytes currentInputFileName
    cdef public object currentFile
    cdef public off_t currentFileSize

    def __init__(self):
        self.currentInputFileName=None
        self.currentFile = None
        self.currentFileSize = -1

cfs=CurrentFileStatus()

cpdef bytes currentInputFileName():
    return cfs.currentInputFileName

cpdef object  currentInputFile():
    return cfs.currentFile

cpdef off_t currentFileSize():
    return cfs.currentFileSize

cpdef off_t currentFileTell():
    return universalTell(cfs.currentFile)

def fileWithProgressBar(file, int step=100):
   
    cdef off_t size
    cdef off_t pos
    
    size = cfs.currentFileSize
                
    def fileBar():
        
        cdef str l
        
        pos=1
        progressBar(pos, size, True,cfs.currentInputFileName)
        for l in file:
            progressBar(currentFileTell,size, False,
                        cfs.currentInputFileName)
            yield l 
        print >>sys.stderr,''   
         
    if size < 0:
        return file
    else:
        f = fileBar()
        return f


def allEntryIterator(files,entryIterator,with_progress=False,histo_step=102,options=None):

    if files :
        for f in files:
            if (entryIterator != EcoPCRDBSequenceIterator) :
                          
                cfs.currentInputFileName=f
                try:
                    f = universalOpen(f,noError=True)
                except Exception as e:    
                    if glob('%s_[0-9][0-9][0-9].sdx' % f):
                        entryIterator=EcoPCRDBSequenceIterator
                    else:
                        print >>sys.stderr, e
                        sys.exit();
                else:
                    cfs.currentFile=f
                    cfs.currentFileSize=fileSize(cfs.currentFile)
                    debug(f)
                
                    if with_progress and cfs.currentFileSize >0:
                        f=fileWithProgressBar(f,step=histo_step)           
                    
            if entryIterator is None:
                for line in f:
                    yield line
            else:
                
                if entryIterator == EcoPCRDBSequenceIterator and options is not None:
                    if options.ecodb==f:
                        iterator = entryIterator(f,options.taxonomy)
                    else:
                        iterator = entryIterator(f)
                        options.taxonomy=iterator.taxonomy
                        options.ecodb=f
                else:
                    iterator = entryIterator(f)
                for entry in iterator:
                    yield entry
            
 
    else:
        if entryIterator is None:
            for line in sys.stdin:
                yield line
        else:
            import os, stat
            
            mode = os.fstat(0).st_mode
            if stat.S_ISFIFO(mode):
                pass
            elif stat.S_ISREG(mode):
                pass
            else:
                print>>sys.stderr, "No Entry to process"
                sys.exit()
            for entry in entryIterator(sys.stdin):
                yield entry
