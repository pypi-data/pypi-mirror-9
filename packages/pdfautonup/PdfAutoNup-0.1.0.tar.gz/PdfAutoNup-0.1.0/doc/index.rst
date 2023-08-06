Welcome to `PdfAutoNup`'s documentation!
========================================

Render PDF files to a 'n-up' PDF file of a given page size, guessing the
layout.


This program is similar to ``pdfnup`` (from package `pdfjam
<http://www2.warwick.ac.uk/fac/sci/statistics/staff/academic-research/firth/software/pdfjam/>`_),
with the following difference:

- ``pdfnup`` is focused on layout: "I want my pdf to appear 'n-upped' on a
  '2x3' layout".
- ``pdfautonup`` is focused on destination paper size: "I want to fit pages on
  a pdf of a given page size".

Rationale
---------

As a teacher, I often write A5 (or some weirder format) documents, to be copied
and given to my students. I was tired of:

- having to explicitely specify the arguments to ``pdfnup`` (since it can be
  guessed given the source file format);
- having to repeat my source file as an argument (when, for example, merging
  four identical instances of a A6 document to an A4 paper).

This program ``pdfautonup`` automatically does this:

- it fits source pages in one destination page;
- it include source files several times is necessary, not to waste space on the
  destination file.

Examples
--------

With default options, my default paper size being A4, ``pdfautonup`` on:

- :download:`example1.pdf <../examples/example1.pdf>` gives :download:`example1-nup.pdf <../examples/example1-nup.pdf>`
- :download:`example2.pdf <../examples/example2.pdf>` gives :download:`example2-nup.pdf <../examples/example2-nup.pdf>`

Download and install
--------------------

See the `main project page <http://git.framasoft.org/spalax/pdfautonup>`_ for
instructions.

Usage
-----

Here are the command line options for `pdfautonup`.

.. argparse::
    :module: pdfautonup.options
    :func: commandline_parser
    :prog: pdfautonup

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

