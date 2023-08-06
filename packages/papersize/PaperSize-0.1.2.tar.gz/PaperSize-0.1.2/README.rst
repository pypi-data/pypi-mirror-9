Paper size related tools

|sources| |pypi| |documentation| |license|

This module provides tools to manipulate paper sizes, that is:

- a dictionary of several named standard names (e.g. A4, letter) , with their
  respective sizes (with and height);
- functions to convert sizes between units;
- functions to manipulate paper orientation (portrait or landscape);
- tools to parse paper sizes, so that you do not have to worry about the format
  of paper sizes provided by your user, it being `a4` or `21cm x 29.7cm`.

Install
=======

This module is compatible with both python 2 and 3.

* From sources::

    python setup.py install

* From pip::

    pip install papersize

Test
====

* Current python version::

    python setup.py test

* All supported python versions (using `tox <http://tox.testrun.org>`_)::

    tox

Documentation
=============

The documentation is available on `readthedocs
<http://papersize.readthedocs.org>`_.  You can build it using::

  cd doc && make html

.. |documentation| image:: http://readthedocs.org/projects/papersize/badge
  :target: http://papersize.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/papersize.svg
  :target: http://pypi.python.org/pypi/papersize
.. |license| image:: https://img.shields.io/pypi/l/PaperSize.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/home-papersize-brightgreen.svg
  :target: http://git.framasoft.org/spalax/papersize
