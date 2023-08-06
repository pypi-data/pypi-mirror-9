.. automodule:: obisilva
   
   :py:mod:`obisilva` specific options
   -------------------------------------  

   .. cmdoption::  -s , --ssu  
   
        Specify that you are interested in the **SSU** database.
                   
    *Example:*

    		.. code-block:: bash
    
       			> obisilva --ssu --parc

		This download and format into an ecoPCR database the latest version of the **SSUParc** database of **Silva**.

   .. cmdoption::  -l, --lsu   
   
        Specify that you are interested in the **LSU** database.

    *Example:*
    
    		.. code-block:: bash
    
       			> obisilva --ssu --parc

		This download and format into an ecoPCR database the latest version of the **LSUParc** database of **Silva**.
   
             
   .. cmdoption::  -p , --parc  
   
		Specify that you are interested in the **Parc** (complete) version of the **Silva** database.


   .. cmdoption::  -r , --ref  
   
		Specify that you are interested in the **Reference** (cleaned to keep only high quality sequences) 
		version of the **Silva** database.

   .. cmdoption::  -n , --nr  
   
		Specify that you are interested in the **Non redundant** version of the **Silva** database.
		just a version of the to closely related sequence is kept in this version of the database
		
		.. warning::
			Non redundant version of **Silva** exists only for the SSU sequences 
			in its **Reference** and  **Truncated** version

   .. cmdoption::  -t , --trunc 
   
		Specify that you are interested in the **Truncated** (limited to the rDNA element without flanked regions) 
		version of the **Silva** database.

   .. cmdoption::  --local=<DIRNAME> 
   
		Specify you have already downloaded a copy of the **Silva** database located at the following URL
		`<http://www.arb-**Silva**.de/no_cache/download/archive/current/Exports/>`_
		
    *Example:*

    		.. code-block:: bash
    
       			> obisilva --ssu --parc --local=**Silva**Dir
       			
       		This format the **SSUParc** version of the **Silva** database pre-downloaded in the `**Silva**Dir` directory.
		

   .. include:: ../optionsSet/defaultoptions.txt
   
   