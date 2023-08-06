.. automodule:: illuminapairedend

    :py:mod:`illuminapairedend` specific options
    -------------------------------------------- 

    .. cmdoption::      -r <FILENAME>, --reverse-reads=<FILENAME>
                        
        Filename points to the file containing the reverse reads.
        
    .. cmdoption::      --index-file=<FILENAME>
        Filename  points to the file containing the illumina index reads

    .. cmdoption::      --score-min=<FLOAT>    
   
        minimum score for keeping alignment. If the alignment score is
        below this threshold both the sequences are just concatenated.
        The ``mode`` attribute is set to the value ``joined``.

    Options to specify input format
    -------------------------------
    
    .. program:: obitools

    Fastq related format
    ....................
    
    .. cmdoption::      --sanger              
    
           Input file is in :doc:`Sanger fastq nucleic format <../fastq>`  (standard
           fastq used by HiSeq/MiSeq sequencers).
    
    .. cmdoption::      --solexa              
    
           Input file is in :doc:`fastq nucleic format <../fastq>` produced by
           Solexa (Ga IIx) sequencers.

    .. include:: ../optionsSet/outputformat.txt

    .. include:: ../optionsSet/defaultoptions.txt
   
      
    :py:mod:`illuminapairedend` added sequence attributes
    -----------------------------------------------------
   
           - :doc:`ali_dir <../attributes/ali_dir>`
           - :doc:`ali_length <../attributes/ali_length>`
           - :doc:`score <../attributes/score>`
           - :doc:`score_norm <../attributes/score_norm>`
           - :doc:`mode <../attributes/mode>`
           - :doc:`pairend_limit <../attributes/pairend_limit>`
           - :doc:`sminL <../attributes/sminL>`
           - :doc:`sminR <../attributes/sminR>`
           - :doc:`seq_ab_match <../attributes/seq_ab_match>`
           - :doc:`seq_a_single <../attributes/seq_a_single>`
           - :doc:`seq_b_single <../attributes/seq_b_single>`
           - :doc:`seq_a_mismatch <../attributes/seq_a_mismatch>`
           - :doc:`seq_b_mismatch <../attributes/seq_b_mismatch>`
           - :doc:`seq_a_deletion <../attributes/seq_a_deletion>`
           - :doc:`seq_b_deletion <../attributes/seq_b_deletion>`
           - :doc:`seq_b_insertion <../attributes/seq_b_insertion>`
           - :doc:`seq_a_insertion <../attributes/seq_a_insertion>`
