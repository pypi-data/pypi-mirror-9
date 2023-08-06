.. automodule:: ecotaxstat
   
   :py:mod:`ecotaxstat` specific options
   --------------------------------------------

   .. cmdoption::  -r TAXID, --required=<TAXID>   
   
        Taxids can be specified to focus the coverage on a smaller part of the taxonomy.
 
    *Example:*
    
            .. code-block:: bash
    
                > ecotaxstat -d my_ecopcr_database seq.ecopcr
     
        This command will print taxonomy coverage for the considered primer pair
   
   .. include:: ../optionsSet/taxonomyDB.txt

   .. include:: ../optionsSet/defaultoptions.txt
   
