# cython: profile=True

'''
Created on 16 sept. 2009

@author: coissac
'''


#from obitools.fasta._fasta cimport *
from obitools.fasta._fasta cimport fastParseFastaDescription
from obitools.fasta._fasta cimport parseFastaDescription
from obitools._obitools cimport BioSequence
from obitools._obitools cimport __default_raw_parser
from obitools._obitools cimport AASequence,NucSequence

from array import array
from obitools import bioSeqGenerator
from obitools.format.genericparser import genericEntryIteratorGenerator
from obitools.utils import universalOpen

import re 
import sys


cimport array
#from cpython cimport array


cdef import from "math.h" :
    double log10(double x)
    double rint(double x)
    
cdef import from "string.h":
    int strlen(char* s)
    void bzero(void *s, size_t n)
    
cdef import from "stdlib.h":
    void* malloc(int size)  except NULL
    void* realloc(void* chunk,int size)  except NULL
    void free(void* chunk)
    

fastqEntryIterator=genericEntryIteratorGenerator(startEntry=b'^@',endEntry=b"^\+",strip=True,join=False)

 

cpdef array.array[double] fastqQualityDecoder(char* qualstring, int base=0):
    cdef int i=0
    cdef int mq=255
    cdef object oaddresse,olength
    cdef int length
    cdef array.array quality
    cdef double* bdouble
     
#    quality = array.array(b'd',[0]*strlen(qualstring))
    quality = array.array(b'd',[0])

#    print >>sys.stderr,"+@@> ",sys.getrefcount(quality)

    array.resize(quality,strlen(qualstring))
#    (oaddress,olength)=quality.buffer_info()
    bdouble=quality._d 
    
    if base==0:
        mq = 255
        while (qualstring[i]!=0):
            if qualstring[i]<mq:
                mq=qualstring[i]
            i+=1
        if mq < 59:
            base=33
        else:
            base=64
            
    i=0    
    while (qualstring[i]!=0):
        bdouble[i]=qualstring[i]-base
        i+=1
        
    return quality

cpdef array.array[double] fastqQualitySangerDecoder(char* qualstring):
        return fastqQualityDecoder(qualstring,33)
    
cpdef array.array[double] fastqQualitySolexaDecoder(char* qualstring):
        return fastqQualityDecoder(qualstring,64)
    
cpdef array.array[double] qualityToSolexaError(array.array quality):
    cdef int i=0
    cdef int lq
    cdef double proba
    cdef object oaddresse,olength
    cdef int length
    cdef double* bdouble
    
    (oaddress,olength)=quality.buffer_info()
    bdouble=<double*><unsigned long int>oaddress 
    lq=olength
    
    for i in range(lq):
        proba=1/(1+10.**(bdouble[i]/10.))
        bdouble[i]=proba
    
    return quality

cpdef array.array[double] qualityToSangerError(array.array quality):
    cdef int i=0
    cdef int lq
    cdef double proba
    cdef object oaddresse,olength
    cdef int length
    cdef double* bdouble
    
    (oaddress,olength)=quality.buffer_info()
    bdouble=<double*><unsigned long int>oaddress 
    lq=olength
    
    for i in range(lq):
        proba=10.**(-bdouble[i]/10.)
        bdouble[i]=proba
    
    return quality

cpdef array.array[double] errorToSangerQuality(array.array quality):
    cdef int i=0
    cdef int lq
    cdef double proba
    cdef object oaddresse,olength
    cdef int length
    cdef double* bdouble
    
    (oaddress,olength)=quality.buffer_info()
    bdouble=<double*><unsigned long int>oaddress 
    lq=olength
    
    for i in range(lq):
        proba=-rint(log10(bdouble[i])*10)
        bdouble[i]=proba
    
    return quality
        
cpdef array.array[double] solexaToSangerQuality(array.array quality):
    cdef int i=0
    cdef int lq
    cdef double proba
    cdef object oaddresse,olength
    cdef int length
    cdef double* bdouble
    
    (oaddress,olength)=quality.buffer_info()
    bdouble=<double*><unsigned long int>oaddress 
    lq=olength
    
    for i in range(lq):
        proba=-rint(log10(1/(1+10.**(bdouble[i]/10.)))*10)
        bdouble[i]=proba
    
    return quality

cpdef bytes errorToSangerFastQStr(array.array quality):
    cdef int i=0
    cdef int lq
    cdef double proba
    cdef object oaddresse,olength
    cdef int length
    cdef double* bdouble
    cdef char* result
    cdef bytes code
    
    (oaddress,olength)=quality.buffer_info()
    bdouble=<double*><unsigned long int>oaddress 
    lq=olength
    result=<char *>malloc(olength+1)
    result[olength]=0
    
    for i in range(lq):
        proba=-rint(log10(bdouble[i])*10)
        if proba > 93.:
            proba=93.
        result[i]=33 + <int>proba
    code=result
    free(<void *>result)
    return code

cpdef bytes formatFastq(object data, bint gbmode=False, bint upper=False):
    cdef list rep=[]
    cdef bytes  seq
    cdef bytes  definition
    cdef bytes  info
    cdef bytes  quality
    cdef bytes  id
    
    
    if isinstance(data, BioSequence):
        data = [data]
        
    for sequence in data:
        seq = str(sequence)
        if upper:
            seq=seq.upper()
        if sequence.definition is None:
            definition=b''
        else:
            definition=sequence.definition
        info=b'; '.join([b'%s=%s' % x for x in sequence.rawiteritems()])
        if info:
            info=info+b';'
            
        if sequence._rawinfo is not None and sequence._rawinfo:
            info+=b" " + sequence._rawinfo.strip()
            

        id = sequence.id
        if gbmode:
            if b'gi' in sequence:
                id = bytes(b"gi|%s|%s" % (sequence[b'gi'],id))
            else:
                id = b"lcl|%s|" % (id)
        if hasattr(sequence, b"quality"):
            quality=errorToSangerFastQStr(sequence.quality)
        else:
            quality=b"I"*len(sequence)
        title=b'@%s %s %s' %(id,info,definition)
        rep.append(b"%s\n%s\n+\n%s" % (title,seq,quality))
    return b'\n'.join(rep)


cdef enum FastqType:
    sanger,solexa

cdef class fastqParserGenetator:
            
    cdef object bioseqfactory
    cdef object tagparser
    cdef object rawparser
    cdef bint _qualityDecoder
    cdef bint _errorDecoder
    
    def __init__(self,fastqvariant=b'sanger',bioseqfactory=NucSequence,tagparser=__default_raw_parser):
        self.bioseqfactory = bioseqfactory
        
        self.rawparser=tagparser
        allparser = tagparser % b'[a-zA-Z][a-zA-Z.0-9_]*'
        tagparser = re.compile(b'( *%s)+' % allparser)

        self.tagparser = tagparser
        # Sanger = True
        # Solexa = False
        self._qualityDecoder, self._errorDecoder = {b'sanger'   : (True,True),
                                                    b'solexa'   : (False,False),
                                                    b'illumina' : (False,True)}[fastqvariant]
                                                  
    cdef errorDecoder(self,object qualstring):
        if self._errorDecoder:
            return qualityToSangerError(qualstring)
        else:
            return qualityToSolexaError(qualstring)
        
    cdef qualityDecoder(self,char* qualstring):
        if self._qualityDecoder:
            return fastqQualitySangerDecoder(qualstring)
        else:
            return fastqQualitySolexaDecoder(qualstring)
        
    def __call__(self,seq):
        cdef str  definition
        cdef str info
        cdef str  id
        cdef str  s0
        cdef str  tseq
        cdef bytes tqual
        
        s0=seq[0]
        title = s0[1:].split(None,1)
        id=title[0]
        if len(title) == 2:
            definition,info=parseFastaDescription(title[1], self.tagparser)
        else:
            info= None
            definition=None
        
        tqual = seq[3]
        quality=self.errorDecoder(self.qualityDecoder(tqual))
    
        tseq=seq[1]
        
        seq = self.bioseqfactory(id, tseq, definition,info,self.rawparser)
        seq.quality = quality
        
        return seq

def fastqIterator(file,fastqvariant=b'sanger',bioseqfactory=NucSequence,tagparser=__default_raw_parser):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be BioSequence
    instances

    @param file: a line iterator containing fasta data or a filename
    @type file:  an iterable object or str
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{BioSequence} instance
 
    @see: L{fastaNucIterator}
    @see: L{fastaAAIterator}

    '''
    fastqParser=fastqParserGenetator(fastqvariant, bioseqfactory, tagparser)
    file = universalOpen(file)
    for entry in fastqEntryIterator(file):
        title=entry[0]
        seq=b"".join(entry[1:-1])
        quality=b''
        lenseq=len(seq)
        while (len(quality) < lenseq):
            quality+=file.next().strip()
            
        yield fastqParser([title,seq,b'+',quality])

def fastqSangerIterator(file,tagparser=__default_raw_parser):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastqIterator(file,b'sanger',NucSequence,tagparser)

def fastqSolexaIterator(file,tagparser=__default_raw_parser):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastqIterator(file,b'solexa',NucSequence,tagparser)

def fastqIlluminaIterator(file,tagparser=__default_raw_parser):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastqIterator(file,b'illumina',NucSequence,tagparser)

def fastqAAIterator(file,tagparser=__default_raw_parser):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be AASequence
    instances
    
    @param file: a line iterator containing fasta data
    @type file: an iterable object
    
    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{AABioSequence} instance

    @see: L{fastqIterator}
    @see: L{fastqNucIterator}
    '''
    return fastqIterator(file,b'sanger',AASequence,tagparser)


cdef class fastFastqParserGenetator(fastqParserGenetator):
            
    
    def __init__(self,fastqvariant=b'sanger'):
        
        self.rawparser=__default_raw_parser

        # Sanger = True
        # Solexa = False
        self._qualityDecoder, self._errorDecoder = {b'sanger'   : (True,True),
                                                    b'solexa'   : (False,False),
                                                    b'illumina' : (False,True)}[fastqvariant]
                                                  
        
    def __call__(self, list seq):

        cdef bytes s0    = seq[0]
        cdef list  title = s0.split(None,1)    
        cdef bytes id    = title[0][1:]
        cdef bytes defintion,info
        cdef bytes tqual = seq[3]
        cdef bytes tseq  = seq[1]
        cdef object sseq

        if len(title) == 2:
            definition,info=fastParseFastaDescription(title[1])
        else:
            info= None
            definition=None
#FIXME: regarder ici                        
        quality=self.errorDecoder(self.qualityDecoder(tqual))

#        print >>sys.stderr,b"@@@> ",sys.getrefcount(quality)

        sseq = NucSequence(id, tseq, definition,info,__default_raw_parser)
        sseq.quality = quality
        
        return sseq

def fastFastqIterator(file,fastqvariant=b'sanger'):
    '''
    iterate through a fasta file sequence by sequence.
    Returned sequences by this iterator will be BioSequence
    instances

    @param file: a line iterator containing fasta data or a filename
    @type file:  an iterable object or str
    @param bioseqfactory: a callable object return a BioSequence
                          instance.
    @type bioseqfactory: a callable object

    @param tagparser: a compiled regular expression usable
                      to identify key, value couples from 
                      title line.
    @type tagparser: regex instance
    
    @return: an iterator on C{BioSequence} instance
 
    @see: L{fastaNucIterator}
    @see: L{fastaAAIterator}

    '''
    fastqParser=fastFastqParserGenetator(fastqvariant)
    file = universalOpen(file)
    for entry in fastqEntryIterator(file):
        title=entry[0]
        seq=b"".join(entry[1:-1])
        quality=b''
        lenseq=len(seq)
        while (len(quality) < lenseq):
            quality+=file.next().strip()
            
        yield fastqParser([title,seq,b'+',quality])

def fastFastqSangerIterator(file):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastFastqIterator(file,b'sanger')

def fastFastqSolexaIterator(file):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastFastqIterator(file,b'solexa')

def fastFastqIlluminaIterator(file):
    '''
    iterate through a fastq file sequence by sequence.
    Returned sequences by this iterator will be NucSequence
    instances
    
    @param file: a line iterator containint fasta data
    @type file: an iterable object
    
    @return: an iterator on C{NucBioSequence} instance
    
    @see: L{fastqIterator}
    @see: L{fastqAAIterator}
    '''
    return fastFastqIterator(file,b'illumina')

