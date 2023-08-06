The extended OBITools fasta and fastq format
--------------------------------------------
.. _obitools-fasta:

The *extended OBITools Fasta format* is a strict :doc:`fasta format file <fasta>`.
The file in *extended OBITools Fasta format* can be readed by all programs
reading fasta files.

Difference between standard and extended fasta is just the structure of the title
line. For OBITools title line is divided in three parts :

        - Seqid : the sequence identifier
        - key=value; : a set of key/value keys
        - the sequence definition


::

    >my_sequence taxid=3456; direct=True; sample=A354; this is my pretty sequence
    ACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGT
    GTGCTGACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTACGTTGCAGTGTTT
    AACGACGTTGCAGTACGTTGCAGT

Following these rules, the title line can be parsed :

        - The sequence identifier of this sequence is : *my_sequence* 
        - Three keys are assigned to this sequence :
              - Key *taxid* with value *3456*
              - Key *direct* with value *True*
              - Key *sample* with value *A354*
        - The definition of this sequence is this is *my pretty sequence* 

Values can be any valid python expression. If a key value cannot be evaluated as
a python expression, it is them assumed as a simple string. Following this rule,
taxid value is considered as an integer value, direct value as a boolean and sample
value is not a valid python expression so it is considered as a string value.


Names reserved for attributes
.............................

The following attribute names are created by some obitools programs and used by others.
They have a special meaning. So we recommend not to use them with another semantic.

Contents:

.. toctree::
   :maxdepth: 2
      
   
   attributes/ali_dir
   attributes/ali_length
   attributes/avg_quality 
   attributes/best_match 
   attributes/best_identity 
   attributes/class 
   attributes/cluster 
   attributes/complemented 
   attributes/count 
   attributes/cut 
   attributes/direction 
   attributes/distance 
   attributes/error 
   attributes/experiment 
   attributes/family 
   attributes/family_name 
   attributes/forward_error 
   attributes/forward_match 
   attributes/forward_primer 
   attributes/forward_score 
   attributes/forward_tag 
   attributes/forward_tm 
   attributes/genus 
   attributes/genus_name 
   attributes/head_quality 
   attributes/id_status 
   attributes/merged_star 
   attributes/merged 
   attributes/mid_quality 
   attributes/mode 
   attributes/obiclean_cluster 
   attributes/obiclean_count 
   attributes/obiclean_head 
   attributes/obiclean_headcount 
   attributes/obiclean_internalcount 
   attributes/obiclean_samplecount 
   attributes/obiclean_singletoncount
   attributes/obiclean_status 
   
   attributes/occurrence 
   attributes/order 
   attributes/order_name 
   attributes/pairend_limit  
   attributes/partial  
   attributes/rank 
   attributes/reverse_error 
   attributes/reverse_match 
   attributes/reverse_primer 
   attributes/reverse_score 
   attributes/reverse_tag 
   attributes/reverse_tm 
   attributes/sample 
   attributes/scientific_name 
   attributes/score
   attributes/score_norm
   attributes/select 
   attributes/seq_ab_match
   attributes/seq_a_single
   attributes/seq_a_mismatch
   attributes/seq_a_deletion
   attributes/seq_a_insertion
   attributes/seq_b_single
   attributes/seq_b_mismatch
   attributes/seq_b_deletion
   attributes/seq_b_insertion
   attributes/seq_length 
   attributes/seq_length_ori
   attributes/seq_rank 
   attributes/sminL 
   attributes/sminR 
   attributes/species 
   attributes/species_list 
   attributes/species_name 
   attributes/status 
   attributes/strand 
   attributes/tail_quality
   attributes/taxid
   