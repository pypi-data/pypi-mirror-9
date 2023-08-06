|pypi| |test| |coverage| |docs|

========
snakeoil
========

snakeoil is a python library that implements optimized versions of common
python functionality. Some classes and functions have cpython equivalents,
but they all have native python implementations too.

Contact
=======

For support and development inquiries a `mailing list`_ is available or you can
join `#pkgcore`_ on Freenode.

For bugs and feature requests please create an issue in the `issue tracker`_.

Tests
=====

A standalone test runner is integrated in setup.py; to run, just execute::

    python setup.py test

In addition, a tox config is provided so the testsuite can be run in a
virtualenv setup against all supported python versions. To run tests for all
environments just execute **tox** in the root directory of a repo or unpacked
tarball. Otherwise, for a specific python version execute something similar to
the following::

    tox -e py27

Note that mock_ is required for tests if you're using anything less than python
3.3.

Installing
==========

To build::

    tar jxf snakeoil-0.xx.tar.bz2
    cd snakeoil-0.xx
    python setup.py build

To install::

    cd snakeoil-0.xx
    python setup.py install

.. _`mailing list`: https://groups.google.com/forum/#!forum/python-snakeoil
.. _#pkgcore: https://webchat.freenode.net?channels=%23pkgcore&uio=d4
.. _`issue tracker`: https://github.com/pkgcore/snakeoil/issues
.. _mock: https://pypi.python.org/pypi/mock

.. |pypi| image:: https://img.shields.io/pypi/v/snakeoil.svg
    :target: https://pypi.python.org/pypi/snakeoil
.. |test| image:: https://travis-ci.org/pkgcore/snakeoil.svg?branch=master
    :target: https://travis-ci.org/pkgcore/snakeoil
.. |coverage| image:: https://coveralls.io/repos/pkgcore/snakeoil/badge.png?branch=master
    :target: https://coveralls.io/r/pkgcore/snakeoil?branch=master
.. |docs| image:: https://readthedocs.org/projects/snakeoil/badge/?version=latest
    :target: https://readthedocs.org/projects/snakeoil/?badge=latest
    :alt: Documentation Status
