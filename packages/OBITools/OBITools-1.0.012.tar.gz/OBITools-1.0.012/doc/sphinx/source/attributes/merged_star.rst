merged_*
========

    The `merged_*` attribute is built based on another attribute `*` (for example, 
    `sample`) by the :doc:`obiuniq <../scripts/obiuniq>` program. The value associated to the `merged_*` 
    attribute is a contingency table summarizing modality frequencies associated to the `*` attribute.
    For instance, `merged_sample={'X1': 12, 'X2': 10}` means that among the 22 identical sequences merged 
    by the :doc:`obiuniq <../scripts/obiuniq>`, the `sample` attribute was set 12 and 10 times to the modality 'X1' 
    and 'X2', respectively.
    
    Attribute added by the program:
        - :doc:`obiuniq <../scripts/obiuniq>`
        - :doc:`obiselect <../scripts/obiselect>`

