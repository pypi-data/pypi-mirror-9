.. automodule:: obiaddtaxids 

    :py:mod:`obiaddtaxids` specific options
    --------------------------------------- 

    .. cmdoption::  -f <FORMAT>, --format=<FORMAT>

                        Format of the sequence file. Possible formats are: 
                        
                            - ``raw``: for regular ``OBITools`` extended :doc:`fasta <../fasta>` files (default value).
                            
                            - ``UNITE``: for :doc:`fasta <../fasta>` files downloaded from the `UNITE web site <http://unite.ut.ee/>`_.
                             
                            - ``SILVA``: for :doc:`fasta <../fasta>` files downloaded from the `SILVA web site <http://www.arb-silva.de/>`_.
                                                    
    .. cmdoption::  -k <KEY>, --key-name=<KEY>

                        Key of the attribute containing the taxon name in sequence files in the ``OBITools`` extended
                        :doc:`fasta <../fasta>` format. 
                      

    .. cmdoption::  -a <ANCESTOR>, --restricting_ancestor=<ANCESTOR>

                        Enables to restrict the search of *taxids* under a specified ancestor.
                        
                        ``<ANCESTOR>`` can be a *taxid* (integer) or a key (string). 
                        
                            - If it is a *taxid*, this *taxid* is used to restrict the search for all the sequence
                              records.
                        
                            - If it is a key, :py:mod:`obiaddtaxids` looks for the ancestor *taxid* in the
                              corresponding attribute. This allows having a different ancestor restriction
                              for each sequence record.
                               
                            

    .. cmdoption::  -g <FILENAME>, --genus_found=<FILENAME>

                        File used to store sequences with a match found for the genus.
                        
                        .. CAUTION:: this option is not valid with the UNITE format.
                        

    .. cmdoption::  -u <FILENAME>, --unidentified=<FILENAME>

                        File used to store sequences with no taxonomic match found.

    .. include:: ../optionsSet/taxonomyDB.txt

    .. include:: ../optionsSet/defaultoptions.txt
    

    :py:mod:`obiaddtaxids` added sequence attribute
    -----------------------------------------------

           - :doc:`taxid <../attributes/taxid>`

