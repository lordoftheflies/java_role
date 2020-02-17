.. java_role documentation master file, created by
    sphinx-quickstart on Mon Feb 17 04:34:09 2020.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Welcome to java_role's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. uml::
   :caption: Caption with **bold** and *italic*
   :width: 50mm

   Foo <|-- Bar

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Google Charts
-------------

 piechart

   dog: 100
   cat: 80
   rabbit: 40

.. role:: python(code)
    :language: python

:python:`"some" "highlighted code"`


.. highlight: python

:code:`"some" "highlighted code"`


.. highlight: python

``"some" "highlighted code"``

:literal:`normal literal`


.. uml::

   Alice -> Bob: Hi!
   Alice <- Bob: How are you?



.. graphviz::

    digraph example {
         a [label="sphinx", href="http://sphinx-doc.org", target="_top"];
         b [label="other"];
         a -> b;
     }

.. digraph:: foo

   "bar" -> "baz" -> "quux";
