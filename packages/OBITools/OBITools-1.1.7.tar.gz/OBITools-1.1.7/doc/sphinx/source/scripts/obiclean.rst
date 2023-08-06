.. automodule:: obiclean

   :py:mod:`obiclean` specific options
   -----------------------------------  

   .. cmdoption::  -d <INTEGER>, --distance=<INTEGER>   
   
                   Maximum numbers of differences between two variant sequences (default: 1).

   .. cmdoption::  -s <KEY>, --sample=<KEY>  
   
                   Attribute containing sample descriptions.

   .. cmdoption::  -r <FLOAT>, --ratio=<FLOAT>  
   
                   Threshold ratio between counts (rare/abundant counts) of two sequence records 
                   so that the less abundant one is a variant of the more abundant
                   (default: 1, i.e. all less abundant sequences are variants).

   .. cmdoption::  -C, --cluster  
   
                   Switch :py:mod:`obiclean` into its clustering mode. This adds information
                   to each sequence about the true.

   .. cmdoption::  -H, --head  
   
                   Select only sequences with the head status in a least one sample.


   .. cmdoption::  -g, --graph  
   
                   Creates a file containing the set of DAG used by the obiclean clustering algorithm.
                   The graph file follows the `dot` format

   .. include:: ../optionsSet/inputformat.txt
    
   .. include:: ../optionsSet/outputformat.txt
    
   .. include:: ../optionsSet/defaultoptions.txt

   :py:mod:`obiclean` used sequence attributes
   -----------------------------------------------

      .. hlist::
           :columns: 3

           - :doc:`count <../attributes/count>`

   :py:mod:`obiclean` added sequence attributes
   -----------------------------------------------

      .. hlist::
           :columns: 3

           - :doc:`obiclean_cluster <../attributes/obiclean_cluster>`
           - :doc:`obiclean_count <../attributes/obiclean_count>`
           - :doc:`obiclean_head <../attributes/obiclean_head>`
           - :doc:`obiclean_headcount <../attributes/obiclean_headcount>`
           - :doc:`obiclean_internalcount <../attributes/obiclean_internalcount>`
           - :doc:`obiclean_samplecount <../attributes/obiclean_samplecount>`
           - :doc:`obiclean_singletoncount <../attributes/obiclean_singletoncount>`
           - :doc:`obiclean_status <../attributes/obiclean_status>`
                  