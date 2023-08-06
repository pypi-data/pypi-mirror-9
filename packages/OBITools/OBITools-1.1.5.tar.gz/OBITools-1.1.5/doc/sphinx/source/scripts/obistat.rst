.. automodule:: obistat
   
   :py:mod:`obistat` specific options
   ----------------------------------  

   .. cmdoption::  -c <KEY>, --category-attribute=<KEY>   
   
        Attribute used to categorize the sequence records. Several ``-c`` options can be combined. 
 
        .. TIP:: The ``<KEY>`` can be simply the key of an attribute, or a *Python* expression
                 similarly to the ``-p`` option of :py:mod:`obigrep`.

    *Example:*
    
    		.. code-block:: bash
    
       			> obistat -c sample -c seq_length seq.fasta
     
		This command prints the number of sequence records and total count for each combination of
		sample and sequence length.
   
             
   .. cmdoption::  -m <KEY>, --min=<KEY>  
   
		Computes the minimum value of attribute <KEY> for each category. 

   	*Example:*
        
    		.. code-block:: bash
    
       			> obistat -c sample -m seq_length seq.fastq
    
		This command computes the minimum sequence length observed for each sample.

   .. cmdoption::  -M <KEY>, --max=<KEY>  
   
		Computes the maximum value of attribute <KEY> for each category. 

   	*Example:*
        
    		.. code-block:: bash
    
       			> obistat -c sample -M seq_length seq.fastq
    
		This command computes the maximum sequence length observed for each sample.

   .. cmdoption::  -a <KEY>, --mean=<KEY>  

		Computes the mean value of attribute <KEY> for each category. 
	
	*Example:*
    
    		.. code-block:: bash
    
       			> obistat -c sample -a seq_length seq.fastq

		This command computes the mean sequence length observed for each sample.

	.. cmdoption::  -v <KEY>, --variance=<KEY>  

		Computes the variance of attribute <KEY> for each category. 
	
	*Example:*
    
    		.. code-block:: bash
    
       			> obistat -c genus_name -v reverse_error seq.fastq
	    
		This command computes the variance of the number of errors observed in the reverse primer for each genus.
			
	.. cmdoption::  -s <KEY>, -std-dev=<KEY>  
	   
		Computes the standard deviation of attribute <KEY> for each category. 
	
	*Example:*
    
    		.. code-block:: bash
    
       			> obistat -c genus_name -s reverse_error seq.fastq
	    
		This command computes the standard deviation of the number of errors observed in the reverse primer for each genus.


   .. include:: ../optionsSet/inputformat.txt

   .. include:: ../optionsSet/taxonomyDB.txt
   
   .. include:: ../optionsSet/defaultoptions.txt
   
   :py:mod:`obistat` used sequence attribute
   -----------------------------------------
   
              - :doc:`count <../attributes/count>`
     
   