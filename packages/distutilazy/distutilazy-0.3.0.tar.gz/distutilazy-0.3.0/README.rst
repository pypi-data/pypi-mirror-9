
Distutilazy
===========

.. image:: https://travis-ci.org/farzadghanei/distutilazy.svg?branch=master
    :target: https://travis-ci.org/farzadghanei/distutilazy

Extra distutils commands, including:

 - clean_pyc: clean compiled python files
 - clean_all: using distutils.clean and clean_pyc to clean all temporary files
 - bdist_pyinstaller: convenient calls for `PyInstaller <http://www.pyinstaller.org>`_ with sane defaults
 - test: run unit tests


How
---
Make sure distutilazy package is in sys.path, then add ``distutilazy.command`` package to the list of command packages in your ``setup.cfg`` file.

::

    [global]
    command_packages = distutilazy.command

That's it. now you may use new commands directly from your ``setup.py``:

To clean compiled python files from the project:

.. code-block:: bash

    $ python setup.py clean_pyc


To run unit tests (by default runs tests/test*.py files):

.. code-block:: bash

    $ python setup.py test

Available commands are in distutilazy.command package as separate modules.

A more detailed way is to use command classes, defined in distutilazy package modules. Each module might define
more than a single command class.

The modules should be imported in setup.py, then desired classes might be assigned to command names using the ``cmdclass`` parameter.

::

    import distutilazy.clean

    setup(
        cmdclass: {'clean_pyc': distutilazy.clean.clean_pyc}
    )

License
-------
Distutilazy is released under the terms of `MIT license <http://opensource.org/licenses/MIT>`_.
