pybib
=====

Installation
------------

To use this script, install the package using ``pip`` with the following
command:

.. code:: sh

    $ pip3 install --user pybib

Usage
-----

.. code:: sh

    # Retrieve a single BibTeX entry
    $ bib 10.1145/159544.159617

    # Retrieve a list of BibTeX entries
    $ cat citations.doi
    10.1145/159544.159611
    10.1145/159544.159612
    10.1145/159544.159613

    $ bib -f citations.doi

Troubleshooting
---------------

If you encounter problems using this program, please open an issue on
this repository so I can rectify the problem.

.. |PyPI version| image:: https://img.shields.io/pypi/v/pybib.svg?style=flat
   :target: https://pypi.python.org/pypi?:action=display&name=pybib
