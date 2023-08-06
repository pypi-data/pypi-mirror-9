.. automodule:: obisample
   
   :py:mod:`obisample` specific options
   ------------------------------------   

   .. cmdoption::  -s ###, --sample-size ###   
   
        Specifies the size of the generated sample.
                       
            - without the ``-a`` option, sample size is expressed as the exact number of sequence 
              records to be sampled (default: number of sequence records in the input file). 
       
            - with the ``-a`` option, sample size is expressed as a fraction of the
              sequence record numbers in the input file 
              (expressed as a number between 0 and 1).
 
    *Example:*
    
    		.. code-block:: bash
    
       			> obisample -s 1000 seq1.fasta > seq2.fasta
     
		Samples randomly 1000 sequence records from the ``seq1.fasta`` file, with replacement, 
		and saves them in the ``seq2.fasta`` file.
   
   .. cmdoption::  -a, --approx-sampling   
   
                   Switches the resampling algorithm to an approximative one, 
                   useful for large files.
                   
                   The default algorithm selects exactly the number of sequence records
                   specified with the ``-s`` option. When the ``-a`` option is set, 
                   each sequence record has a probability to be selected related to the
                   ``count`` attribute of the sequence record and the ``-s`` fraction. 

   	*Example:*
        
    		.. code-block:: bash
    
       			> obisample -s 0.5 -a seq1.fastq > seq2.fastq
    
		Samples randomly half of the sequence records of the ``seq1.fastq`` file, 
		without replacement, 
		and saves them in the ``seq2.fastq`` file.

   .. cmdoption::  -w, --without-replacement   
   
                   Asks for sampling without replacement.

   	*Example:*
        
    		.. code-block:: bash

       			> obisample -s 1000 -w seq1.fasta > seq2.fasta

   		Samples randomly 1000 sequence records from the ``seq1.fasta`` file, without replacement 
   		(the input file must contain at least 1000 sequences), and saves them in the ``seq2.fasta`` file.

   .. include:: ../optionsSet/inputformat.txt

   .. include:: ../optionsSet/defaultoptions.txt

   :py:mod:`obisample` used sequence attribute
   -------------------------------------------   

           - :doc:`count <../attributes/count>`
   
