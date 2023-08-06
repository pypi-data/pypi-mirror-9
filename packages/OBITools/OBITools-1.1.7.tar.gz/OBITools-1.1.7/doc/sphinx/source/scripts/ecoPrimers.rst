:py:mod:`ecoPrimers`: new barcode markers and primers
=====================================================

Authors: 	Eric Coissac <eric.coissac@metabarcoding.org> and Tiayyba Riaz <tiayyba.riaz@metabarcoding.org>
				
:py:mod:`ecoPrimers` designs the most efficient barcode markers and primers, based 
on a set of reference sequence records, and according to specified parameters.

Reference
---------
        
    Riaz T, Shehzad W, Viari A, Pompanon F, Taberlet P, Coissac E (2011) ecoPrimers: inference of new DNA 
    barcode markers from whole genome sequence analysis. Nucleic Acids Research, 39, e145.
    
       

:py:mod:`ecoPrimers` specific options
-------------------------------------   

   .. cmdoption:: -d <filename>   
   
        Filename containing the reference sequence records used for designing the barcode 
        markers and primers (see :doc:`obiconvert <./obiconvert>` for a description
        of the database format).
        
   .. WARNING:: This option is compulsory.
                       
  
   .. cmdoption:: -e <INTEGER>  
   
         Maximum number of errors (mismatches) allowed per primer (default: 0).
                               
  
   .. cmdoption::  -l <INTEGER>   
   
		 Minimum length of the barcode, excluding primers.
                       
  
   .. cmdoption::  -L <INTEGER>   
   
		 Maximum length of the barcode, excluding primers.
                       
  
   .. cmdoption::  -r <TAXID>   
   
         Defines the example sequence records (example dataset). Only the sequences of the corresponding 
         taxonomic group identified by its ``TAXID`` are taken into account for designing the barcodes and 
         the primers. The ``TAXID`` is an integer that can be found either in the NCBI taxonomic database, 
         or using the :doc:`ecofind <ecofind>` program.
  
   .. cmdoption::  -i <TAXID>   
   
		 Defines the counterexample sequence records (counterexample dataset). The barcodes and primers 
		 will be selected in order to avoid the counterexample taxonomic group identified by its ``TAXID``.
                       
  
   .. cmdoption::  -E <TAXID>   
   
		 Defines an counterexample taxonomic group (identified by its ``TAXID``) within the example
		 dataset.
                       
  
   .. cmdoption::  -c   
   
			Considers that the sequences of the database are circular (e.g. mitochondrial
			or chloroplast DNA).
                       
  
   .. cmdoption::  -3 <INTEGER>   
   
			Defines the number of nucleotides on the 3' end of the primers that must have a strict match
			with their target sequences.


   .. cmdoption::  -q <FLOAT>   
   
			Defines the strict matching quorum, i.e. the proportion of the sequence records in which a 
			strict match between the primers and their targets occurs (default: 0.7)
                       
  
   .. cmdoption::  -s <FLOAT>  
   
			Defines the sensitivity quorum, i.e. the proportion of the example sequence records that
			must fulfill the specified parameters for designing the barcodes and the primers.
                       
  
   .. cmdoption::  -x <FLOAT>   
   
			Defines the false positive quorum, i.e. the maximum proportion of the counterexample 
			sequence records that fulfill the specified parameters for designing the barcodes and 
			the primers.
                       
  
   .. cmdoption::  -t <TAXONOMIC_LEVEL>
   
			Defines the taxonomic level that is considered for evaluating the barcodes and primers in 
			the output of :py:mod:`ecoPrimers`. The default taxonomic level is the species level. When 
			using a taxonomic database builts from a :doc:`NCBI taxonomy dump files <../taxdump>`, the 
			other possible taxonomic levels are genus, family, order, class, phylum, kingdom, and 
			superkingdom.
                       
  
   .. cmdoption::  -D   
   
			Sets the double strand mode.
                       
  
   .. cmdoption::  -S   
   
			Sets the single strand mode.
                       
  
   .. cmdoption::  -O <INTEGER>
   
			Sets the primer length (default: 18).
                       
  
   .. cmdoption::  -m <1|2>  
   
			Defines the method used for estimating the *Tm* (melting temperature) between 
			the primers and their corresponding target sequences (default: 1).
			
				1 SantaLucia method (SantaLucia J (1998) A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics. PNAS, 95, 1460-1465).
				
				2 Owczarzy method (Owczarzy R, Vallone PM, Gallo FJ *et al.* (1997) Predicting sequence-dependent melting stability of short duplex DNA oligomers. Biopolymers, 44, 217-239).
				               
  
   .. cmdoption::  -a <FLOAT>
   
			Salt concentration used for estimating the *Tm* (default: 0.05).
                       
  
   .. cmdoption::  -U
   
			No multi match of a primer on the same sequence record.
                       
  
   .. cmdoption::  -R <TEXT>
   
			Defines the reference sequence by indicating its identifier in the database.
                       
  
   .. cmdoption::  -A
   
			Prints the list of all identifiers of sequence records in the database.
                       
  
   .. cmdoption::  -f
   
			Remove data mining step during strict primer identification.
                       
  
   .. cmdoption::  -v
   
			Stores statistic file about memory usage during strict primer identification.
                       
  
   .. cmdoption::  -h   
   
            Print help.
                       
  
  
Output file
-----------
	
		The output file contains several columns, with '|' as separator, and describes 
		the characteristics of each barcode and its associated primers.
			
		column 1: serial number
			
		column 2: sequence of primer 1
			
		column 3: sequence of primer 2
			
		column 4: *Tm* (melting temperature) of primer 1, without mismatch
			
		column 5: lowest *Tm* of primer 1 against example sequence records
			
		column 6: *Tm* of primer 2, without mismatch
			
		column 7: lowest *Tm* of primer 2 against example sequence records
			
		column 8: number of C or G in primer 1
			
		column 9: number of C or G in primer 2
			
		column 10: GG (*Good-Good*) means that both primer are specific to the example dataset,
		           GB or BG (*Good-Bad* or *Bad-Good*) means that only one of the two primers
		           is specific to the example dataset
			
		column 11: number of sequence records of the example dataset that are properly amplified according to the specified parameters
			
		column 12: proportion of sequence records of the example dataset that are properly amplified according to the specified parameters
			
		column 13: yule-like output 
			
		column 14: number of taxa of the example dataset that are properly amplified according to the specified parameters
			
		column 15: number of taxa of the counterexample dataset that are properly amplified according to the specified parameters
			
		column 16: proportion of taxa of the example dataset that are properly amplified according to the specified parameters (*Bc* index)
			
		column 17: number of taxa of the example dataset that are properly identified
			
		column 18: proportion of taxa of the example dataset that are properly identified (*Bs* index)
			
		column 19: minimum length of the barcode in base pairs for the example sequence records (excluding primers)
			
		column 20: maximum length of the barcode in base pairs for the example sequence records (excluding primers)
			
		column 21: average length of the barcode in base pairs for the example sequence records(excluding primers)

  
  
Examples
--------
	
	*Example 1:*
	    
	    		.. code-block:: bash
	    
	       			>  ecoPrimers -d mydatabase -e 3 -l 50 \
	       			   -L 800 -r 2759 -3 2 > mybarcodes.ecoprimers
	     
			Launches a search for barcodes and corresponding primers on mydatabase (see 
			:doc:`obiconvert <./obiconvert>` for a description of the database format), with a maximum
			of three mismatches for each primer. The minimum and maximum barcode lengths (excluding 
			primers) are 50 bp and 800 bp, respectively. The search is restricted to the taxonomic 
			group identified by its *taxid* (2759 corresponds to the Diatoma). The two last 
			Nucleotides on the 3' end of the primers must have a perfect match with their target sequences. 
			The results are saved in the mybarcodes.ecoprimers file.
	   
	
	
	*Example 2:*
	    
	    		.. code-block:: bash
	    
	       			> ecoPrimers -d mydatabase -e 2 -l 30 -L 120 \
	       			  -r 7742 - i 2 -E 9604 -3 2 > mybarcodes.ecoprimers
	     
			Launches a search for barcodes and corresponding primers on mydatabase (see :doc:`obiconvert <./obiconvert>` 
			for a description of the database format), with a maximum of two mismatches for each primer. The minimum and 
			maximum barcode lengths (excluding primers) are 30 bp and 120 bp, respectively. The search is 
			restricted to the Vertebrates, excluding Bacteria and Hominidae (7742, 2, and 9604 corresponds to 
			the `TAXID` of Vertebrates, Bacteria, and Hominidae, respectively. The two last nucleotides on 
			the 3' end of the primers must have a perfect match with their target sequences. The results 
			are saved in the mybarcodes.ecoprimers file.
			

	

