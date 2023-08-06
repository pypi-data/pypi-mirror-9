.. meta::
   :description: Orange Textable documentation, URLs widget
   :keywords: Orange, Textable, documentation, URLs, widget

.. _URLs:

URLs
====

.. image:: figures/URLs_54.png

Fetch text data from internet locations.

Signals
-------

Inputs:

* ``Message``

  JSON Message controlling the list of imported URLs

Outputs:

* ``Text data``

  Segmentation covering the content of imported URLs

Description
-----------

This widget is designed to import the contents of one or several internet
locations (URLs) in Orange Canvas. It outputs a segmentation containing a
potentially annotated) segment for the content of each selected URL. The
imported textual content is systematically converted in Unicode (from the
encoding defined by the user) and subjected to the `canonical Unicode
decomposition-recomposition <http://unicode.org/reports/tr15>`_ technique:
Unicode sequences such as ``LATIN SMALL LETTER C (U+0063)`` + ``COMBINING
CEDILLA (U+0327)`` are systematically replaced by the combined equivalent,
e.g. ``LATIN SMALL LETTER C WITH CEDILLA (U+00C7)``.

The interface of **URLs** is available in two versions, according to whether or
not the **Advanced Settings** checkbox is selected.

Basic interface
~~~~~~~~~~~~~~~

In its basic version (see :ref:`figure 1 <URLs_fig1>` below), the **URLs**
widget is limited to the import of a single URL's content. The interface
contains a **Source** section enabling the user to type the input URL and to
select the encoding of its content.

.. _URLs_fig1:

.. figure:: figures/urls_basic_example.png
    :align: center
    :alt: Basic interface of the URLs widget

    Figure 1: **URLs** widget (basic interface).

The **Options** section allows the user to define the label of the output
segmentation (**Output segmentation label**), here *url_content*.

The **Info** section indicates the  the number of characters in the single
segment contained in the output segmentation, or the reasons why no
segmentation is emitted (inability to retrieve the data, encoding issue,
etc.).

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.
Advanced interface
~~~~~~~~~~~~~~~~~~

The advanced version of **URLs** allows the user to import the content of
several URLs in a determined order; each URL can moreover be associated to a
distinct encoding and specific annotations. The emitted segmentation contains
a segment for the content of each imported URL.

.. _URLs_fig2:

.. figure:: figures/urls_advanced_example.png
    :align: center
    :alt: Advanced interface of the URLs widget
    :scale: 80%

    Figure 2: **URLs** widget (advanced interface).

The advanced interface (see :ref:`figure 2 <URLs_fig2>` above) presents
similarities with that of the :ref:`Text Files`, :ref:`Recode`, and
:ref:`Segment` widgets. The **Sources** section  allows the user to specify
the imported URL(s) as well as their content's encoding, to determine the
order in which they appear in the output segmentation, and optionally to
assign an annotation. The list of imported URLs appears at the top of the
window; the columns of this list indicate (a) the URL, (b) the corresponding
annotation (if any), and (c) the encoding with which the content of each is
associated.

In :ref:`figure 2 <URLs_fig2>`, we can see that two URLs are imported (only
the end of each URL is visible on the figure) and that each is provided with
an annotation whose key is *author*. The first URL associates value *Dickens*
with this key and is encoded in utf-8; the second one has value *Fitzgerald*
and is encoded in iso-8859-1.

The first buttons on the right of the imported URLs' list enable the user to
modify the order in which they appear in the output segmentation (**Move Up**
and **Move Down**), to delete an URL from the list (**Remove**) or to
completely empty it (**Clear All**). Except for **Clear All**, all these
buttons require the user to previously select an entry from the list. **Import
List** enables the user to import a list of URLs in JSON format (see
:doc:`JSON im-/export format <json_format>`, :doc:`URL list <json_url_list>`)
and to add it to the previously selected sources. In the opposite **Export
List** enables the user to export the source list in a JSON file.

The remainder of the **Sources** section allows the user to add new URLs to
the list. these must first be inputted in the field with the same name before
they can be added to the list by clicking on the **Add** button. In order for
several URLs to be simultaneously added, they must be separated by the string
" / " (space + slash + space).

Before adding one or more URLs to the list by clicking on **Add**, it is
possible to select their encoding (**Encoding**), and to assign an annotation
by specifying its key in the **Annotation key** field and the corresponding
value in the **Annotation value** field. These three parameters (encoding,
key, value) will be applied to each URL appearing in the **URLs** field
at the moment of their addition to the list with **Add**.

The **Options** section allows the user to specify the label affected to the
output segmentation (**Output segmentation label**). The **Import URLs
with key** checkbox enables the program to create for each imported URL an
annotation whose value is the URL (as displayed in the list) and whose
key is specified by the user in the text field on the right of the checkbox.
Similarly the button **Auto-number with key** enables the program to
automatically number the imported URLs and to associate the number to the
annotation key specified in the text field on the right.

In :ref:`figure 2 <URLs_fig2>`, it was thus decided to assign the label
*novels* to the output segmentation, and to associate the name of each URL to
the annotation key *url*. On the other hand, the auto-numbering option
has not been enabled.

The **Info** section indicates the length of the output segmentation in
characters, or the reasons why no segmentation is emitted (inability to
retrieve the data, encoding issue, etc.). In the example, the two segments
corresponding to the imported URLs' content thus total up to 1'300'344
characters.

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface.

.. _urls_remote_control_ref:

Remote control
~~~~~~~~~~~~~~

**URLs** is one the widgets that can be controlled by means of the
:ref:`Message` widget. Indeed, it can receive in input a message consisting
of a URL list in JSON format (see :doc:`JSON im-/export format
<json_format>`, :doc:`URL list <json_url_list>`), in which case the list
of URLs specified in this message replaces previously imported sources (if
any). Note that removing the incoming connection from the **Message** instance
will not, by itself, remove the list of URLs imported in this way from the
**URLs** instance's interface; conversely, this list of files can be
modified using buttons **Move up/down**, **Remove**, etc. even if the incoming
connection from the **Message** instance has not been removed. Finally, note
that if an **URLs** instance has the basic version of its interface activated
when an incoming connection is created from an instance of :ref:`Message`, it
automatically switches to the advanced interface.

Examples
--------

* :doc:`Cookbook: Import text from internet location
  <import_text_internet_location>`

See also
--------

* :doc:`Reference: JSON im-/export format <json_format>`, :doc:`URL list
  <json_url_list>`
* :ref:`Reference: Message widget <Message>`

