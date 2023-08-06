# cython: profile=True


import re
from obitools.utils import universalOpen

cdef bint isBeginning(bytes line, object startEntry):
    return startEntry is None or startEntry.match(line) is not None

cdef bint isEnding(bytes line, object startEntry, object endEntry):
    return ((endEntry is not None and endEntry.match(line) is not None) or
            (endEntry is None and startEntry is not None and startEntry.match(line) is not None))
    


def genericEntryIteratorGenerator(bytes startEntry=None,
                                  bytes endEntry=None,
                                  bint head=False,
                                  bint tail=False,
                                  bint strip=False,
                                  bint join=True):
    '''
    Transfom a text line iterator to an entry oriented iterator.
    
    This iterator converted is useful to implement first stage
    of flat file parsing.
    
    @param startEntry: a regular pattern matching the beginning of
                       an entry
    @type startEntry: C{str} or None
    @param endEntry:   a regular pattern matching the end of
                       an entry
    @type endEntry: C{str} or None
    @param head:       indicate if an header is present before
                       the first entry (as in many original genbank
                       files)
    @type head: C{bool}
    @param tail:       indicate if some extra informations are present 
                       after the last entry.
    @type tail: C{bool}
    
    @return: an iterator on entries in text format
    @rtype: an iterator on C{str}
    '''

    if startEntry is not None:
        c_startEntry = re.compile(startEntry)
    else:
        c_startEntry = None
        
    if endEntry is not None:
        c_endEntry = re.compile(endEntry)
    else:
        c_endEntry = None
        
                    
    def transparentIteratorEntry(object f):
        f = universalOpen(f)
        return f

    def genericEntryIterator(file):
        
        cdef list entry = []
        cdef bytes line
        cdef bint started
        
        if not hasattr(file, 'next'):
            file = universalOpen(file)

        line = file.next()
        started = head or isBeginning(line,c_startEntry)
        
        try:
            while 1:
                while not started:
                    line = file.next()
                    started = isBeginning(line,c_startEntry)
                    
                if endEntry is None:
                    entry.append(line)
                    line = file.next()
                    
                while started:
                    end = isEnding(line,c_startEntry,c_endEntry)
                    if end:
                        if endEntry is not None:
                            entry.append(line)
                        if join:
                            e = ''.join(entry)
                            if strip:
                                e=e.strip()
                        else:
                            e=entry
                            if strip:
                                e=[x.strip() for x in e]
                        entry=[]
                        yield e
                        started=False
                        if endEntry is not None:
                            line = file.next()
                    else:
                        entry.append(line)
                        line = file.next()
                        
                started = isBeginning(line,c_startEntry) 
                       
        except StopIteration:
            if entry and (endEntry is None or tail):
                if join:
                    e = ''.join(entry)
                    if strip:
                        e=e.strip()
                else:
                    e=entry
                    if strip:
                        e=[x.strip() for x in e]
                yield e

                            
                
    if startEntry is None and endEntry is None:
        return transparentIteratorEntry
    
    return genericEntryIterator


class GenericParser(object):
    
    def __init__(self,
                 startEntry=None,
                 endEntry=None,
                 head=False,
                 tail=False,
                 strip=False,
                 **parseAction):
        """
        @param startEntry: a regular pattern matching the beginning of
                           an entry
        @type startEntry: C{str} or None
        @param endEntry:   a regular pattern matching the end of
                           an entry
        @type endEntry: C{str} or None
        @param head:       indicate if an header is present before
                           the first entry (as in many original genbank
                           files)
        @type head: C{bool}
        @param tail:       indicate if some extra informations are present 
                           after the last entry.
        @type tail: C{bool}
        
        @param parseAction:  
        
        """
        self.flatiterator= genericEntryIteratorGenerator(startEntry, 
                                                         endEntry, 
                                                         head, 
                                                         tail,
                                                         strip)
        
        self.action={}
        
        for k in parseAction:
            self.addParseAction(k,*parseAction[k])
            
    def addParseAction(self,name,dataMatcher,dataCleaner=None,cleanSub=''):
        '''
        Add a parse action to the generic parser. A parse action
        allows to extract one information from an entry. A parse
        action is defined by a name and a method to extract this 
        information from the full text entry.
        
        A parse action can be defined following two ways.
        
            - via regular expression patterns
            
            - via dedicated function.
            
        In the first case, you have to indicate at least the
        dataMatcher regular pattern. This pattern should match exactly
        the data part you want to retrieve. If cleanning of extra 
        characters is needed. The second pattern dataCLeanner can be
        used to specifyed these characters.
        
        In the second case you must provide a callable object (function)
        that extract and clean data from the text entry. This function
        should return an array containing all data retrevied even if 
        no data or only one data is retrevied.
        
        @summary: Add a parse action to the generic parser.
        
        @param name: name of the data extracted
        @type name:    C{str}
        @param dataMatcher: a regular pattern matching the data
                            or a callable object parsing the
                            entry and returning a list of marched data
        @type dataMatcher:  C{str} or C{SRE_Pattern} instance or a callable 
                            object
        @param dataCleaner: a regular pattern matching part of the data
                            to suppress.
        @type dataCleaner: C{str} or C{SRE_Pattern} instance or C{None}
        @param cleanSub: string used to replace dataCleaner matches.
                         Default is an empty string
        @type cleanSub: C{str}
        
        '''
        if callable(dataMatcher):
            self.action[name]=dataMatcher
        else :
            if isinstance(dataMatcher, str):
                dataMatcher=re.compile(dataMatcher)
            if isinstance(dataCleaner, str):
                dataCleaner=re.compile(dataCleaner)
            self.action[name]=self._buildREParser(dataMatcher,
                                                 dataCleaner,
                                                 cleanSub)
            
    def _buildREParser(self,dataMatcher,dataCleaner,cleanSub):
        def parser(data):
            x = dataMatcher.findall(data)
            if dataCleaner is not None:
                x = [dataCleaner.sub(cleanSub,y) for y in x]
            return x
        return parser
    
    def __call__(self,file):
        for e in self.flatiterator(file):
            pe = {'fullentry':e}
            for k in self.action:
                pe[k]=self.action[k](e)
            yield pe
            
            
