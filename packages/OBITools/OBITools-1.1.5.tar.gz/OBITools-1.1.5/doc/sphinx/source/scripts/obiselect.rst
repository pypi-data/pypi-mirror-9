.. automodule:: obiselect

   In each group as definied by a set of `-c` options, sequence records are ordered according
   to a score function. The `N` first sequences (`N`is selected using the `-n` option) are kept
   in the result subset of sequence records.
    
   By default the score function is a random function and one sequence record is retrieved per
   group. This leads to select randomly one sequence per group.
    

   :py:mod:`obiselect` specific options
   ------------------------------------   

   .. cmdoption::  -c <KEY>, --category-attribute=<KEY>   
   
        Attribute used to categorize the sequence records. Several ``-c`` options can be combined. 
 
        .. TIP:: The ``<KEY>`` can be simply the key of an attribute, or a *Python* expression
                 similarly to the ``-p`` option of :py:mod:`obigrep`.

    *Example:*
    
            .. code-block:: bash
    
                > obiselect -c sample -c seq_length seq.fasta
     
        This command select randomly one sequence record per sample and sequence length from
        the sequence records included in the `seq.fasta` file.
        The selected sequence records are printed on the screen.
   
   .. cmdoption:: -n <INTEGER>, --number=<INTEGER>
   
        Indicates how many sequence records per group have to be retrieved.
        If the size of the group is lesser than this `NUMBER`, the whole group
        is retrieved.
             
    *Example:*
    
            .. code-block:: bash
    
                > obiselect -n 2 -c sample -c seq_length seq.fasta
     
        This command has the same effect than the previous example except that two
        sequences are retrieved by class of sample/length.
        
   .. cmdoption:: --merge=<KEY>   

     Attribute to merge.

     *Example:*
    
        .. code-block:: bash

            > obiselect -c seq_length -n 2 -m sample seq1.fasta > seq2.fasta
    
        This command keeps two sequences per sequence length, and records how 
        many times they were observed for each sample in the new attribute 
        ``merged_sample``.

   .. cmdoption::  --merge-ids
       
     Adds a ``merged`` attribute containing the list of sequence record ids merged
     within this group.
   

   .. cmdoption:: -m, --min             
     
     Sets the function used for scoring sequence records into a group to the minimum function. 
     The minimum function is applied to the values used to define categories (see option `-c`).
     Sequences will be ordered according to the distance of their values to the minimum value.

   .. cmdoption::    -M, --max 

     Sets the function used for scoring sequence records into a group to the maximum function. 
     The maximum function is applied to the values used to define categories (see option `-c`).
     Sequences will be ordered according to the distance of their values to the maximum value.

   .. cmdoption::    -a, --mean  

     Sets the function used for scoring sequence records into a group to the mean function. 
     The mean function is applied to the values used to define categories (see option `-c`).
     Sequences will be ordered according to the distance of their values to the mean value.

   .. cmdoption::    --median  

     Sets the function used for scoring sequence records into a group to the median function. 
     The median function is applied to the values used to define categories (see option `-c`).
     Sequences will be ordered according to the distance of their values to the median value.


   .. cmdoption::    -f FUNCTION, --function=FUNCTION

     Sets the function used for scoring sequence records into a group to a user define function. 
     The user define function is declared using `Python` syntax. Attribute keys can be used as variables.
     An extra `sequence` variable representing the full sequence record is available. If option for
     loading a taxonomy database is provided, a `taxonomy` variable is also available.
     The function is estimated for each sequence record and the minimum value of this function in
     each group.
     Sequences will be ordered in each group according to the distance of their function estimation
     to the minimum value of their group.
      
  
   .. include:: ../optionsSet/inputformat.txt
   
   .. include:: ../optionsSet/taxonomyDB.txt

   .. include:: ../optionsSet/outputformat.txt

   .. include:: ../optionsSet/defaultoptions.txt
   
   :py:mod:`obiselect` added sequence attributes
   ---------------------------------------------

           - :doc:`class <../attributes/class>`
           - :doc:`distance <../attributes/distance>`
           - :doc:`merged <../attributes/merged>`
           - :doc:`class <../attributes/class>`
           - :doc:`merged_* <../attributes/merged_star>`
           - :doc:`select <../attributes/select>`

   :py:mod:`obiselect` used sequence attribute
   -------------------------------------------

           - :doc:`taxid <../attributes/taxid>`


