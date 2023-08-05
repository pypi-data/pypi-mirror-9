.. automodule:: obitaxonomy 

    :py:mod:`obitaxonomy` specific options
    --------------------------------------- 
    

    .. cmdoption::  -a <TAXON_INFOS>, --add-taxon=<TAXON_INFOS>

                        Adds a new taxon to the taxonomy. The new taxon 
                        is described by three values separated by colons: 
                        its scientific name, its taxonomic rank, and the 
                        taxid of its first ancestor.

        *Example:*
        
            .. code-block:: bash
        
                    > obitaxonomy -d my_ecopcr_database \
                      -a 'Gentiana alpina':'species':49934
    
            Adds a taxon with the scientific name *Gentiana alpina* and the rank *species* under
            the taxon whose taxid is 49934.


    .. cmdoption::  -m <####>, --min-taxid=<####>

                        Minimum *taxid* for the newly added *taxid(s)*.

        *Example:*
        
            .. code-block:: bash
        
                    > obitaxonomy -d my_ecopcr_database -m 1000000000 \
                      -a 'Gentiana alpina':'species':49934
    
            Adds a taxon with the scientific name *Gentiana alpina* and the rank *species* under
            the taxon whose *taxid* is 49934, with a *taxid* greater than or equal to 1000000000.


    .. cmdoption::  -D <TAXID>, --delete-local-taxon=<TAXID>

                        Deletes the local taxon with the *taxid* <TAXID> from the 
                        taxonomic database. 

        *Example:*
        
            .. code-block:: bash
        
                    > obitaxonomy -d my_ecopcr_database -D 10000832
    
            Deletes the local taxon with the taxid 10000832 from the taxonomic database.


    .. cmdoption::  -s <SPECIES_NAME>, --add-species=<SPECIES_NAME>

                        Adds a new species to the taxonomy. The new species 
                        is described by its scientific name. The genus of the 
                        species must already exist in the database. 
                        The species will be added under its genus.

        *Example:*
        
            .. code-block:: bash
        
                    > obitaxonomy -d my_ecopcr_database -s 'Gentiana alpina'
    
            Adds the species with the scientific name *Gentiana alpina* under the genus *Gentiana*.

         
    .. cmdoption::  -f <TAXON_NAME>:<TAXID>, --add-favorite-name=<TAXON_NAME>:<TAXID>

                        Adds a new favorite scientific name to the taxonomy. 
                        The new name is described by two values separated by 
                        a colon: the new favorite name and the *taxid* of the taxon.

        *Example:*
        
            .. code-block:: bash
        
                    > obitaxonomy -d my_ecopcr_database \
                      -f 'Gentiana algida':50748
    
            Adds the favorite scientific name *Gentiana algida* for the *taxid* 50748 in the taxonomic database.


    .. cmdoption::  -F <FILE_NAME>, --file-name=<FILE_NAME>

                        Adds all the taxa from a sequence file in ``OBITools`` extended 
                        doc:`fasta <../fasta>` format, and eventually their ancestors to the database 
                        (see documentation). Each sequence record must contain the 
                        attribute specified by the ``-k`` option.

        *Example:*
        
            .. code-block:: bash
        
                    > obitaxonomy -d my_ecopcr_database \
                      -k my_taxon_name_key -F my_sequences.fasta
    
            Adds the taxon of each sequence record from the file ``my_sequences.fasta`` in the taxonomic 
            database, based on the scientific name contained in the ``my_taxon_name_key`` attribute.

  
    .. cmdoption::  -k <KEY_NAME>, --key-name=<KEY_NAME>

                        Works with the ``-F`` option. Defines the key of the 
                        attribute that contains the scientific name of 
                        the taxon to be added. See example above.


    .. cmdoption::  -A <ANCESTOR>, --restricting_ancestor=<ANCESTOR>

                        Works with the ``-F`` option. Can be a *taxid* (integer) or 
                        a key (string). If it is a *taxid*, this *taxid* is the 
                        default *taxid* under which the new taxon is added if 
                        none of his ancestors are specified or can be found. 
                        If it is a key, :py:mod:`obitaxonomy` looks for the 
                        ancestor *taxid* in the corresponding attribute, and the 
                        new taxon is *systematically* added under this ancestor. 
                        By default, the restricting ancestor is the root of the 
                        taxonomic tree for all the new taxa.

        *Example:*
        
            .. code-block:: bash
        
                    > obitaxonomy -d my_ecopcr_database -a 33090 \
                      -k my_taxon_name_key -F my_sequences.fasta
    
            Adds the taxon of each sequence record from the file ``my_sequences.fasta`` in the taxonomic 
            database, based on the scientific name contained in the ``my_taxon_name_key`` attribute. If
            the genus of the new taxon cannot be found, the new taxon is added under the taxon whose 
            *taxid* is 33090.


    .. cmdoption::  -p <PATH>, --path=<PATH>

                        Works with the ``-F`` option. Key of the attribute containing 
                        the taxonomic paths of the taxa if they are in the headers of 
                        the sequence records. The value contained in this attribute 
                        must be of the form 'Fungi, Agaricomycetes, Thelephorales, 
                        Thelephoraceae' with the highest ancestors first and commas 
                        between ancestors.
                             
        *Example:*
        
            .. code-block:: bash
        
                    > obitaxonomy -d my_ecopcr_database -p my_taxonomic_path_key \
                      -k my_taxon_name_key -F my_sequences.fasta
    
            Adds the taxon of each sequence record from the file ``my_sequences.fasta`` in the taxonomic 
            database, based on the scientific name contained in the ``my_taxon_name_key`` attribute. 
            Each ancestor contained in the ``my_taxonomic_path_key`` attribute is added if it does not 
            already exist, and the new taxon is added under the latest ancestor of the path.            


    .. include:: ../optionsSet/taxonomyDB.txt

    .. include:: ../optionsSet/defaultoptions.txt
