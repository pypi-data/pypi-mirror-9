The *fasta* format
==================

.. _classical-fasta:


The *fasta* format is certainly the most widely used sequence file format. 
This is certainly due to its great simplicity. It was originally created 
for the Lipman and Pearson `FASTA program`_. OBITools use in more
of the classical :ref:`fasta <classical-fasta>` format an
:ref:`extended version <obitools-fasta>` of this format where structured 
data are included in the title line.

In *fasta* format a sequence is represented by a title line beginning with a **>** character and
the sequences by itself following the :doc:`iupac <iupac>` code. The sequence is usually split other 
severals lines of the same length (expect for the last one) ::


    >my_sequence this is my pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT
 

This is no special format for the title line excepting that this line should be unique.
Usually the first word following the **>** character is considered as the sequence identifier.
The end of the title line corresponding to a description of the sequence.

Several sequences can be concatenated in a same file. The description of the next sequence
is just pasted at the end of the record of the previous one ::


    >sequence_A this is my first pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT
    >sequence_B this is my second pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT
    >sequence_C this is my third pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT


.. _`FASTA program`: http://www.ncbi.nlm.nih.gov/pubmed/3162770?dopt=Citation