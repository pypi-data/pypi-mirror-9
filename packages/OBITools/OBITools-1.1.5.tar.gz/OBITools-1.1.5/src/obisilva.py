#!/usr/local/bin/python
'''
:py:mod:`obisilva`: converts silva database into an ecoPCR database
===================================================================

:py:mod:`obisilva`: converts and optionally download the `Silva database <http://www.arb-silva.de>`_
into an ecoPCR database. The formated database include the taxonomy as defined by the Silva authors.

.. warning::
    Take care that the numeric taxids associated to the sequences are specific 
    to this Silva database and not compatible with the NCBI taxids. 
    The taxids present in a version of the Silva database (*i.e* ssu, lsu, parc, ref...)
    are are just valid for this version of the database and not compatible 
    with the taxids used in another version.

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

'''


from obitools.options import getOptionManager
from obitools.ecopcr.taxonomy import ecoTaxonomyWriter, Taxonomy
from obitools.fasta import fastaIterator
import sys
from obitools.utils import universalOpen, ColumnFile
import re
import urllib2
from obitools import NucSequence
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
    optionManager.add_option('-s','--ssu',
                             action="store_const", dest="rrna",
                             metavar="<taxon_name>:rank:parent",
                             const = "ssu",
                             default=None,
                             help="specify that you are interested in the SSU database")
    
    optionManager.add_option('-l','--lsu',
                             action="store_const", dest="rrna",
                             metavar="<taxon_name>:rank:parent",
                             const = "lsu",
                             default=None,
                             help="specify that you are interested in the LSU database")

    optionManager.add_option('-p','--parc',
                             action="store_const", dest="type",
                             metavar="<taxon_name>:rank:parent",
                             const = "parc",
                             default=None,
                             help="specify that you are interested in the parc version of the database")
    
    optionManager.add_option('-r','--ref',
                             action="store_const", dest="type",
                             metavar="<taxon_name>:rank:parent",
                             const = "ref",
                             default=None,
                             help="specify that you are interested in the reference version of the database")

    optionManager.add_option('-n','--nr',
                             action="store_true", dest="nr",
                             default=False,
                             help="specify that you are interested in the non redundant version of the database")

    optionManager.add_option('-t','--trunc',
                             action="store_true", dest="trunc",
                             default=False,
                             help="specify that you are interested in the truncated version of database")
    
    optionManager.add_option('--localdb',
                             action="store", dest="local",
                             type='str',
                             default=None,
                             help="Local copy of the files located in the specified directory "
                             "will be used instead of those present on the ARB-Silva web site")

    optionManager.add_option('-m','--min-taxid',
                             action="store", dest="taxashift",
                             type="int",
                             metavar="####",
                             default=10000000,
                             help="minimal taxid for the species taxid")
    
siteurl="http://www.arb-silva.de/"
baseurl="%sno_cache/download/archive/current/Exports" % siteurl

# (options.rrna,options.type,options.trunc,options.nr)
seqfilepattern={('lsu','parc',False,False) : "SILVA_%d_LSUParc_tax_silva.fasta.gz",
                ('lsu','parc',False,True ) : None,
                ('lsu','parc',True ,False) : "SILVA_%d_LSUParc_tax_silva_trunc.fasta.gz",
                ('lsu','parc',True ,True ) : None,
                ('lsu','ref' ,False,False) : "SILVA_%d_LSURef_tax_silva.fasta.gz",
                ('lsu','ref' ,False,True ) : None,
                ('lsu','ref' ,True ,False) : "SILVA_%d_LSURef_tax_silva_trunc.fasta.gz",
                ('lsu','ref' ,True ,True ) : None,
                ('ssu','parc',False,False) : "SILVA_%d_SSUParc_tax_silva.fasta.gz",
                ('ssu','parc',False,True ) : None,
                ('ssu','parc',True ,False) : "SILVA_%d_SSUParc_tax_silva_trunc.fasta.gz",
                ('ssu','parc',True ,True ) : None,
                ('ssu','ref' ,False,False) : "SILVA_%d_SSURef_tax_silva.fasta.gz",
                ('ssu','ref' ,False,True ) : "SILVA_%d_SSURef_Nr99_tax_silva.fasta.gz",
                ('ssu','ref' ,True ,False) : "SILVA_%d_SSURef_tax_silva_trunc.fasta.gz",
                ('ssu','ref' ,True ,True ) : "SILVA_%d_SSURef_Nr99_tax_silva_trunc.fasta.gz"
               }
# (options.rrna,options.nr)
taxfilepattern={'lsu' : "tax_slv_lsu_%d.txt",
                'ssu' : "tax_slv_ssu_nr_%d.txt"
               }

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
    
def silvaURLS(options):
    global siteurl
    
    if options.local is not None:
        archive = dict((f,f) for f in listdir(options.local) if isfile(join(options.local,f)))
        taxonomy= dict((f,"taxonomy/"+f) for f in listdir(options.local+'/taxonomy') if isfile(join(options.local+'/taxonomy',f)))
        siteurl=options.local
    else:
        archive=getHyperlink(baseurl)
        taxonomy=getHyperlink(baseurl+"/taxonomy")
        
    silvafile = [x for x in archive.keys() 
                 if x.startswith('SILVA') and (x.endswith('fasta.gz') or x.endswith('fasta'))
                ]
    
    versions = [int(x.split('_')[1]) for x in silvafile]
            
    if all(x==versions[0] for x in versions):
        version = int(versions[0])
    else:
        raise AssertionError("Unable to identify the database version")
        
    whichfile = (options.rrna,options.type,options.trunc,options.nr)
        
    seqfile = seqfilepattern[whichfile]
        
    if seqfile is None:
        raise AssertionError("Non existing version of Silva")
        
    seqfile = seqfile % version
    taxfile = taxfilepattern[options.rrna] % version
    
    try:
        sequrl = archive[seqfile]
    except KeyError:
        if seqfile[-3:]=='.gz':
            seqfile=seqfile[0:-3]
        else:
            seqfile=seqfile+'.gz'
        sequrl = archive[seqfile]
        
    try:
        taxurl = taxonomy[taxfile]
    except KeyError:
        if taxfile[-3:]=='.gz':
            taxfile=taxfile[0:-3]
        else:
            taxfile=taxfile+'.gz'
        taxurl = taxonomy[taxfile]

    output = "silva_%d_%s%s_%s%s" % (version,options.rrna,options.type,
                                     {True:"nr_" ,   False:""}[options.nr],
                                     {True:"trunc" , False:"full"}[options.trunc]
                                    )
    return "%s/%s" %(siteurl,sequrl),"%s/%s" %(siteurl,taxurl),output
    
    
def silvaPathParser(path):
    x = path.strip().rsplit(";",2)[0:2]
    if x[1]=="":
        x[1]=x[0]
        x[0]="root"
    return x
        
class SilvaDump(Taxonomy):  
        
    def __init__(self,taxdump=None):
        
        self._path=taxdump
        self._readNodeTable(taxdump)
        
        print >>sys.stderr,"Adding scientific name..."
                        
#         self._nameidx = {}
#         for x in self._name :
#             if x[0] not in self._nameidx :
#                 self._nameidx[x[0]] = [x[2]]
#             else :
#                 self._nameidx[x[0]].append(x[2])
                
        # self._bigestTaxid = max(x[0] for x in self._taxonomy)

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
                           types=(str,int,str,str,int))
        print >>sys.stderr,"Reading taxonomy dump file..."
            # (taxid,rank,parent)
        
        taxonomy=[[n[1],n[2],n[0]] for n in nodes]
        taxonomy.append([1,'root','root;'])
                
        print >>sys.stderr,"Sorting taxons..."
        
        taxonomy.sort(SilvaDump._taxonCmp)
        
        print >>sys.stderr,"Assigning parent taxids..."
        
        taxidx=dict((n[2][0:-1],n[0]) for n in taxonomy)
        
        taxonomy=[[n[0],n[1]]+ silvaPathParser(n[2]) for n in taxonomy]

        print >>sys.stderr,"Extracting scientific name..."
        
        taxonomy=[[n[0],n[1],taxidx[n[2]],n[3],'silva'] for n in taxonomy]
                
        print >>sys.stderr,"List all taxonomy rank..."    
        ranks =list(set(x[1] for x in taxonomy) | set(['species'])) 
        ranks.sort()
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
        self.silvaname=taxidx
                   
        
def silva2obi(seq,taxonomy,state):
    s = str(seq).lower().replace('u', 't')
    s = NucSequence(seq.id,s,seq.definition)
    ancestor,species = [x.strip() for x in seq.definition.rsplit(';',1)]
    
    try:
        # parent = taxonomy.findTaxonByTaxid(taxonomy.silvaname[ancestor])
        ptaxid=taxonomy.silvaname[ancestor]
        if taxonomy.getRank(ptaxid)=="genus":
            state.add(ptaxid)
        taxid  = taxonomy.addLocalTaxon(species,'species',ptaxid,options.taxashift) 
        s['taxid']=taxid
        s['specie_name']=species
    except KeyError:
        pass
    
    return s                
                   
                           
                 
if __name__ == '__main__':
    
    optionParser = getOptionManager([silvaOptions])

    (options, entries) = optionParser()
    
    if options.rrna is None:
        raise AssertionError("rRNA type not specified (--ssu or --lsu)")
        
    if options.type is None:
        raise AssertionError("library type not specified (--parc or --ref)")
         
    
    sequrl,taxurl,options.ecopcroutput = silvaURLS(options)
    
    taxonomydata = universalOpen(taxurl)
    
    options.taxonomy = SilvaDump(taxonomydata)

#     if options.write != '' :
#         options.write = open(options.write, 'w')
    
    entries = fastaIterator(universalOpen(sequrl))
    writer  = EcoPCRDBSequenceWriter(options)
    
    state = set()
        
    gidx = options.taxonomy.findRankByName('genus')
    ngenus = len([x for x in options.taxonomy._taxonomy if x[1]==gidx])

    progressBar(max(1,len(state)),ngenus,
                head=options.ecopcroutput)


    for e in entries:
        e = silva2obi(e, options.taxonomy,state)

        progressBar(max(1,len(state)),ngenus,
                    head=options.ecopcroutput)
        
        if 'taxid' in e:
            writer.put(e)
        else:
            print >>sys.stderr,"\nCannot find taxon for entry : %s : %s" % (e.id,e.definition)
        
        
    print >>sys.stderr
        
    ecoTaxonomyWriter(options.ecopcroutput,options.taxonomy,onlyLocal=True)

    