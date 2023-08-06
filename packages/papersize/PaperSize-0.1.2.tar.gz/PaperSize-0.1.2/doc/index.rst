Welcome to `papersize`'s documentation!
=======================================

Paper size related data and functions.

|sources| |pypi| |documentation| |license|

This module provides tools to manipulate paper sizes, that is:

- a dictionary of several named standard names (e.g. A4, letter) , with their
  respective sizes (with and height);
- functions to convert sizes between units;
- functions to manipulate paper orientation (portrait or landscape);
- tools to parse paper sizes, so that you do not have to worry about the format
  of paper sizes provided by your user, it being `a4` or `21cm x 29.7cm`.

Module documentation
--------------------

.. automodule:: papersize

Download and install
--------------------

* Download: `papersize-0.1.0.tar.gz <http://pypi.python.org/packages/source/p/papersize/papersize-0.1.0.tar.gz>`_
* Install (in a `virtualenv`, not to mess with your distribution installation system):

    * With `pip`:

        .. code-block:: shell

            pip install papersize

    * Without `pip`: Download and unpack package, and run:

        .. code-block:: shell

            python3 setup.py install

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |documentation| image:: http://readthedocs.org/projects/papersize/badge
  :target: http://papersize.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/papersize.svg
  :target: http://pypi.python.org/pypi/papersize
.. |license| image:: https://img.shields.io/pypi/l/PaperSize.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/home-papersize-brightgreen.svg
  :target: http://git.framasoft.org/spalax/papersize
