.. meta::
   :description: Orange Textable documentation, Merge widget
   :keywords: Orange, Textable, documentation, Merge, widget

.. _Merge:

Merge
=====

.. image:: figures/Merge_54.png

Merge two or more segmentations.

Signals
-------

Inputs:

* ``Segmentation`` (multiple)

  Any number of segmentations that should be merged together

Outputs:

* ``Merged data``

  Merged segmentation

Description
-----------

This widget takes several input segmentations, successively copies each
segment of each input segmentation to form a new segmentation, and sends this
segmentation to its output connections.

.. _merge_fig1:

.. figure:: figures/merge_advanced_example.png
    :align: center
    :alt: Merge widget (advanced interface)

    Figure 1: **Merge** widget (advanced interface).

The **Ordering** section of the widget interface (see :ref:`figure 1
<merge_fig1>` above) allows the user to select the order in which the input
segmentations are placed to form the merged output segmentation. The label of
each input segmentation appears on a line of the list and can be selected then
moved by clicking on the **Move Up** and **Move Down** buttons.

The **Options** section allows the user to specify the label assigned to the
output segmentation (**Output segmentation label**). The **Import labels with
key** checkbox enables the user to create for each input segmentation an
annotation whose value is the segmentation label (as displayed in the list)
and whose key is specified by the user in the text field on the right of the
checkbox. Similarly, the **Auto-number with key** checkbox enables the program
to automatically number the output segments and to associate the number to the
annotation key specified in the text field on the right. The **Copy
annotations** checkbox copies every input segmentation annotation to the
output segmentation.

The two last elements of the **Options** section influence the ordering of
segments in the output segmentation as well as their count. The **Sort
segments** checkbox enables the program to sort the segments on the basis of
their address (string index first, then initial position, and final position);
this option is typically useful to rearrange segments that belong to
different segmentations of a single text in their order of occurrence in the
text. [#]_ The **Fuse duplicate segments** checkbox enables the program to
fuse into a single segment several distinct segments whose addresses are the
same; the annotations associated to the fused segments are all copied in the
single resulting segment. [#]_

When the **Advanced settings** checkbox is not selected, only the **Output
segmentation label** and **Import labels with key** options are accessible.
In that case, auto-numbering is disabled, annotations are copied by default,
and segments are sorted by address but not fused.

The **Info** section indicates the number of segments in the output
segmentation, or the reasons why no segmentation is emitted (no input data,
no label specified for the output segmentation, etc.).

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface or when its input data are
modified (by deletion or addition of a connection, or because modified data is
received through an existing connection).

Examples
--------

* :doc:`Getting started: Merging segmentations together
  <merging_segmentations_together>`
* :doc:`Getting started: Annotating by merging <annotating_merging>`
* :doc:`Cookbook: Merge several texts <merge_several_texts>`

See also
--------

* :doc:`Getting started: Tagging table rows with annotations
  <tagging_table_rows_annotations>`

Footnotes
---------

.. [#] Note that if sorting is enabled, it may well result in segments being
       ordered in a different way than specified by the user in the
       **Ordering** section.

.. [#] In the case where the fused segments have distinct values for the same
       annotation key, only the value of the last segment (in the order of the
       output segmentation before fusion) will be retained.


