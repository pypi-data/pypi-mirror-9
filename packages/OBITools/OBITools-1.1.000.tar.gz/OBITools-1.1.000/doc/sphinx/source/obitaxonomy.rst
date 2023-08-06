The OBITools formatted taxonomy
===============================

Management of the taxonomy
--------------------------

Filtering and annotation steps in the processing of DNA metabarcoding sequence data are greatly 
eased by the explicit association of taxonomic information to sequences together with an easy 
access to the taxonomy. Taxonomic information, including a taxonomic identifier, can thus be 
stored in the set of attributes of each sequence record. Specifically, the `taxid` attribute 
is used by the OBITools when querying taxonomic information of a sequence record, nevertheless 
several OBITools commands can annotate sequence records with taxonomy-related attributes for 
the user's convenience. The value of the `taxid` attribute must be a unique integer referring 
unambiguously to one taxon in the taxonomic associated database (note that a taxon can be any node 
in the taxonomic tree). Although this is not mandatory, the NCBI taxonomy is a preferred source of 
taxonomic information as the OBITools provide commands to easily extract the full taxonomic 
information from it. The command `obitaxonomy` is useful to build a taxonomic database in the 
OBITools format from a dump of the NCBI taxonomic database (downloadable at the following 
URL: ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz). Moreover, the `obitaxonomy` command can 
enrich an existing taxonomy with private taxa, therefore enabling to associate sequence records to 
taxa not initially present in the reference taxonomic database. As the OBITools have access to the 
full taxonomic tree topology, they are able to inform higher taxonomic levels from a taxon identifier 
(e.g. the family, order, class, phylum, etc. corresponding to a genus) leading to efficient and 
simple annotation and querying of taxonomic information. 


