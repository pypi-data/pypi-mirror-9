pdftools
========

-  **Version** 1.0.1
-  **Copyright (c)** 2015 Stefan Lehmann
-  **License:** MIT
-  **Description:**\ \* This is a small collection of convenience python
   scripts for fast pdf manipulation via commandline.

Features
--------

-  split PDF files in multiple documents
-  merge PDF files into one document
-  rotate PDF files
-  zip PDF files in one document

Usage
-----

*pdftools* adds some scripts to your existing Python installation that
can be called via the commandline. The description for each script is
listed below.

pdfsplit.py
~~~~~~~~~~~

With *pdfsplit* one PDF file can be split in multiple documents. The new
documents are named according to the *-o* argument. The page number and
the file ending *pdf* are added to the name automatically.

.. code:: bash

    usage: pdfsplit.py [-h] [-o OUTPUT] [-s STEPSIZE] input

    Split a PDF file in multiple documents.


    positional arguments:
      input                 input file that shall be splitted

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            filename of the output files
      -s STEPSIZE, --stepsize STEPSIZE
                            defines how many pages are packed in one file

pdfmerge.py
~~~~~~~~~~~

This tool merges multiple input files to one output file. The page order
is according to the order of the input files.

.. code:: bash

    usage: pdfmerge.py [-h] -o OUTPUT [-d] inputs [inputs ...]

    Merge the pages of multiple input files in one output file.

    positional arguments:
      inputs                list of input files

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            filename of the output file
      -d, --delete          delete input files after merge

pdfrotate.py
~~~~~~~~~~~~

Rotate the pages of one or multiple input files clockwise or
counterclockwise. The source file will be overwritten.

.. code:: bash

    usage: pdfrotate.py [-h] [-c] inputs [inputs ...]

    Rotate the pages of multiple input files by 90 degrees. Wildcards can be used.

    positional arguments:
      inputs      list of input files

    optional arguments:
      -h, --help  show this help message and exit
      -c          rotate pages counterclockwise

pdfzip
------

Zip the pages of two input files in one output file. This is useful when
dealing with scanned documents where even pages are in one docuemnt and
odd pages in the other.

.. code:: bash

    usage: pdfzip.py [-h] -o OUTPUT [-d] input1 input2

    Zip the pages of two documents in one output file.

    positional arguments:
    input1                first inputfile
    input2                second inputfile

    optional arguments:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
    filename of the output file
    -d, --delete          delete input files after merge
