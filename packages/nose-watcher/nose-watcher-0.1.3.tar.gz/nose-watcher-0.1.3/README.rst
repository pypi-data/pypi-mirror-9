===============================
Nose-Watcher
===============================

.. image:: https://pypip.in/version/nose-watcher/badge.png
        :target: https://pypi.python.org/pypi/nose-watcher/
        :alt: Latest Version

.. image:: https://pypip.in/d/nose-watcher/badge.png
        :target: https://pypi.python.org/pypi/nose-watcher

.. image:: https://pypip.in/wheel/nose-watcher/badge.png
        :target: https://pypi.python.org/pypi/nose-watcher/
        :alt: Wheel Status

.. image:: https://travis-ci.org/solarnz/nose-watcher.png?branch=develop
        :target: https://travis-ci.org/solarnz/nose-watcher

.. image:: https://coveralls.io/repos/solarnz/nose-watcher/badge.png?branch=develop
        :target: https://coveralls.io/r/solarnz/nose-watcher?branch=develop

.. image:: https://pypip.in/license/nose-watcher/badge.png
        :target: https://pypi.python.org/pypi/nose-watcher/
        :alt: License


A nose plugin to watch for changes within the local directory.

* Free software: BSD license
* Documentation: http://nose-watcher.readthedocs.org.

Inspired by the `nose-watch <https://github.com/lukaszb/nose-watch>`_ nose
plugin.

Note: nose-watcher will only run on linux, due to the depenency on
`python-inotify` and `inotify`.

Features
--------

* Watches for changes in the local directory, then runs nosetests with the
  specified command line options.

* Doesn't run the tests multiple times if you're using vim, Unlike the similar
  plugin `nose-watch`.

* Specify additional filetypes to watch using the command line argument
  `--filetype`.


Installation
------------

.. code-block:: bash

    pip install nose-watcher

Usage
-----

.. code-block:: bash

    nosetests --with-watcher

    nosetests --with-watcher --filetype .txt

Additional Contributors
-----------------------

*  `Felix Chapman (aelred) <https://github.com/aelred>`_
