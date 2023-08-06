#!/usr/local/bin/python

'''
:py:mod:`obiclean`: tags a set of sequences for PCR/sequencing errors identification 
====================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiclean` is a command that classifies sequence records either as ``head``, ``internal`` or ``singleton``.

For that purpose, two pieces of information are used:
    - sequence record counts
    - sequence similarities

*S1* a sequence record is considered as a variant of *S2* another sequence record if and only if:
    - ``count`` of *S1* divided by ``count`` of *S2* is lesser than the ratio *R*.
      *R* default value is set to 1, and can be adjusted between 0 and 1 with the ``-r`` option.
    - both sequences are *related* to one another (they can align with some differences, 
      the maximum number of differences can be specified by the ``-d`` option).

Considering *S* a sequence record, the following properties hold for *S* tagged as:
    - ``head``: 
       + there exists **at least one** sequence record in the dataset that is a variant of *S*
       + there exists **no** sequence record in the dataset such that *S* is a variant of this 
         sequence record
    - ``internal``:
       + there exists **at least one** sequence record in the dataset such that *S* is a variant
         of this sequence record
    - ``singleton``: 
       + there exists **no** sequence record in the dataset that is a variant of *S*
       + there exists **no** sequence record in the dataset such that *S* is a variant of this 
         sequence record

By default, tagging is done once for the whole dataset, but it can also be done sample by sample
by specifying the ``-s`` option. In such a case, the counts are extracted from the sample 
information.

Finally, each sequence record is annotated with three new attributes ``head``, ``internal`` and 
``singleton``. The attribute values are the numbers of samples in which the sequence record has 
been classified in this manner.
'''

from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.graph import UndirectedGraph,Indexer
from obitools.graph.dag import DAG
from obitools.utils import progressBar
from obitools.align import LCS
from obitools.align import isLCSReachable


import sys
import math


def addCleanOptions(optionManager):
    optionManager.add_option('-d','--distance',
                             action="store", dest="dist",
                             metavar="###",
                             type="int",
                             default=1,
                             help="Maximum numbers of errors between two variant sequences [default: 1]")
    optionManager.add_option('-s','--sample',
                             action="store", dest="sample",
                             metavar="<TAGNAME>",
                             type="str",
                             default=None,
                             help="Tag containing sample descriptions")
     
    optionManager.add_option('-g','--graph',
                             action="store", dest="graph",
                             metavar="<TAGNAME>",
                             type="str",
                             default=None,
                             help="File name where the clustering graphs are saved")
     
    optionManager.add_option('-r','--ratio',
                             action="store", dest="ratio",
                             metavar="<FLOAT>",
                             type="float",
                             default="0.5",
                             help="Minimum ratio between counts of two sequence records so that the less abundant "
                                  "one can be considered as a variant of the more abundant "
                                  "[default: 0.5]")
    optionManager.add_option('-H','--head',
                             action="store_true", dest="onlyhead",
                             default=False,
                             help="Outputs only head tagged sequence records")
    
    optionManager.add_option('-C','--cluster',
                             action="store_true", dest="clustermode",
                             default=False,
                             help="Set obiclean in clustering mode")
    
def lookforFather(node,sample):
    father=set()
    
    for neighbour in node.neighbourIterator():
        if sample in neighbour['_sample']:
            if neighbour['_sample'][sample] > node['_sample'][sample]:
                gdfather = lookforFather(neighbour, sample)
                father|=gdfather
    if not father:
        father.add(node)
        
    return father

def cmpseqcount(s1,s2):
    if 'count' not in s1:
        s1['count']=1
    if 'count' not in s2:
        s2['count']=1
    
    return cmp(s2['count'],s1['count'])


if __name__ == '__main__':
    
    optionParser = getOptionManager([addCleanOptions,addInOutputOption], progdoc=__doc__)
    (options, entries) = optionParser()
    
    if (options.onlyhead):
        options.clustermode=True
       
    globalIndex = Indexer()         # I keep correspondances for all graphs between 
                                    # node id and sequence
                                     
    db = []                         # sequences are stored in a list. The indexes in the list
                                    # are corresponding to the node index in graphs
                                    
    sampleOccurrences = []          # Contains the list of count distribution per samples
                                    # The indexes in the list are corresponding to the node 
                                    # index in graphs
                                    
    graph = UndirectedGraph("error",indexer=globalIndex)
    pcr= {}                         # For each sample store a set of node id occuring in this PCR
    
    if options.graph is not None:
        graphfile=open(options.graph,"w")
    else:
        graphfile=None
    
    for s in entries:
        nodeid = globalIndex.getIndex(s.id)
        db.append(s)

        if options.sample is None:
            sample = {"XXX":s['count'] if 'count' in s else 1}
        else:
            sample = s[options.sample]
            
        sampleOccurrences.append(sample)
            
        graph.addNode(s.id,shape='circle')

        for sp in sample:
            spcr = pcr.get(sp,set())
            spcr.add(nodeid)
            pcr[sp]=spcr
        
    
    writer = sequenceWriterGenerator(options)            
    
    ldb = len(db)    
    digit = int(math.ceil(math.log10(ldb)))
    aligncount = ldb*(ldb+1)/2
    edgecount = 0
    print >>sys.stderr
    
    header = "Alignment  : %%0%dd x %%0%dd -> %%0%dd " % (digit,digit,digit)
    progressBar(1,aligncount,True,"Alignment  : %s x %s -> %s " % ('-'*digit,'-'*digit, '0'*digit))
    pos=1
    aligner = LCS()
    
    #
    # We build the global levenstein graph
    # Two sequences are linked if their distances are below
    # options.dist (usually 1)
    #
    
    for i in xrange(ldb):

        aligner.seqA = db[i]
        li = len(db[i])
        
        for j in xrange(i+1,ldb):
            progressBar(pos,aligncount,head=header % (i,j,edgecount))
            pos+=1
            
            lj = len(db[j])
            
            lm = max(li,lj)
            lcsmin = lm - options.dist
            
            if isLCSReachable(db[i],db[j],lcsmin):
                aligner.seqB=db[j]
                ali = aligner()
                llcs=ali.score
                lali = len(ali[0])
                obsdist = lali-llcs
                if obsdist >= 1 and obsdist <= options.dist:
                    graph.addEdge(index1=i, index2=j)
                    edgecount+=1               
            
    print >>sys.stderr

    header = "Clustering sample  : %20s "
    samplecount = len(pcr)
    
    print >>sys.stderr,"Sample count : %d" % samplecount

    
    progressBar(1,samplecount,True,head=header % "--")
    isample=0
    
    #
    # We iterate through all PCR
    #
    
    for sample in pcr:
        
        isample+=1
        progressBar(isample,samplecount,head=header % sample)
        
        seqids   = list(pcr[sample])
        nnodes    = len(seqids)
        
        #
        # We build a sub DAG for each sample
        #
        
        sub = DAG(sample,indexer=globalIndex)
        counts = []
        
        for i in seqids:
            c=sampleOccurrences[i][sample]
            sub.addNode(index=i,count=c,oricount=c)
            counts.append(c)

        order  = map(None,counts,seqids)
        order.sort(key=lambda a : a[0],reverse=True)
        
        for j in xrange(nnodes - 1):
            count1,index1 = order[j]
            for k in xrange(j+1,nnodes):
                count2,index2 = order[k]
                r = float(count2)/float(count1)
                if r <= options.ratio and graph.hasEdge(index1=index1,index2=index2):
                    sub.addEdge(index1=index1, 
                                index2=index2,
                                ratio=r,
                                arette = "%d -> %d" % (count1,count2))
                    
        if (options.clustermode):
            # We transfer the weight of errors to the parent sequence
            # when an error has several parents, we distribute its
            # weight to each of its parent proportionally to the parent 
            # weight. 
                        
            leaves = sub.getLeaves()
            
            while leaves:
                for l in leaves:
                    l['color']='red'
                    l['done']=True
                    c = l['count']
                    p = l.getParents()
                    pc = [float(x['count']) for x in p]
                    ps = sum(pc)
                    pc = [x / ps * c for x in pc]
                    for i in xrange(len(pc)):
                        p[i]['count']+=int(round(pc[i]))
                
                    leaves = [x for x in sub.nodeIterator(lambda n : 'done' not in n and not [y for y in n.neighbourIterator(lambda  k : 'done' not in k)])]
            
    
            
            # Just clean the done tag set by the precedent loop
            
            for x in sub.nodeIterator():
                del x["done"]
                
        
        # Annotate each sequences with its more probable parent.
        # When a sequence has several potential parents, it is
        # annotated with the heaviest one
        
        heads = sub.getRoots()
        sons  = []
        for h in heads:
            h['cluster']=h.label
            
            if (options.clustermode):
                h['head']   =True
            
            sons.extend(h.neighbourIterator(lambda  k : 'cluster' not in k))

            #
            # Annotate the corresponding sequence
            #
            
            seq = db[h.index]
            
            # sequence at least head in one PCR get the obiclean_head
            # attribute
            seq['obiclean_head']=True
            
            if (options.clustermode):
                # Store for each sample the cluster center related to
                # this sequence 
                if "obiclean_cluster" not in seq:
                    seq['obiclean_cluster']={}
                seq['obiclean_cluster'][sample]=h.label
            
            
                # Store for each sample the count of this sequence plus 
                # the count of all its related
                if "obiclean_count" not in seq:
                    seq["obiclean_count"]={}
                
                seq["obiclean_count"][sample]=h['count']
            
            if "obiclean_status" not in seq:
                seq["obiclean_status"]={}
                
            if len(h) > 0:
                seq["obiclean_status"][sample]='h'
            else:
                seq["obiclean_status"][sample]='s'

        
        heads=sons
        sons  = []
        
        while heads:
            for h in heads:
                parents = h.getParents()
                maxp=None
                for p in parents:
                    if maxp is None or p['count']>maxp['count']:
                        maxp=p
                        
                if 'cluster' in maxp:
                    cluster = maxp['cluster']
                    h['cluster']=cluster
                    sons.extend(h.neighbourIterator(lambda  k : 'cluster' not in k))
                    
                    #
                    # Annotate the corresponding sequence
                    #
                    
                    seq = db[h.index]
                    if (options.clustermode):
                        if "obiclean_cluster" not in seq:
                            seq['obiclean_cluster']={}
                        seq['obiclean_cluster'][sample]=cluster
                        
                        if "obiclean_count" not in seq:
                            seq["obiclean_count"]={}
                        seq["obiclean_count"][sample]=h['count']
    
                if "obiclean_status" not in seq:
                    seq["obiclean_status"]={}
                    
                seq["obiclean_status"][sample]='i'

            heads=sons
            sons  = []
            
        if graphfile is not None:
            print >>graphfile,sub

    print >>sys.stderr

    seqcount = len(db)
    sc=0
    progressBar(1,seqcount,True,head="Writing sequences")
        
    for node in db:
        sc+=1
        progressBar(sc,seqcount,head="Writing sequences")
        
        if (not options.onlyhead or 'obiclean_head' in node):
            status = node["obiclean_status"]
            i=0
            h=0
            s=0
            for sample in status:
                st=status[sample]
                if st=="i":
                    i+=1
                elif st=="s":
                    s+=1
                else:
                    h+=1
            node['obiclean_headcount']=h
            node['obiclean_internalcount']=i
            node['obiclean_singletoncount']=s
            node['obiclean_samplecount']=s+i+h
            
            if 'obiclean_head' not in node:
                node['obiclean_head']=False
            
#            if (not options.clustermode):
#                del node["obiclean_status"]
            
            writer(node)
                
    print >>sys.stderr
            
            
            

            
    

