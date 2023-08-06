| |Build Status|
| |Coverage Status|
| |Scrutinizer Code Quality|
| |PyPI Version|
| |PyPI Downloads|

Getting Started
===============

Requirements
------------

-  Python 3.3+
-  Git (with `stored
   credentials <http://stackoverflow.com/questions/7773181>`__)
-  OSX/Linux (with a decent shell for Git)

Installation
------------

GDM can be installed with pip:

::

    $ pip3 install gdm

or directly from the source code:

::

    $ git clone https://github.com/jacebrowning/gdm.git
    $ cd gdm
    $ python3 setup.py install

Setup
-----

Create a GDM configuration file (``gdm.yml`` or ``.gdm.yml``) in the
root of your working tree:

.. code:: yaml

    location: .gdm
    sources:
    - repo: https://github.com/kstenerud/iOS-Universal-Framework
      dir: framework
      rev: Mk5-end-of-life
      link: Frameworks/iOS-Universal-Framework
    - repo: https://github.com/jonreid/XcodeCoverage
      dir: coverage
      rev: master
      link: Tools/XcodeCoverage

Ignore GDM's dependency storage location:

::

    $ echo .gdm >> .gitignore

Basic Usage
===========

Get the specified versions of all dependencies:

::

    $ gdm install

which will essentially:

#. clone each specfied ``repo`` to *root*/``location``/``dir``
#. checkout the specified ``rev`` for each nested working tree
#. symbolicly link each ``location``/``dir`` from *root*/``link``
   (optional)
#. repeat for all nested working trees containing a configuration file

To remove all installed dependencies:

::

    $ gdm uninstall

For Contributors
================

Requirements
------------

-  Make:

   -  Windows: http://cygwin.com/install.html
   -  Mac: https://developer.apple.com/xcode
   -  Linux: http://www.gnu.org/software/make (likely already installed)

-  virtualenv: https://pypi.python.org/pypi/virtualenv#installation
-  Pandoc: http://johnmacfarlane.net/pandoc/installing.html
-  Graphviz: http://www.graphviz.org/Download.php

Installation
------------

Create a virtualenv:

::

    $ make env

Run the tests:

::

    $ make test
    $ make tests  # includes integration tests

Build the documentation:

::

    $ make doc

Run static analysis:

::

    $ make pep8
    $ make pep257
    $ make pylint
    $ make check  # includes all checks

Prepare a release:

::

    $ make dist  # dry run
    $ make upload

.. |Build Status| image:: http://img.shields.io/travis/jacebrowning/gdm/master.svg
   :target: https://travis-ci.org/jacebrowning/gdm
.. |Coverage Status| image:: http://img.shields.io/coveralls/jacebrowning/gdm/master.svg
   :target: https://coveralls.io/r/jacebrowning/gdm
.. |Scrutinizer Code Quality| image:: http://img.shields.io/scrutinizer/g/jacebrowning/gdm.svg
   :target: https://scrutinizer-ci.com/g/jacebrowning/gdm/?branch=master
.. |PyPI Version| image:: http://img.shields.io/pypi/v/GDM.svg
   :target: https://pypi.python.org/pypi/GDM
.. |PyPI Downloads| image:: http://img.shields.io/pypi/dm/GDM.svg
   :target: https://pypi.python.org/pypi/GDM

Changelog
=========

0.1.3 (2014/02/27)
------------------

- Strip whitespace during shell logging.

0.1.2 (2014/02/27)
------------------

- Added '--force' argument to:
    - overwrite uncommitted changes
    - create symbolic links in place of directories
- Added live shell command output with '-vv' argument.

0.1 (2014/02/24)
----------------

- Initial release.


