:py:mod:`ecoPCR`: *in silico* PCR
=================================

:py:mod:`ecoPCR` *in silico* PCR preserves the taxonomic information 
of the selected sequences, and allows various specified conditions for the
*in silico* amplification.

Additionally to the different options, the command requires two arguments corresponding 
to the two primers.

References
----------
        
    Bellemain E, Carlsen T, Brochmann C, Coissac E, Taberlet P, Kauserud H (2010) ITS as an environmental DNA barcode for fungi: an *in silico* approach reveals potential PCR biases BMC Microbiology, 10, 189.

    Ficetola GF, Coissac E, Zundel S, Riaz T, Shehzad W, Bessiere J, Taberlet P, Pompanon F (2010) An *in silico* approach for the evaluation of DNA barcodes. BMC Genomics, 11, 434.

   
:py:mod:`ecoPCR` specific options
---------------------------------   

   .. cmdoption::   -d <filename>   
   
        Filename containing the database used for the *in silico* PCR. The database
        must be in the ``ecoPCR format`` (see :doc:`obiconvert <./obiconvert>`). 
        
        .. WARNING:: This option is compulsory.
                       
  
   .. cmdoption::  -e <INTEGER>  
   
         Maximum number of errors (mismatches) allowed per primer (default: 0).
         See example 2 for avoiding errors on the 3' end of the primers.
                               
  
   .. cmdoption::  -l <INTEGER>   
   
			Minimum length of the *in silico* amplified DNA fragment, excluding primers.
                       
  
   .. cmdoption::  -L <INTEGER>   
   
			Maximum length of the *in silico* amplified DNA fragment, excluding primers.
                       
  
   .. cmdoption::  -r <TAXID>   
   
            Only the sequence records corresponding to the taxonomic group identified by its 
            ``TAXID`` are considered for the *in silico* PCR. The ``TAXID`` is an integer that 
            can be found either in the NCBI taxonomic database, or using the :doc:`ecofind <./ecofind>` program. 
  
   .. cmdoption::  -i <TAXID>   
    
			The sequences of the taxonomic group identified by its ``TAXID`` are not considered for 
			the *in silico* PCR.
                       
  
   .. cmdoption::  -c   
   
			Considers that the sequences of the database are circular (e.g. mitochondrial
			or chloroplast DNA).
                       
  
   .. cmdoption::  -D <INTEGER>   
   
			Keeps the specified number of nucleotides on each side of the *in silico* 
			amplified sequences, (including the amplified DNA fragment plus the two target 
			sequences of the primers).


   .. cmdoption::  -k   
   
			Print in the programme output the kingdom of the *in silico* amplified 
			sequences (default: print the superkingdom).
                       
  
   .. cmdoption::  -m <1|2>  
   
			Defines the method used for estimating the Tm (melting temperature) between 
			the primers and their corresponding target sequences (default: 1).
			
				1 SantaLucia method (SantaLucia J (1998) A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics. PNAS, 95, 1460-1465).
				
				2 Owczarzy method (Owczarzy R, Vallone PM, Gallo FJ *et al.* (1997) Predicting sequence-dependent melting stability of short duplex DNA oligomers. Biopolymers, 44, 217-239).
				
                       
   .. cmdoption::  -a <FLOAT>
   
			Salt concentration used for estimating the *Tm* (default: 0.05).
                       
  
   .. cmdoption::  -h   
   
            Print help.
                       
  
  
Output file
-----------
	
		The output file contains several columns, with '|' as separator, and describes 
		the properties of the *in silico* amplified sequences.
			
		column 1: sequence identification in the reference database (= accession number when using EMBL or GenBank for building the reference database)
			
		column 2: length of the original sequence
			
		column 3: scientific name as indicated in the reference database
			
		column 4: taxonomic rank as indicated in the reference database
			
		column 5: *taxid* of the species
			
		column 6: scientific name of the species
			
		column 7: *taxid* of the genus
			
		column 8: genus name
			
		column 9: *taxid* of the family
			
		column 10: family name
			
		column 11: *taxid* of the super kingdom (or of the kingdom if the ``-k`` option is set)
			
		column 12: super kingdom name (or kingdom name if the ``-k`` option is set)
			
		column 13: strand (D or R, corresponding to direct or reverse, respectively)
			
		column 14: target sequence of the first primer
			
		column 15: number of mismatches for the first primer
			
		column 16: target sequence of the second primer
			
		column 17: number of mismatches for the second primer
			
		column 18: length of the amplified fragment (excluding primers)
			
		column 19: sequence
			
		column 20: definition  

  
  
Examples
--------
	
	*Example 1:*
	    
	    		.. code-block:: bash
	    
	       			>  ecoPCR -d mydatabase -e 3 -l 50 -L 500 \
	       			   TCACAGACCTGTTATTGC TYTGTCTGSTTRATTSCG > mysequences.ecopcr 
	     
			Launches an *in silico* PCR on mydatabase (see :doc:`obiconvert <./obiconvert>` for a description
			of the database format), with a maximum of three mismatches for each primer. The minimum and 
			maximum amplified sequence lengths (excluding primers) are 50 bp and 500 bp, respectively. The 
			primers used are TCACAGACCTGTTATTGC and TYTGTCTGSTTRATTSCG (possibility to use 
			:doc:`IUPAC codes <../iupac>`). They amplify a short portion of the nuclear 18S gene. The 
			results are saved in the *mysequence.ecopcr* file.
	   
	
	
	*Example 2:*
	    
	    		.. code-block:: bash
	    
	       			> ecoPCR -d mydatabase -e 2  -l 80 -L 120 -D 50 -r 7742 \
	       			  TTAGATACCCCACTATG#C# TAGAACAGGCTCCTCTA#G# > mysequences.ecopcr
	     
            Launches an *in silico* PCR on mydatabase (see :doc:`obiconvert <./obiconvert>` for a description
            of the database format), with a maximum of two mismatches for each primer, but with a perfect match 
            on the last two nucleotides	of the 3' end of each primer (a perfect match can be enforced by adding 
            a '#' after the considered nucleotide). The minimum and maximum amplified sequence lengths (excluding 
            primers) are 80 bp and 120 bp, respectively. The ``-D`` option keeps 50 nucleotides on each side of 
            the *in silico* amplified sequences, (including the amplified DNA fragment plus the two target 
            sequences of the primers). The primers used	are TTAGATACCCCACTATGC and TAGAACAGGCTCCTCTAG. They 
            amplify a short portion of the mitochondrial 12S gene. The ``-r`` option restricts the search to 
            vertebrates (7742 is the :doc:`taxid <../attributes/taxid>` of vertebrates). The results are saved 
            in the ``mysequence.ecopcr`` file.


:py:mod:`ecoPCR` used sequence attributes
-----------------------------------------
   
           - :doc:`taxid <../attributes/taxid>`
      
	   
	
	   
	

