.. automodule:: oligotag
   
   :py:mod:`oligotag` specific options
   -----------------------------------  

   .. cmdoption::   -L <filename>, --oligo-list=<filename>   
   
        Filename containing a list of oligonucleotides. `oligotag` selects within this list 
        the oligonucleotides that match the specified options.
        
        .. CAUTION:: Cannot be used with the ``-s`` option.
                       
  
   .. cmdoption::  -s ###, --oligo-size=###   
   
        Size of oligonucleotides to be generated.
        
        .. CAUTION:: Cannot be used with the ``-L`` option.
        
        .. WARNING:: A size equal or greater than eight often leads to a very long 
                     computing time and requires a large amount of memory.
                       
  
   .. cmdoption::  -f ###, --family-size=###   
   
            Minimal size of the oligonucleotide family to be generated.
                       
  
   .. cmdoption::  -d ###, --distance=###   
   
			Minimal Hamming distance (number of differences) 
			between two oligonucleotides.
                       
  
   .. cmdoption::  -g ###, --gc-max=###   
   
			Maximum number of G or C in the oligonucleotides.
                       
  
   .. cmdoption::  -a <IUPAC_PATTERN>, --accepted=<IUPAC_PATTERN>   
   
			Selected oligonucleotides are constrained by the given pattern 
			(only :doc:`IUPAC <../iupac>` symbols are allowed).
                       
         .. CAUTION:: pattern length must have the same length as oligonucleotides.
  
   .. cmdoption::  -r <IUPAC_PATTERN>, --rejected=<IUPAC_PATTERN>   
   
            Selected oligonucleotides do not match the given pattern 
            (only :doc:`IUPAC <../iupac>` symbols are allowed).
                        
         .. CAUTION:: pattern length must have the same length as oligonucleotides.
  
   .. cmdoption::  -p ###, --homopolymer=###   
   
			Selected oligonucleotides do not contain any homopolymer 
			longer than the specified length.
                       
  
   .. cmdoption::  -P ###, --homopolymer-min=###   
   
			Selected oligonucleotides contain at least one homopolymer longer 
			or equal to the specified length.
                       
   
   .. cmdoption::  -T <seconde>, --timeout=<seconde>   
   
			Timeout to identify a set of oligonucleotides of required size, 
			as defined by the ``-f`` option.
                      

   .. include:: ../optionsSet/defaultoptions.txt

	
   Examples
   --------
	
	*Example 1:*
	    
	    		.. code-block:: bash
	    
	       			> oligotag -s 5 -f 24 -d 3 -g 3 -p 2 > mytags.txt 
	     
			Searches for a family of at least 24 oligonucleotides of a length of 5 nucleotides,
			with at least 3 differences among them, with a maximum of 3 C/G, and without
			homopolymers longer than 2. The resulting list of oligonucleotides is saved in
			the ``mytags.txt`` file. 
	   
	   
	*Example 2:*
	    
	    		.. code-block:: bash
	    
	       			>  oligotag -d 5 -L my_oligos.txt -f 10 -p 1 
	     
			Searches for a subset of at least 10 oligonucleotides listed in the ``my_oligos.txt`` file, with 
			at least 5 differences among them, and without homopolymers. The ``my_oligos.txt`` file must 
			contain a set of oligonucleotides of the same length, with only one oligonucleotide per line.
			The resulting list of oligonucleotides is printed on the terminal window.
	   
	
	
	*Example 3:*
	    
	    		.. code-block:: bash
	    
	       			> oligotag -s 7 -f 96 -d 3 -p 1 -r cnnnnnn > mytags.txt 
	     
			Searches for a family of at least 96 oligonucleotides of a length of 7 nucleotides,
			with at least 3 differences among them, without homopolymers, and without a ``C`` in 
			the first position. The resulting list is saved in the ``mytags.txt`` file.
	   
	   
	*Example 4:*
	    
	    		.. code-block:: bash
	    
	       			> oligotag -s 9 -f 24 -d 3 -a yryryryry > mytags.txt 
	     
			Searches for a family of at least 24 oligonucleotides of a length of 9 nucleotides,
			with at least 3 differences among them, and an alternation of pyrimidines and purines. 
			The resulting list is saved in the ``mytags.txt`` file. Because of the 
			constraints imposed by the ``-a`` option, it is possible to compute longer oligonucleotides 
			in a reasonable time.
			

   Reference
   ---------
		
   E. Coissac. Oligotag: a program for designing sets of tags for next-generation sequencing of multiplexed samples. Methods Mol Biol, 888:13-31, 2012.
	
	   
	   
	   