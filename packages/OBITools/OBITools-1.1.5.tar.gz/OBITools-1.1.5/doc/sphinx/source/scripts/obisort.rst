.. automodule:: obisort
   
   :py:mod:`obisort` specific options
   ---------------------------------- 

   .. cmdoption::  -k <KEY>, --key=<KEY>   
   
        Attribute used to sort the sequence records. 
 
    *Example:*
    
    		.. code-block:: bash
    
       			> obisort -k count seq1.fasta > seq2.fasta
     
		Sorts the sequence records of file ``seq1.fasta`` according to their `count` 
		(numeric order) and prints the results in the ``seq2.fasta`` file.
   
   .. cmdoption::  -r, --reverse   
   
		Sorts in reverse order. 

   	*Example:*
        
    		.. code-block:: bash
    
       			> obisort -r -k count seq1.fastq > seq2.fastq
    
		Sorts the sequence records of file ``seq1.fasta`` according to their `count` 
		(reverse numeric order) and prints the results in the ``seq2.fasta`` file.

   .. include:: ../optionsSet/inputformat.txt

   .. include:: ../optionsSet/defaultoptions.txt
   
