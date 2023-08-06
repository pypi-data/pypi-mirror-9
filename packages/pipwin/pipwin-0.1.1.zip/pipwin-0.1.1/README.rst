===============================
pipwin
===============================

.. image:: https://img.shields.io/pypi/v/pipwin.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pipwin/
    :alt: Latest Version
    
.. image:: https://img.shields.io/pypi/dm/pipwin.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pipwin/
    :alt: Downloads
  
.. image:: https://img.shields.io/pypi/l/pipwin.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pipwin/
    :alt: License

**pipwin** is a complementary tool for **pip** on Windows.
**pipwin** installs unofficial python package binaries for windows provided by Christoph Gohlke here `http://www.lfd.uci.edu/~gohlke/pythonlibs/ <http://http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_

QuickStart
^^^^^^^^^^

.. code-block::

   >> pip install pipwin
   >> pipwin search cv

   Did you mean any of these ?

     -> cvxopt
     -> opencv-python
     -> abcview
     -> cvxpy
   >> pipwin install opencv-python


Details
^^^^^^^

- On first run, **pipwin** builds a cache of available package list in ``~/.pipwin``.

- You can force a cache rebuild using : ``pipwin refresh``

- List all available packages : ``pipwin list``

- Search packages : ``pipwin search <partial_name/name>``

- Install packages : ``pipwin install <package>``

- Uninstall packages (Can directly use **pip** for this) : ``pipwin uninstall <package>``

**Free software: BSD license**
