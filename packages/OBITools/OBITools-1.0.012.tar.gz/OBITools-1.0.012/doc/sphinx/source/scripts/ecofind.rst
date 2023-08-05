:py:mod:`ecofind`: querying a taxonomic database
================================================

:py:mod:`ecofind` retrive taxonomic information from taxonomic database 
given either a *taxid* or a regular expression patterns.
   
:py:mod:`ecofind` specific options
----------------------------------   

   .. cmdoption::   -d <filename>   
   
        Filename containing the database used for the *in silico* PCR. The database
        must be in the ``ecoPCR format`` (see :doc:`obiconvert <./obiconvert>`). 
        
        .. WARNING:: This option is compulsory.
                       
   .. cmdoption::   -a
   
        Enable the search on all alternative names and not only scientific names.
    
   .. cmdoption::   -L

        List all taxonomic rank available for -r option and exit.

   .. cmdoption::  -r

        Restrict to given taxonomic rank.

   .. cmdoption::  -s

        Displays all subtree's information for the given taxid.

   .. cmdoption::  -p 
   
        Displays all parental tree's information for the given taxid.

   .. cmdoption::  -P

        Display taxonomic Path as suplementary column in output

   .. cmdoption::  -h   
   
            Print help.
                       
  
  
Output file
-----------
	
		The output file contains several columns, with '|' as separator, and describes 
		the properties of the retrieved *taxids*.
			
		column 1: the *taxid*
			
		column 2: the taxonomic rank
			
		column 3: the name (not only scientific)
			
		column 4: class name
			
		column 5: the scientific name
			
		column 6 (optional): the full taxonomic path of the *taxid*
			
  
  
Examples
--------
	
	*Example 1:*
	    
	    		.. code-block:: bash
	    
	       			>  ecofind -d mydatabase 'homo ' > homo_.tax 
	     
			Retrieve all *taxids* whose 'homo ' is contained in the associated names.
	
	*Example 2:*
	
	    		.. code-block:: bash
	    
	       			> ecofind -d mydatabase  -p 9606 -P > sapiens.info.tax
	     
			Retrieve all parents taxa of the 9606 *taxid*. The -P option add a supplementary column
			with the full path for each *taxid*.  