.. automodule:: obiuniq


   
   :py:mod:`obiuniq` specific options
   ----------------------------------

   .. cmdoption::  -m <KEY>, --merge=<KEY>   

     Attribute to merge.

     *Example:*
    
        .. code-block:: bash

            > obiuniq -m sample seq1.fasta > seq2.fasta
    
        Dereplicates sequences and keeps the value distribution of the ``sample`` attribute
        in the new attribute ``merged_sample``.

   .. cmdoption::  -i , --merge-ids
       
     Adds a ``merged`` attribute containing the list of sequence record ids merged
     within this group.
   
   .. cmdoption::  -c <KEY>, --category-attribute=<KEY>

     Adds one attribute to the list of attributes used to define sequence groups
     (this option can be used several times).

     *Example:*
    
        .. code-block:: bash

            > obiuniq -c sample seq1.fasta > seq2.fasta
    
        Dereplicates sequences within each sample.

   .. cmdoption::  -p, --prefix
        
     Dereplication is done based on prefix matching:
        
            1. The shortest sequence of each group is a prefix of any sequence of its group
            
            2. The shortest sequence of a group is the prefix of only the sequences belonging
               to its group 


   .. include:: ../optionsSet/taxonomyDB.txt

   .. include:: ../optionsSet/inputformat.txt

   .. include:: ../optionsSet/defaultoptions.txt

   :py:mod:`obiuniq` added sequence attributes
   -------------------------------------------

      .. hlist::
           :columns: 3

           - :doc:`count <../attributes/count>`
           - :doc:`merged_* <../attributes/merged_star>`
           - :doc:`merged <../attributes/merged>`
           - :doc:`scientific_name <../attributes/scientific_name>`
           - :doc:`rank <../attributes/rank>`
           - :doc:`family <../attributes/family>`
           - :doc:`family_name <../attributes/family_name>`
           - :doc:`genus <../attributes/genus>`
           - :doc:`genus_name <../attributes/genus_name>`       
           - :doc:`order <../attributes/order>`
           - :doc:`order_name <../attributes/order_name>`
           - :doc:`species <../attributes/species>`
           - :doc:`species_name <../attributes/species_name>`

   :py:mod:`obiuniq` used sequence attribute
   -----------------------------------------

           - :doc:`taxid <../attributes/taxid>`
      