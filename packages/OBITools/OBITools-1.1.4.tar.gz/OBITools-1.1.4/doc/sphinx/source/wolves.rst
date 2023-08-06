Wolves' diet based on DNA metabarcoding
=======================================


Here is a tutorial on how to analyze DNA metabarcoding data produced on Illumina 
sequencers using:

    - the *OBITools*
    - some basic *Unix* commands

The data used in this tutorial correspond to the analysis of four wolf scats, using the 
protocol published in Shehzad et al. (2012) for assessing carnivore diet.
After extracting DNA from the faeces, the DNA amplifications were carried out using the 
primers TTAGATACCCCACTATGC and TAGAACAGGCTCCTCTAG amplifiying the 12S-V5 region 
(Riaz et al. 2011), together with a wolf blocking oligonucleotide. 

The complete data set can be downloaded here: :download:`the tutorial dataset<../../../wolf_tutorial.zip>`


+-------------------------------------------------------------+
| Good to remember: I am working with tons of sequences       |
+-------------------------------------------------------------+
| It is always a good idea to have a look at the intermediate |
| results or to evaluate the best parameter for each step.    |
| Some commands are designed for that purpose, for example    |
| you can use :                                               |
|                                                             |
| - :doc:`obicount <scripts/obicount>` to count the number    |
|   of sequence records in a file                             |
| - :doc:`obihead <scripts/obihead>` and                      |
|   :doc:`obitail <scripts/obitail>` to view the first        |
|   or last sequence records of a file                        |
| - :doc:`obistat <scripts/obistat>` to get some basic        |
|   statistics (count, mean, standard deviation) on the       |
|   attributes (key=value combinations) in the header of each |
|   sequence record (see The `extended OBITools fasta format` |
|   in the :doc:`fasta format <fasta>` description)           |
| - any *Unix* command such as ``less``, ``awk``, ``sort``,   |
|   ``wc`` to check your files                                |
+-------------------------------------------------------------+


Data
----

The data needed to run the tutorial are the following:


- :doc:`fastq <fastq>` files resulting of a GA IIx (Illumina) paired-end (2 x 108 bp) 
  sequencing assay of DNA extracted and amplified from 
  four wolf faeces:
  
    * ``wolf_F.fastq``
    * ``wolf_R.fastq``
    
- the file describing the primers and tags used for all samples sequenced:

    * ``wolf_diet_ngsfilter.txt``
      The tags correspond to short and specific sequences added on the 5' end of each 
      primer to distinguish the different samples
    
- the file containing the reference database in a fasta format:

    * ``db_v05_r117.fasta``
      This reference database has been extracted from the release 117 of EMBL using 
      :doc:`ecoPCR <scripts/ecoPCR>`
    
- the NCBI taxonomy formatted in the :doc:`ecoPCR <scripts/ecoPCR>` format (see the 
  :doc:`obiconvert <scripts/obiconvert>` utility for details) :

    * ``embl_r117.ndx`` 
    * ``embl_r117.rdx`` 
    * ``embl_r117.tdx`` 


Step by step analysis
---------------------


Recover full sequence reads from forward and reverse partial reads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When using the result of a paired-end sequencing assay with supposedly overlapping forward
and reverse reads, the first step is to recover the assembled sequence.

The forward and reverse reads of the same fragment are *at the same line position* in the 
two fastq files obtained after sequencing. 
Based on these two files, the assembly of the forward and reverse reads is done with the 
:doc:`illuminapairedend <scripts/illuminapairedend>` utility that aligns the two reads 
and returns the reconstructed sequence.

In our case, the command is: 

.. code-block:: bash

   > illuminapairedend --score-min=40 -r wolf_R.fastq wolf_F.fastq > wolf.fastq

The :py:mod:`--score-min` option allows discarding sequences with low alignment quality. 
If the alignment score is below 40, the forward and reverse reads are not aligned but 
concatenated, and the value of the :py:mod:`mode` attribute in the sequence header is set 
to :py:mod:`joined` instead of :py:mod:`alignment`   

Remove unaligned sequence records
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Unaligned sequences (:py:mod:`mode=joined`) cannot be used. The following command allows 
removing them from the dataset:

.. code-block:: bash

   > obigrep -p 'mode!="joined"' wolf.fastq > wolf.ali.fastq

The :py:mod:`-p` requires a *python* expression. :py:mod:`mode!="joined"` means that if 
the value of the :py:mod:`mode` attribute is different from :py:mod:`joined`, the 
corresponding sequence record will be kept. 

The first sequence record of ``wolf.ali.fastq`` can be obtained using the following 
command line:

.. code-block:: bash

   > obihead --without-progress-bar -n 1 wolf.ali.fastq
   
And the result is:

.. code-block:: bash

   @HELIUM_000100422_612GNAAXX:7:119:14871:19157#0/1_CONS ali_length=61; 
   direction=left; seq_ab_match=47; sminR=40.0; seq_a_mismatch=7; seq_b_deletion=1; 
   seq_b_mismatch=7; seq_a_deletion=1; score_norm=1.89772607661; 
   score=115.761290673; seq_a_insertion=0; mode=alignment; sminL=40.0; 
   seq_a_single=46; seq_b_single=46; seq_b_insertion=0;
   ccgcctcctttagataccccactatgcttagccctaaacacaagtaattattataacaaaatcattcgccagagtgtagc
   gggagtaggttaaaactcaaaggacttggcggtgctttatacccttctagaggagcctgttctaaggaggcgg
   +
   ddddddddddddddddddddddcddddcacdddddddddddddc\d~b~~~b~~~~~~b`ryK~|uxyXk`}~ccBccBc
   ccBcBcccBcBccccccc~~~~b|~~xdbaddaaWcccdaaddddadacddddddcddadbbddddddddddd



Assign each sequence record to the corresponding sample/marker combination
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each sequence record is assigned to its corresponding sample and marker using the data
provided in a text file (here ``wolf_diet_ngsfilter.txt``). This text file contains one 
line per sample, with the name of the experiment (several experiments can be included in 
the same file), the name of the tags (for example: ``aattaac`` if the same tag has been 
used on each extremity of the PCR products, or ``aattaac:gaagtag`` if the tags were 
different), the sequence of the forward primer, the sequence of the reverse primer, the 
letter ``T`` or ``F`` for sample identification using the forward primer and tag only or 
using both primers and both tags, respectively (see :doc:`ngsfilter  <scripts/ngsfilter>` 
for details).

.. code-block:: bash

   > ngsfilter -t wolf_diet_ngsfilter.txt -u unidentified.fastq wolf.ali.fastq > \
     wolf.ali.assigned.fastq

This command creates two files:

- ``unidentified.fastq`` containing all the sequence records that were not assigned to a 
  sample/marker combination

- ``wolf.ali.assigned.fastq`` containing all the sequence records that were properly 
  assigned to a sample/marker combination

Note that each sequence record of the ``wolf.ali.assigned.fastq`` file contains only the 
barcode sequence as the sequences of primers and tags are removed by the 
:doc:`ngsfilter <scripts/ngsfilter>` program. Information concerning the experiment, 
sample, primers and tags is added as attributes in the sequence header.

For instance, the first sequence record of ``wolf.ali.assigned.fastq`` is:

.. code-block:: bash

   @HELIUM_000100422_612GNAAXX:7:119:14871:19157#0/1_CONS_SUB_SUB status=full; 
   seq_ab_match=47; sminR=40.0; ali_length=61; tail_quality=67.0; 
   reverse_match=tagaacaggctcctctag; seq_a_deletion=1; sample=29a_F260619; 
   forward_match=ttagataccccactatgc; forward_primer=ttagataccccactatgc; 
   reverse_primer=tagaacaggctcctctag; sminL=40.0; forward_score=72.0; 
   score=115.761290673; seq_a_mismatch=7; forward_tag=gcctcct; seq_b_mismatch=7; 
   experiment=wolf_diet; mid_quality=69.4210526316; avg_quality=69.1045751634; 
   seq_a_single=46; score_norm=1.89772607661; reverse_score=72.0; 
   direction=forward; seq_b_insertion=0; seq_b_deletion=1; seq_a_insertion=0; 
   seq_length_ori=153; reverse_tag=gcctcct; seq_length=99; mode=alignment; 
   head_quality=67.0; seq_b_single=46; 
   ttagccctaaacacaagtaattattataacaaaatcattcgccagagtgtagcgggagtaggttaaaactcaaaggact
   tggcggtgctttataccctt
   +
   cacdddddddddddddc\d~b~~~b~~~~~~b`ryK~|uxyXk`}~ccBccBcccBcBcccBcBccccccc~~~~b|~~
   xdbaddaaWcccdaadddda





Dereplicate reads into uniq sequences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The same DNA molecule can be sequenced several times. In order to reduce both file size 
and computations time, and to get easier interpretable results, 
it is convenient to work with unique *sequences* instead of *reads*. To *dereplicate* such 
*reads* into unique *sequences*, we use the :doc:`obiuniq <scripts/obiuniq>` command.

+-------------------------------------------------------------+
| Definition: Dereplicate reads into unique sequences         |
+-------------------------------------------------------------+
| 1. compare all the reads in a data set to each other        |
| 2. group strictly identical reads together                  |
| 3. output the sequence for each group and its count in the  |
|    original dataset (in this way, all duplicated reads are  |
|    removed)                                                 |
|                                                             |
| Definition adapted from Seguritan and Rohwer (2001)         |
+-------------------------------------------------------------+


For dereplication, we use the :doc:`obiuniq <scripts/obiuniq>` command with the `-m 
sample`. The `-m sample` option is used to keep the information of the samples of origin 
for each unique sequence.

.. code-block:: bash

   > obiuniq -m sample wolf.ali.assigned.fastq > wolf.ali.assigned.uniq.fasta

Note that :doc:`obiuniq <scripts/obiuniq>` returns a fasta file.

The first sequence record of ``wolf.ali.assigned.uniq.fasta`` is:

.. code-block:: bash

   >HELIUM_000100422_612GNAAXX:7:119:14871:19157#0/1_CONS_SUB_SUB_CMP ali_length=61; 
   seq_ab_match=47; sminR=40.0; tail_quality=67.0; reverse_match=ttagataccccactatgc; 
   seq_a_deletion=1; forward_match=tagaacaggctcctctag; forward_primer=tagaacaggctcctctag; 
   reverse_primer=ttagataccccactatgc; sminL=40.0; merged_sample={'29a_F260619': 1}; 
   forward_score=72.0; seq_a_mismatch=7; forward_tag=gcctcct; seq_b_mismatch=7; 
   score=115.761290673; mid_quality=69.4210526316; avg_quality=69.1045751634; 
   seq_a_single=46; score_norm=1.89772607661; reverse_score=72.0; direction=reverse; 
   seq_b_insertion=0; experiment=wolf_diet; seq_b_deletion=1; seq_a_insertion=0; 
   seq_length_ori=153; reverse_tag=gcctcct; count=1; seq_length=99; status=full; 
   mode=alignment; head_quality=67.0; seq_b_single=46; 
   aagggtataaagcaccgccaagtcctttgagttttaacctactcccgctacactctggcg
   aatgattttgttataataattacttgtgtttagggctaa
   
The run of :doc:`obiuniq <scripts/obiuniq>` has added two key=values entries in the header
of the fasta sequence:

   - :py:mod:`merged_sample={'29a_F260619': 1}`: this sequence have been found once in a 
     single sample called 29a_F260619
   - :py:mod:`count=1` : the total count for this sequence is 1 
   
To keep only these two ``key=value`` attributes, we can use the 
:doc:`obiannotate <scripts/obiannotate>` command:


.. code-block:: bash

   > obiannotate -k count -k merged_sample \
     wolf.ali.assigned.uniq.fasta > $$ ; mv $$ wolf.ali.assigned.uniq.fasta


The first five sequence records of ``wolf.ali.assigned.uniq.fasta`` become:

.. code-block:: bash

   >HELIUM_000100422_612GNAAXX:7:119:14871:19157#0/1_CONS_SUB_SUB_CMP merged_sample={'29a_F260619': 1}; count=1; 
   aagggtataaagcaccgccaagtcctttgagttttaacctactcccgctacactctggcg
   aatgattttgttataataattacttgtgtttagggctaa
   >HELIUM_000100422_612GNAAXX:7:108:5640:3823#0/1_CONS_SUB_SUB_CMP merged_sample={'29a_F260619': 7, '15a_F730814': 2}; count=9; 
   aagggtataaagcaccgccaagtcctttgagttttaagctattgccggtagtactctggc
   gaacaattttgttatattaattacttgtgtttagggctaa
   >HELIUM_000100422_612GNAAXX:7:97:14311:19299#0/1_CONS_SUB_SUB_CMP merged_sample={'29a_F260619': 5, '15a_F730814': 4}; count=9; 
   aagggtataaagcaccgccaagtcctttgagttttaagctcttgccggtagtactctggc
   gaataattttgttatattaattacttgtgtttagggctaa
   >HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB merged_sample={'29a_F260619': 4697, '15a_F730814': 7638}; count=12335; 
   aagggtataaagcaccgccaagtcctttgagttttaagctattgccggtagtactctggc
   gaataattttgttatattaattacttgtgtttagggctaa
   >HELIUM_000100422_612GNAAXX:7:57:18459:16145#0/1_CONS_SUB_SUB_CMP merged_sample={'26a_F040644': 10490}; count=10490; 
   agggatgtaaagcaccgccaagtcctttgagtttcaggctgttgctagtagtactctggc
   gaacattcttgtttattgaatgtttatgtttagggctaa


Denoise the sequence dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To have a set of sequences assigned to their corresponding samples does not mean that all 
sequences are *biologically* meaningful i.e. some of these sequences can contains PCR 
and/or sequencing errors, or chimeras. To remove such sequences as much as possible, we 
first discard rare sequences and then rsequence variants that likely correspond to 
artifacts.



Get the count statistics
~~~~~~~~~~~~~~~~~~~~~~~~

In that case, we use :doc:`obistat <scripts/obistat>` to get the counting statistics on 
the 'count' attribute (the count attribute has been added by the :doc:`obiuniq 
<scripts/obiuniq>` command). By piping the result in the *Unix* commands ``sort`` and 
``head``, we keep only the count statistics for the 20 lowest values of the 'count' 
attribute.

.. code-block:: bash

   > obistat -c count wolf.ali.assigned.uniq.fasta |  \  
     sort -nk1 | head -20

This print the output:

.. code-block:: bash

    count      count     total
    1          3504      3504
    2           228       456
    3           136       408
    4            73       292
    5            61       305
    6            47       282
    7            34       238
    8            27       216
    9            26       234
    10           25       250
    11           13       143
    12           14       168
    13           10       130
    14            5        70
    15            9       135
    16            8       128
    17            4        68
    18            9       162
    19            5        95
    
The dataset contains 3504 sequences occurring only once.  

 
    
Keep only the sequences having a count greater or equal to 10 and a length shorter than 80 bp
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on the previous observation, we set the cut-off for keeping sequences for further 
analysis to a count of 10. To do this, we use the :doc:`obigrep <scripts/obigrep>` 
command.
The ``-p 'count>=10'`` option means that the ``python`` expression :py:mod:`count>=10` 
must be evaluated to :py:mod:`True` for each sequence to be kept. Based on previous 
knowledge we also remove sequences with a length shorter than 80 bp (option -l) as we know 
that the amplified 12S-V5 barcode for vertebrates must have a length around 100bp.

.. code-block:: bash

   > obigrep -l 80 -p 'count>=10' wolf.ali.assigned.uniq.fasta \
       > wolf.ali.assigned.uniq.c10.l80.fasta
       
       
The first sequence record of ``wolf.ali.assigned.uniq.c10.l80.fasta`` is:

.. code-block:: bash    

   >HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB count=12335; merged_sample={'29a_F260619': 4697, '15a_F730814': 7638}; 
   aagggtataaagcaccgccaagtcctttgagttttaagctattgccggtagtactctggc
   gaataattttgttatattaattacttgtgtttagggctaa
   

Clean the sequences for PCR/sequencing errors (sequence variants)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a final denoising step, using the :doc:`obiclean <scripts/obiclean>` program, we keep 
the `head` sequences (``-H`` option) that are sequences with no variants with a count 
greater than 5% of their own count  (``-r 0.05`` option).

.. code-block:: bash

   > obiclean -s merged_sample -r 0.05 -H \
     wolf.ali.assigned.uniq.c10.l80.fasta > wolf.ali.assigned.uniq.c10.l80.clean.fasta 

The first sequence record of ``wolf.ali.assigned.uniq.c10.l80.clean.fasta`` is:

.. code-block:: bash

   >HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB 
   merged_sample={'29a_F260619': 4697, '15a_F730814': 7638}; 
   obiclean_count={'29a_F260619': 5438, '15a_F730814': 8642}; obiclean_head=True; 
   obiclean_cluster={'29a_F260619': 
   'HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB', '15a_F730814': 
   'HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB'}; 
   count=12335; obiclean_internalcount=0; obiclean_status={'29a_F260619': 'h', '15a_F730814': 'h'}; 
   obiclean_samplecount=2; obiclean_headcount=2; obiclean_singletoncount=0; 
   aagggtataaagcaccgccaagtcctttgagttttaagctattgccggtagtactctggc
   gaataattttgttatattaattacttgtgtttagggctaa

Taxonomic assignment of sequences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once denoising has been done, the next step in diet analysis is to assign the barcodes to 
the corresponding species in order to get the complete list of species associated to each 
sample.

Taxonomic assignment of sequences requires a reference database compiling all possible 
species to be identified in the sample. Assignment is then done based on sequence 
comparison between sample sequences and reference sequences.


Build a reference database
~~~~~~~~~~~~~~~~~~~~~~~~~~

One way to build the reference database is to use the :doc:`ecoPCR <scripts/ecoPCR>` 
program to simulate a PCR and to extract all sequences from the EMBL that may be amplified 
`in silico` by the two primers (`TTAGATACCCCACTATGC` and `TAGAACAGGCTCCTCTAG`) used for 
PCR amplification. 

The full list of steps for building this reference database would then be:
 
1. Download the whole set of EMBL sequences (available from: 
   ftp://ftp.ebi.ac.uk/pub/databases/embl/release/)
2. Download the NCBI taxonomy (available from: 
   ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz)
3. Format them into the ecoPCR format (see :doc:`obiconvert <scripts/obiconvert>` for how 
   you can produce ecoPCR compatible files)
4. Use ecoPCR to simulate amplification and build a reference database based on putatively
   amplified barcodes together with their recorded taxonomic information  

As step 1 and step 3 can be really time-consuming (about one day), we alredy provide the 
reference database produced by the following commands so that you can skip its 
construction. Note that as the EMBL database and taxonomic data can evolve daily, if you 
run the following commands you may end up with quite different results.


Any utility allowing file downloading from a ftp site can be used. In the following 
commands, we use the commonly used ``wget`` *Unix* command.

Download the sequences
......................

.. code-block:: bash

   > mkdir EMBL
   > cd EMBL
   > wget -nH --cut-dirs=4 -Arel_std_\*.dat.gz -m ftp://ftp.ebi.ac.uk/pub/databases/embl/release/
   > cd ..

Download the taxonomy
.....................

.. code-block:: bash

   > mkdir TAXO
   > cd TAXO
   > wget ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
   > tar -zxvf taxdump.tar.gz
   > cd ..

Format the data
...............

.. code-block:: bash

   > obiconvert --embl -t ./TAXO --ecopcrDB-output=embl_last ./EMBL/*.dat


Use ecoPCR to simulate an in silico` PCR
........................................

.. code-block:: bash

   > ecoPCR -d ./ECODB/embl_last -e 3 -l 50 -L 150 \ 
     TTAGATACCCCACTATGC TAGAACAGGCTCCTCTAG > v05.ecopcr


Note that the primers must be in the same order both in ``wolf_diet_ngsfilter.txt`` and in 
the :doc:`ecoPCR <scripts/ecoPCR>` command.


Clean the database
..................

    1. filter sequences so that they have a good taxonomic description at the species, 
       genus, and family levels (:doc:`obigrep <scripts/obigrep>` command below).
    2. remove redundant sequences (:doc:`obiuniq <scripts/obiuniq>` command below).
    3. ensure that the dereplicated sequences have a taxid at the family level 
       (:doc:`obigrep <scripts/obigrep>` command below).
    4. ensure that sequences each have a unique identification 
       (:doc:`obiannotate <scripts/obiannotate>` command below)

.. code-block:: bash

   > obigrep -d embl_last --require-rank=species \
     --require-rank=genus --require-rank=family v05.ecopcr > v05_clean.fasta
   
   > obiuniq -d embl_last \ 
     v05_clean.fasta > v05_clean_uniq.fasta
   
   > obigrep -d embl_last --require-rank=family \ 
     v05_clean_uniq.fasta > v05_clean_uniq_clean.fasta
   
   > obiannotate --uniq-id v05_clean_uniq_clean.fasta > db_v05.fasta


.. warning::
   From now on, for the sake of clarity, the following commands will use the filenames of 
   the files provided with the tutorial. If you decided to run the last steps and use the 
   files you have produced, you'll have to use ``db_v05.fasta`` instead of 
   ``db_v05_r117.fasta`` and ``embl_last`` instead of ``embl_r117``


Assign each sequence to a taxon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the reference database is built, taxonomic assignment can be carried out using
the :doc:`ecotag <scripts/ecotag>` command.

.. code-block:: bash

   > ecotag -d embl_r117 -R db_v05_r117.fasta wolf.ali.assigned.uniq.c10.l80.clean.fasta > \
     wolf.ali.assigned.uniq.c10.l80.clean.tag.fasta


The :doc:`ecotag <scripts/ecotag>` adds several `key=value` attributes in the sequence 
record header, among them:

- best_match=ACCESSION where ACCESSION is the id of hte sequence in the reference database 
  that best aligns to the query sequence;
- best_identity=FLOAT where FLOAT*100 is the percentage of identity between the best match 
  sequence and the query sequence;
- taxid=TAXID where TAXID is the final assignation of the sequence by 
  :doc:`ecotag <scripts/ecotag>` 
- scientific_name=NAME where NAME is the scientific name of the assigned taxid.

The first sequence record of ``wolf.ali.assigned.uniq.c10.l80.clean.tag.fasta`` is:


.. code-block:: bash

   >HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB_CMP 
   species_name=Capreolus capreolus; family=9850; scientific_name=Capreolus 
   capreolus; rank=species; taxid=9858; best_identity={'db_v05_r117': 1.0}; 
   scientific_name_by_db={'db_v05_r117': 'Capreolus capreolus'}; 
   obiclean_samplecount=2; species=9858; merged_sample={'29a_F260619': 4697, 
   '15a_F730814': 7638}; obiclean_count={'29a_F260619': 5438, '15a_F730814': 8642}; 
   obiclean_singletoncount=0; obiclean_cluster={'29a_F260619': 
   'HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB_CMP', 
   '15a_F730814': 
   'HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB_CMP'}; 
   species_list={'db_v05_r117': ['Capreolus capreolus']}; obiclean_internalcount=0; 
   match_count={'db_v05_r117': 1}; obiclean_head=True; taxid_by_db={'db_v05_r117': 
   9858}; family_name=Cervidae; genus_name=Capreolus; 
   obiclean_status={'29a_F260619': 'h', '15a_F730814': 'h'}; obiclean_headcount=2; 
   count=12335; id_status={'db_v05_r117': True}; best_match={'db_v05_r117': 
   'AJ885202'}; order_name=None; rank_by_db={'db_v05_r117': 'species'}; genus=9857; 
   order=None; 
   ttagccctaaacacaagtaattaatataacaaaattattcgccagagtactaccggcaat
   agcttaaaactcaaaggacttggcggtgctttataccctt


Generate the final result table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some unuseful attributes can be removed at this stage. 

.. code-block:: bash

   > obiannotate  --delete-tag=scientific_name_by_db --delete-tag=obiclean_samplecount \
     --delete-tag=obiclean_count --delete-tag=obiclean_singletoncount \
     --delete-tag=obiclean_cluster --delete-tag=obiclean_internalcount \
     --delete-tag=obiclean_head --delete-tag=taxid_by_db --delete-tag=obiclean_headcount \
     --delete-tag=id_status --delete-tag=rank_by_db --delete-tag=order_name \
     --delete-tag=order wolf.ali.assigned.uniq.c10.l80.clean.tag.fasta > \
     wolf.ali.assigned.uniq.c10.l80.clean.tag.ann.fasta


The first sequence record of ``wolf.ali.assigned.uniq.c10.l80.clean.tag.ann.fasta`` is 
then:

.. code-block:: bash

   >HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB_CMP 
   match_count={'db_v05_r117': 1}; count=12335; species_name=Capreolus capreolus; 
   best_match={'db_v05_r117': 'AJ885202'}; family=9850; family_name=Cervidae; 
   scientific_name=Capreolus capreolus; taxid=9858; rank=species; 
   obiclean_status={'29a_F260619': 'h', '15a_F730814': 'h'}; 
   best_identity={'db_v05_r117': 1.0}; merged_sample={'29a_F260619': 4697, 
   '15a_F730814': 7638}; genus_name=Capreolus; genus=9857; species=9858; 
   species_list={'db_v05_r117': ['Capreolus capreolus']}; 
   ttagccctaaacacaagtaattaatataacaaaattattcgccagagtactaccggcaat
   agcttaaaactcaaaggacttggcggtgctttataccctt


The sequences can be sorted by decreasing order of `count`.

.. code-block:: bash

   > obisort -k count -r wolf.ali.assigned.uniq.c10.l80.clean.tag.ann.fasta >  \ 
     wolf.ali.assigned.uniq.c10.l80.clean.tag.ann.sort.fasta 
   
The first sequence record of ``wolf.ali.assigned.uniq.c10.l80.clean.tag.ann.sort.fasta`` is then:

.. code-block:: bash

   >HELIUM_000100422_612GNAAXX:7:22:8540:14708#0/1_CONS_SUB_SUB_CMP count=12335; 
   match_count={'db_v05_r117': 1}; species_name=Capreolus capreolus; 
   best_match={'db_v05_r117': 'AJ885202'}; family=9850; family_name=Cervidae; 
   scientific_name=Capreolus capreolus; taxid=9858; rank=species; 
   obiclean_status={'29a_F260619': 'h', '15a_F730814': 'h'}; 
   best_identity={'db_v05_r117': 1.0}; merged_sample={'29a_F260619': 4697, 
   '15a_F730814': 7638}; genus_name=Capreolus; genus=9857; species=9858; 
   species_list={'db_v05_r117': ['Capreolus capreolus']}; 
   ttagccctaaacacaagtaattaatataacaaaattattcgccagagtactaccggcaat
   agcttaaaactcaaaggacttggcggtgctttataccctt

Finally, a tab-delimited file that can be open by excel or R is generated. 

.. code-block:: bash

   > obitab -o wolf.ali.assigned.uniq.c10.l80.clean.tag.ann.sort.fasta > \ 
     wolf.ali.assigned.uniq.c10.l80.clean.tag.ann.sort.tab
 
   
This file contains 26 sequences. You can deduce the diet of each sample:
 - 13a_F730603: Cervus elaphus
 - 15a_F730814: Capreolus capreolus
 - 26a_F040644: Marmota sp. (according to the location, it is Marmota marmota)
 - 29a_F260619: Capreolus capreolus

Note that we also obtained a few wolf sequences although a wolf-blocking oligonucleotide 
was used.


References
----------

 - Shehzad W, Riaz T, Nawaz MA, Miquel C, Poillot C, Shah SA, Pompanon F, Coissac E, 
   Taberlet P (2012) Carnivore diet analysis based on next generation sequencing: 
   application to the leopard cat (Prionailurus bengalensis) in Pakistan. Molecular 
   Ecology, 21, 1951-1965.
 - Riaz T, Shehzad W, Viari A, Pompanon F, Taberlet P, Coissac E (2011) ecoPrimers: 
   inference of new DNA barcode markers from whole genome sequence analysis. Nucleic 
   Acids Research, 39, e145.
 - Seguritan V, Rohwer F. (2001) FastGroup: a program to dereplicate libraries of 
   16S rDNA sequences. BMC Bioinformatics. 2001;2:9. Epub 2001 Oct 16.


Contact
-------

For any suggestion or improvement, please contact :

    - eric.coissac@metabarcoding.org
    - frederic.boyer@metabarcoding.org


