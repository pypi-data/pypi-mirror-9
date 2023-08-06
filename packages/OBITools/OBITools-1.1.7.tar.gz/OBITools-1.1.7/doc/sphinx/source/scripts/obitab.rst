.. automodule:: obitab
   
   
    :py:mod:`obitab` specific options
    ---------------------------------   

    .. cmdoption::   -n <NOT AVAILABLE STRING>, --na-string=<NOT AVAILABLE STRING>
   
                   String written in the table for the not available values 
                   (default value ``NA``).
                   
    .. cmdoption::    --output-field-separator=<STRING>
   
                   Field separator for the tabular file 
                   (default value ``TAB``).
                   
    .. cmdoption::    -o, --output-seq      
   
                   Adds an extra column at the end of the table for 
                   the sequence itself.
                   
    .. cmdoption::    -d, --no-definition   
   
                   Removes column containing the sequence definition in
                   the output tab file.
                   
    .. cmdoption::    -a <KEY>, --omit-attribute=<KEY>
   
                   Attributes whose key is in this list will not be printed in 
                   the output tab file.  
                        
    .. include:: ../optionsSet/inputformat.txt

    .. include:: ../optionsSet/defaultoptions.txt



    Example
    -------
        
        .. code-block:: bash
            
              > obitab -d -o seq1.fasta > seq1.txt
        
        Reformats all sequence records present in the ``seq1.fasta`` file 
        into a tabular file without outputing the sequence definition but
        with an extra column containing the sequence itself. The result is
        stored in the ``seq1.txt`` file.