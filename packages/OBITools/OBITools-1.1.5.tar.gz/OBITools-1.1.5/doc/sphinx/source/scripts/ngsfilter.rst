.. automodule:: ngsfilter

   :py:mod:`ngsfilter` specific options
   ------------------------------------

   .. cmdoption::  -t, --tag-list   
   
                   Used to specify the file containing the samples description (with tags, primers, sample names,...) 

   .. cmdoption::  -u, --unidentified  
   
                   Filename used to store the sequences unassigned to any sample

   .. cmdoption::  -e, --error  
   
                   Used to specify the number of errors allowed for matching primers [default = 2]


   .. include:: ../optionsSet/inputformat.txt

   .. include:: ../optionsSet/outputformat.txt

   .. include:: ../optionsSet/defaultoptions.txt


   :py:mod:`ngsfilter` added sequence attributes
   ---------------------------------------------
   
      .. hlist::
           :columns: 3
           
           - :doc:`avg_quality <../attributes/avg_quality>`
           - :doc:`complemented <../attributes/complemented>`
           - :doc:`cut <../attributes/cut>`
           - :doc:`direction <../attributes/direction>`
           - :doc:`error <../attributes/error>`
           - :doc:`experiment <../attributes/experiment>`
           - :doc:`forward_match <../attributes/forward_match>`
           - :doc:`forward_primer <../attributes/forward_primer>`
           - :doc:`forward_score <../attributes/forward_score>`
           - :doc:`forward_tag <../attributes/forward_tag>`
           - :doc:`head_quality <../attributes/head_quality>`
           - :doc:`mid_quality <../attributes/mid_quality>`
           - :doc:`partial <../attributes/partial>`
           - :doc:`reverse_match <../attributes/reverse_match>`
           - :doc:`reverse_primer <../attributes/reverse_primer>`
           - :doc:`reverse_score <../attributes/reverse_score>`
           - :doc:`reverse_tag <../attributes/reverse_tag>`
           - :doc:`sample <../attributes/sample>`
           - :doc:`seq_length <../attributes/seq_length>`
           - :doc:`seq_length_ori <../attributes/seq_length_ori>`
           - :doc:`status <../attributes/status>`
           - :doc:`tail_quality <../attributes/tail_quality>`

