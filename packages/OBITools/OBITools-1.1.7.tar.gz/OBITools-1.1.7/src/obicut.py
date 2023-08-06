#!/usr/local/bin/python
'''
:py:mod:`obicut`: trims sequences
=================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obicut` is a command that trims sequence objects based on two integer 
values: the ``-b`` option gives the first position of the sequence to be kept, 
and the ``-e`` option gives the last position to be kept. Both values can be 
computed using a python expression.

  *Example:*
    
    .. code-block:: bash
        
          > obicut -b 50 -e seq_length seq1.fasta > seq2.fasta
    
    Keeps only the sequence part from the fiftieth position to the end.

  *Example:*
    
    .. code-block:: bash
        
          > obicut -b 50 -e seq_length-50 seq1.fasta > seq2.fasta
    
    Trims the first and last 50 nucleotides of the sequence object.
'''

from obitools.format.options import addInOutputOption, sequenceWriterGenerator

from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions, sequenceFilterIteratorGenerator

from obitools.options.bioseqcutter import addSequenceCuttingOptions, cutterIteratorGenerator

if __name__=='__main__':  # @UndefinedVariable


    optionParser = getOptionManager([addSequenceCuttingOptions,
                                     addSequenceFilteringOptions,
                                     addInOutputOption],
                                    progdoc=__doc__)  # @UndefinedVariable
    (options, entries) = optionParser()

    filter = sequenceFilterIteratorGenerator(options)
    cutter = cutterIteratorGenerator(options)

    writer = sequenceWriterGenerator(options)

    for seq in cutter(filter(entries)):
        writer(seq)
        