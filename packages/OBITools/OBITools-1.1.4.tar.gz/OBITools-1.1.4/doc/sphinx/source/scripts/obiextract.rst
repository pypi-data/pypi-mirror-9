.. automodule:: obiextract
   
   :py:mod:`obiextract` specific options
   -------------------------------------  

   .. cmdoption::  -s <KEY>, --sample=<KEY>  
   
                   Attribute containing sample descriptions. By default the attribute
                   name used for describing samples is set to ``merged_sample``.
                   

   .. cmdoption::  -e <SAMPLE_NAME>, --extract=<KEY>   
   
        Attribute indicating which <SAMPLE_NAME> have to be extracted. 
        Several ``-p`` options can be added for specifying several samples.
        If you want to extract a large number of samples, please refer to the ``-E``
        option described below 
 
        .. TIP:: The ``<KEY>`` can be simply the key of an attribute, or a *Python* expression
                 similarly to the ``-p`` option of :py:mod:`obigrep`.

    *Example:*
    
    		.. code-block:: bash
    
       			> obiextract -e sampleA -e sampleB allseqs.fasta > samplesAB.fasta
     
		This command extracts from the ``allseqs.fasta`` file data related to samples ``A`` and ``B``.
   
             
   .. cmdoption::  -E <FILENAME>, --extract-list=<FILENAME>  
   
		Allows for indicating a file name where a list of sample is stored. The file must be a simple
		text file with a sample name per line.

   	*Example:*
        
    		.. code-block:: bash
    
       			> obiextract -E subset.txt allseqs.fasta > subset_samples.fasta
    
		This command extracts from the ``allseqs.fasta`` file data related to samples listed in the ``subset.txt`` file.


   .. include:: ../optionsSet/inputformat.txt
   
   .. include:: ../optionsSet/outputformat.txt
    
   .. include:: ../optionsSet/defaultoptions.txt
   
   :py:mod:`obiextract` modified sequence attributes
   -------------------------------------------------

		- :doc:`count <../attributes/count>`

   :py:mod:`obiextract` used sequence attribute
   --------------------------------------------
   
		- :doc:`count <../attributes/count>`
     
   