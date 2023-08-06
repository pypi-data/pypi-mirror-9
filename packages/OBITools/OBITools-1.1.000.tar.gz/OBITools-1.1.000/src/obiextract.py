#!/usr/local/bin/python
'''
:py:mod:`obiextract`: extract samples from a dataset 
====================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

The :py:mod:`obiextract` command extract a subset of samples from a complete
dataset.

Extracted sample names can be specified or by indicating their names using option
on the command line or by indicating a file name containing a sample name per line

The count attribute of the sequence and the slot describing distribution of the sample
occurrences among samples are modified according to the selected samples.

A sequence not present in at least one of the selected samples is not conserved in the 
output of :py:mod:`obiextract`.

'''
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager

def addExtractOptions(optionManager):
    optionManager.add_option('-s','--sample',
                             action="store", dest="sample",
                             metavar="<TAGNAME>",
                             type="str",
                             default="merged_sample",
                             help="Tag containing sample descriptions")
     
    optionManager.add_option('-e','--extract',
                             action="append",
                             type="string",
                             dest="sample_list",
                             default=[],
                             metavar="<SAMPLE_NAME>",
                             help="which <SAMPLE_NAME> have to be extracted")

    optionManager.add_option('-E','--extract-list',
                             action="store", dest="sample_file",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="File name where a list of sample is stored")
     

def selectSamples(entry,key,samples):
    newsamples = {}
    oldsamples = entry.get(key,{})
    for k in samples:
        if k in oldsamples:
            newsamples[k]=oldsamples[k]
    s = sum(newsamples.values())
    if s > 0:
        entry['count']=s 
        entry[key]=newsamples
        if len(newsamples)==1 and key[0:7]=='merged_':
            entry[key[7:]]=newsamples.keys()[0]
    else:
        entry=None
        
    return entry
        

if __name__ == '__main__':
    optionParser = getOptionManager([addExtractOptions,addInOutputOption],progdoc=__doc__)
    
    (options, entries) = optionParser()
    
    if options.sample_file is not None:
        s = [x.strip() for x in open(options.sample_file)]
        options.sample_list.extend(s)
        
    writer = sequenceWriterGenerator(options)
    
    print options.sample_list
    
    for seq in entries:
        seq = selectSamples(seq,options.sample,options.sample_list)
        if seq is not None:
            writer(seq)
            
