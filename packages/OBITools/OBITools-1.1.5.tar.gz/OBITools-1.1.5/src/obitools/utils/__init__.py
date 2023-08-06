import sys

import time
import re
import shelve

from threading import Lock
from logging  import warning
import urllib2

from obitools.gzip import GzipFile
from obitools.zipfile import ZipFile
import os.path

from _utils import FakeFile     # @UnresolvedImport
from _utils import progressBar  # @UnresolvedImport
import zlib

try:
    from collections import Counter
except ImportError:
    from obitools.collections import Counter


class FileFormatError(Exception):
    pass


def uncompressFile(fileobj):
    d = zlib.decompressobj(16+zlib.MAX_WBITS) 
    READ_BLOCK_SIZE = 1024*8

    buf = ""    
    while True:
        data = fileobj.read(READ_BLOCK_SIZE)
        if not data: break
        
        buf = buf + d.decompress(data)
        lines = buf.split('\n')
        buf=lines[-1]
        
        for line in lines[0:-1]:
            yield line+"\n"
            

def universalOpen(file,noError=False):
    '''
    Open a file gziped or not.
    
    If file is a C{str} instance, file is
    concidered as a file name. In this case 
    the C{.gz} suffixe is tested to eventually
    open it a a gziped file.
    
    If file is an other kind of object, it is assumed
    that this object follow the C{file} interface 
    and it is return as is.
    
    @param file: the file to open
    @type file: C{str} or a file like object
    
    @return: an iterator on text lines.
    '''
    if isinstance(file,str):
        try:
            if urllib2.urlparse.urlparse(file)[0]=='':
                rep = open(file)
            else:
                rep  = urllib2.urlopen(file,timeout=15)
                    
            if file[-3:] == '.gz':
                rep = uncompressFile(fileobj=rep)
            if file[-4:] == '.zip':
                zip = ZipFile(file=rep)
                data = zip.infolist()
                assert len(data)==1,'Only zipped file containning a single file can be open'
                name = data[0].filename
                rep = zip.open(name)
        except Exception as e:
            if not noError:
                print >>sys.stderr, e
                sys.exit();
            else:
                raise e
    else:
        rep = file
    return rep

def universalTell(file):
    '''
    Return the position in the file even if
    it is a gziped one.
    
    @param file: the file to check
    @type file: a C{file} like instance
    
    @return: position in the file
    @rtype:  C{int}
    '''
    
    if hasattr(file, "tell"):
        return file.tell()
    else:
        return None

def fileSize(file):
    '''
    Return the file size even if it is a 
    gziped one.
    
    @param file: the file to check
    @type file: a C{file} like instance
    
    @return: the size of the file
    @rtype: C{int}
    '''
    if hasattr(file, "tell"):
        pos = file.tell()
        file.seek(0,2)
        length = file.tell()
        file.seek(pos,0)
    else:
        length=0
    return length


def endLessIterator(endedlist):
    for x in endedlist:
        yield x
    while(1):
        yield endedlist[-1]
    
    
def multiLineWrapper(lineiterator):
    '''
    Aggregator of strings.
    
    @param lineiterator: a stream of strings from an opened OBO file.
    @type lineiterator: a stream of strings.
    
    @return: an aggregated stanza.
    @rtype: an iterotor on str
    
    @note: The aggregator aggregates strings from an opened OBO file.
    When the length of a string is < 2, the current stanza is over.
    '''
    
    for line in lineiterator:
        rep = [line]
        while len(line)>=2 and line[-2]=='\\':
            rep[-1]=rep[-1][0:-2]
            try:
                line = lineiterator.next()
            except StopIteration:
                raise FileFormatError
            rep.append(line)
        yield ''.join(rep)
    
    
def skipWhiteLineIterator(lineiterator):
    '''
    Curator of stanza.
    
    @param lineiterator: a stream of strings from an opened OBO file.
    @type lineiterator: a stream of strings.
    
    @return: a stream of strings without blank strings.
    @rtype: a stream strings
    
    @note: The curator skip white lines of the current stanza.
    '''
    
    for line in lineiterator:
        cleanline = line.strip()
        if cleanline:
            yield line
        else:
            print 'skipped'
    

class ColumnFile(object):
    
    def __init__(self,stream,sep=None,strip=True,
                 types=None,skip=None,head=None,
                 extra=None,
                 extraformat='([a-zA-Z]\w*) *= *([^;]+);'):
        self._stream = universalOpen(stream)
        self._delimiter=sep
        self._strip=strip
        self._extra=extra
        self._extraformat = re.compile(extraformat)
        
        if types:
            self._types=[x for x in types]
            for i in xrange(len(self._types)):
                if self._types[i] is bool:
                    self._types[i]=ColumnFile.str2bool
        else:
            self._types=None
        
        self._skip = skip
        if skip is not None:
            self._lskip= len(skip)
        else:
            self._lskip= 0
        self._head=head
            
    def str2bool(x):
        return bool(eval(x.strip()[0].upper(),{'T':True,'V':True,'F':False}))
                    
    str2bool = staticmethod(str2bool)
            
        
    def __iter__(self):
        return self
    
    def next(self):
        
        def cast(txt,type):
            try:
                v = type(txt)
            except:
                v=None
            return v
        ligne = self._stream.next()
        if self._skip is not None:
            while ligne[0:self._lskip]==self._skip:
                ligne = self._stream.next()
        if self._extra is not None:
            try:
                (ligne,extra) = ligne.rsplit(self._extra,1)
                extra = dict(self._extraformat.findall(extra))
            except ValueError:
                extra=None
        else:
            extra = None
        data = ligne.split(self._delimiter)
        if self._strip or self._types:
            data = [x.strip() for x in data]
        if self._types:
            it = endLessIterator(self._types)
            data = [cast(*x) for x in ((y,it.next()) for y in data)]
        if self._head is not None:
            data=dict(map(None, self._head,data))
            if extra is not None:
                data['__extra__']=extra
        else:
            if extra is not None:
                data.append(extra)
        return data
    
    def tell(self):
        return universalTell(self._stream)

                    
class CachedDB(object):
    
    def __init__(self,cachefile,masterdb):
        self._cache = shelve.open(cachefile,'c')
        self._db = masterdb
        self._lock=Lock()
        
    def _cacheSeq(self,seq):
        self._lock.acquire()
        self._cache[seq.id]=seq
        self._lock.release()
        return seq
        
    def __getitem__(self,ac):
        if isinstance(ac,str):
            self._lock.acquire()
            if ac in self._cache:
#                print >>sys.stderr,"Use cache for %s" % ac
                data = self._cache[ac]
                self._lock.release()

            else:
                self._lock.release()
                data = self._db[ac]
                self._cacheSeq(data)
            return data
        else:
            self._lock.acquire()
            acs = [[x,self._cache.get(x,None)] for x in ac]
            self._lock.release()
            newacs = [ac for ac,cached in acs if cached is None]
            if newacs:
                newseqs = self._db[newacs]
            else:
                newseqs = iter([])
            for r in acs:
                if r[1] is None:
                    r[1]=self._cacheSeq(newseqs.next())
#                else:
#                    print >>sys.stderr,"Use cache for %s" % r[0]
            return (x[1] for x in acs)
    
        
def moduleInDevelopment(name):
    Warning('This module %s is under development : use it with caution' % name)
    
            
def deprecatedScript(newscript):
    current = sys.argv[0]
    print >>sys.stderr,"        "   
    print >>sys.stderr,"        "   
    print >>sys.stderr,"        "   
    print >>sys.stderr,"#########################################################"
    print >>sys.stderr,"#                                                       #"
    print >>sys.stderr,"    W A R N I N G :"
    print >>sys.stderr,"        %s is a deprecated script                     " % os.path.split(current)[1]
    print >>sys.stderr,"        it will disappear in the next obitools version" 
    print >>sys.stderr,"        "   
    print >>sys.stderr,"    The new corresponding command is %s    " % newscript   
    print >>sys.stderr,"#                                                       #"
    print >>sys.stderr,"#########################################################"
    print >>sys.stderr,"        "   
    print >>sys.stderr,"        "   
    print >>sys.stderr,"        "   
