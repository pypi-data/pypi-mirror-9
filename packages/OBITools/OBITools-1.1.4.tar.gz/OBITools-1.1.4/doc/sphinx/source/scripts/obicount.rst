.. automodule:: obicount


   :py:mod:`obicount` specific options
   -----------------------------------  

   .. cmdoption::  -a, --all   

                   Prints only the sum of ``count`` attributes.
                   If a sequence has no `count` attribute, its default count is 1.

      *Example:*
    
         .. code-block:: bash
    
           > obicount -a seq.fasta
       
        For all sequence records contained in the ``seq.fasta`` file, prints only 
        the sum of ``count`` attributes.
   

   .. cmdoption::  -s, --sequence  

                   Prints only the number of sequence records.

      *Example:*
    
        .. code-block:: bash
    
           > obicount -s seq.fasta
    
        Prints only the number of sequence records contained in the ``seq.fasta`` file.

   .. include:: ../optionsSet/inputformat.txt

   .. include:: ../optionsSet/defaultoptions.txt

   :py:mod:`obicount` added sequence attribute
   -------------------------------------------  

           - :doc:`count <../attributes/count>`

