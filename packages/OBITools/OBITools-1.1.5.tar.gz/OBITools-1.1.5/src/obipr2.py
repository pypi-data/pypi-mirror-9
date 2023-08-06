#!/usr/local/bin/python
'''
:py:mod:`obipr2`: converts silva database into an ecoPCR database
=================================================================

:py:mod:`obipr2`: converts and optionally download the `PR2 database <http://ssu-rrna.org/pr2/>`_
into an ecoPCR database. The formated database include the taxonomy as defined by the PR2 authors.

.. warning::
    Take care that the numeric taxids associated to the sequences are specific 
    to this **PR2** database and not compatible with the NCBI taxids. 
    The taxids present in a version of the **PR2** database are are just valid for 
    this version of the database and not compatible with the taxids used in another version
    downloaded at an other time.


*Example:*

    .. code-block:: bash

           > obipr2 
           
   This command downloads and formats the latest version of the PR2 database from
   the official `PR2 web site<http://ssu-rrna.org/pr2/>`_.
        

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

'''


from obitools.options import getOptionManager
from obitools.ecopcr.taxonomy import Taxonomy
from obitools.fasta import fastaIterator
import sys
from obitools.utils import universalOpen, ColumnFile
import re
import urllib2
from obitools.ecopcr.sequence import EcoPCRDBSequenceWriter
from obitools.utils import progressBar
from os.path import isfile, join
from os import listdir




def numberInStr(s) :
    containsNumber = False
    for c in s :
        if c.isdigit() :
            containsNumber = True
    return containsNumber

def silvaOptions(optionManager):
    optionManager.add_option('--localdb',
                             action="store", dest="local",
                             type='str',
                             default=None,
                             help="Local copy of the files located in the specified directory "
                             "will be used instead of those present on the PR2 web site")

    optionManager.add_option('-m','--min-taxid',
                             action="store", dest="taxashift",
                             type="int",
                             metavar="####",
                             default=10000000,
                             help="minimal taxid for the species taxid")

# http://5.196.17.195/pr2/download/entire_database/gb203_pr2.fasta.gz
siteurl="http://5.196.17.195/"
baseurl="%s/pr2/download/entire_database" % siteurl


def getHyperlink(url):
    furl = urllib2.urlopen(url)
    data = "".join([l.strip() for l in furl])
    
    href = re.compile('<a .*?</a>',re.IGNORECASE)
    target=re.compile('href="(.*?)"',re.IGNORECASE)
    filename=re.compile(">(.*?)</a>",re.IGNORECASE)
    
    hrefs = href.findall(data)
    
    links = {}
    
    for h in hrefs:
        t = target.search(h).group(1) 
        f = filename.search(h).group(1)
        links[f]=t 
        
    return links
    
def pr2URLS(options):
    
    global baseurl
    
    if options.local is not None:
        archive = dict((f,f) for f in listdir(options.local) if isfile(join(options.local,f)))
        baseurl=options.local
    else:
        archive=getHyperlink(baseurl)

        
    pr2file = [x.strip() for x in archive.keys() 
                 if x.strip().endswith('pr2.fasta.gz') or x.strip().endswith('pr2.fasta')
                ]
    
    version_pattern = re.compile("^gb([0-9]*)", re.IGNORECASE)
    
    versions = [int(version_pattern.search(x.strip()).group(1)) for x in pr2file]
    latest = max(versions)

    seqfile=pr2file[versions.index(latest)]
        
    pr2txfile = [x for x in archive.keys() 
                 if x.endswith('pr2.tlf.gz') or x.endswith('pr2.tlf')
                ]
            
    versions = [int(version_pattern.search(x).group(1)) for x in pr2txfile]
    print versions
    
    taxfile = pr2txfile[versions.index(latest)]
    
    try:
        sequrl = archive[seqfile]
    except KeyError:
        if seqfile[-3:]=='.gz':
            seqfile=seqfile[0:-3]
        else:
            seqfile=seqfile+'.gz'
        sequrl = archive[seqfile]
        
    try:
        taxurl = archive[taxfile]
    except KeyError:
        if taxfile[-3:]=='.gz':
            taxfile=taxfile[0:-3]
        else:
            taxfile=taxfile+'.gz'
        taxurl = archive[taxfile]

    output = "pr2_gb%d" % latest
           
    return "%s/%s" %(baseurl,sequrl),"%s/%s" %(baseurl,taxurl),output
    
    
pathElementPattern = re.compile("^ *(.*?) {(.*?)} *$", re.IGNORECASE)
def pr2PathParser(path):
    x = pathElementPattern.match(path)
    rank = x.group(1)
    if rank=='classe':
        rank='class'
    elif rank=='ordre':
        rank='order'
    elif rank=='famille':
        rank='family'
    elif rank=='genre':
        rank='genus'
    elif rank=='espece':
        rank='species'
    elif rank.strip()=="":
        rank="no rank"
    
    return rank,x.group(2)
        
class Pr2Dump(Taxonomy):  
        
    def __init__(self,taxdump=None):
        
        self._path=taxdump
        self._readNodeTable(taxdump)
        
        Taxonomy.__init__(self)
           
    def _taxonCmp(t1,t2):
        if t1[0] < t2[0]:
            return -1
        elif t1[0] > t2[0]:
            return +1
        return 0
    
    _taxonCmp=staticmethod(_taxonCmp)
        
    def _readNodeTable(self,dumpfile):

        
        nodes = ColumnFile(dumpfile, 
                           sep='\t', 
                           types=(str,pr2PathParser))
        print >>sys.stderr,"Reading taxonomy dump file..."
            # (taxid,rank,parent)

        nexttaxid = 2  
        taxidx={'root':1}         
        actaxid={} 
        taxonomy=[[1,'root',1,'root','pr2']]
        for node in nodes:
            ac = node[0]
            path = [('root','root')] + node[2:]
            allpath = [[]]
            for s in path:
                allpath.append(allpath[-1]+[s[1]])
                
            allpath.pop(0)
            allpath=[";".join(x) for x in allpath]
            i=0
            for p in allpath:
                try:
                    taxid = taxidx[p]
                except KeyError:
                    taxid=nexttaxid
                    taxidx[p]=taxid
                    nexttaxid+=1
                    parent=p.rsplit(";",1)[0]
                    ptaxid=taxidx[parent]
                    rank = path[i][0]
                    name = path[i][1]
                    taxonomy.append([taxid,rank,ptaxid,name,'pr2'])
                i+=1
            actaxid[ac]=taxid
                                
        print >>sys.stderr,"List all taxonomy rank..."    
        ranks =list(set(x[1] for x in taxonomy)) 
        ranks.sort()
        print >>sys.stderr,ranks
        rankidx = dict(map(None,ranks,xrange(len(ranks))))
        
        self._taxonomy=taxonomy
        self._localtaxon=len(taxonomy)
    
        print >>sys.stderr,"Indexing taxonomy..."
        index = {}
        for i in xrange(self._localtaxon):
            index[self._taxonomy[i][0]]=i
        
        print >>sys.stderr,"Indexing parent and rank..."
        for t in self._taxonomy:
            t[1]=rankidx[t[1]]
            t[2]=index[t[2]]
        
        self._ranks=ranks
        self._index=index 
        self._preferedName = []

        self._name=[(n[3],'scientific name',self._index[n[0]]) for n in taxonomy]    
        self.pr2ac=actaxid
        
                   
        
def pr22obi(seq,taxonomy):

    try:
        # parent = taxonomy.findTaxonByTaxid(taxonomy.silvaname[ancestor])
        oriid=seq.id 
        seq.id,seq.definition=oriid.split("|",1)
        taxid=taxonomy.pr2ac[seq.id]
        seq['taxid']=taxid
    except KeyError:
        pass
    
    return seq            
                   
                           
                 
if __name__ == '__main__':
    
    optionParser = getOptionManager([silvaOptions])

    (options, entries) = optionParser()
    
    sequrl,taxurl,options.ecopcroutput = pr2URLS(options)
    
    taxonomydata = universalOpen(taxurl)
    
    options.taxonomy = Pr2Dump(taxonomydata)

#     if options.write != '' :
#         options.write = open(options.write, 'w')
    
    entries = fastaIterator(universalOpen(sequrl))
    writer  = EcoPCRDBSequenceWriter(options)
    
    nseq = len(options.taxonomy.pr2ac)

    progressBar(1,nseq,
                head=options.ecopcroutput)

    done=0
    for e in entries:
        e = pr22obi(e, options.taxonomy)
        done+=1
        progressBar(done,nseq,
                    head=options.ecopcroutput)
        
        if 'taxid' in e:
            writer.put(e)
        else:
            print >>sys.stderr,"\nCannot find taxon for entry : %s : %s" % (e.id,e.definition)
        
    print >>sys.stderr
        
    