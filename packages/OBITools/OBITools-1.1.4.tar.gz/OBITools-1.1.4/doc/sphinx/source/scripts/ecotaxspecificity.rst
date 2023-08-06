.. automodule:: ecotaxspecificity
   
   :py:mod:`ecotaxspecificity` specific options
   --------------------------------------------

   .. cmdoption::  -e INT, --errors=<INT>   
   
        Two sequences are considered as different if they have INT or more
        differences (default: 1).
 
    *Example:*
    
            .. code-block:: bash
    
                > ecotaxspecificity -d my_ecopcr_database -e 5 seq.fasta
     
        This command considers that two sequences with less than 5 differences 
        correspond to the same barcode.
   
   .. include:: ../optionsSet/taxonomyDB.txt

   .. include:: ../optionsSet/inputformat.txt
   
   .. include:: ../optionsSet/defaultoptions.txt
   
   :py:mod:`ecotaxspecificity` used sequence attribute
   ---------------------------------------------------
    
      
           - :doc:`taxid <../attributes/taxid>`
   
