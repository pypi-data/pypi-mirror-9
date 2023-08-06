Welcome to `dummypdf`'s documentation!
======================================

|sources| |pypi| |documentation| |license|

This tool can produce dummy PDF files. They can be used to test software
manipulating such PDF files.

The produced files contain:

- a big page number;
- a rectangle around the page, and a cross across the whole page.

The color, page format and number of pages can be configured.

Examples:

- One page A4 paper: :download:`example1 <examples/example1.pdf>`
- Six pages, a third of an A4 paper: :download:`example2 <examples/example2.pdf>`

Download and install
--------------------

See the `project main page <http://git.framasoft.org/spalax/dummypdf>`__.

Usage
-----

Here are the command line options for `dummypdf`.

.. argparse::
    :module: dummypdf.main
    :func: commandline_parser
    :prog: dummypdf

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |documentation| image:: http://readthedocs.org/projects/dummypdf/badge
  :target: http://dummypdf.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/dummypdf.svg
  :target: http://pypi.python.org/pypi/dummypdf
.. |license| image:: https://img.shields.io/pypi/l/dummypdf.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/sources-dummypdf-brightgreen.svg
  :target: http://git.framasoft.org/spalax/dummypdf
