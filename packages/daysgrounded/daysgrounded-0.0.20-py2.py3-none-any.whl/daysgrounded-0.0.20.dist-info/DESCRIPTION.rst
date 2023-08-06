daysgrounded
============

*daysgrounded* allows you to manage your kid's grounded days (simple app for trying Python programming and testing procedures).

Although the code is OS independent, I'm only able to test it in console (Windows Cmd) and Windows GUI.

You shouldn't use this because it's just a fake app for allowing me to try Python programming and testing procedures.

**Features:**

* Saves a log file with all changes.
* Saves grounded days total per child and last update date.
* Allows changes in CLI and GUI (this last one has different widgets for the same function).

Installation
------------

.. code:: bash

    $ pip install daysgrounded

Usage
-----

.. code:: bash

    $ daysgrounded

Options
-------

.. code:: bash

    $ daysgrounded -h
    usage: daysgrounded [-option | child+/-days...]

    optional arguments:
      -h, --help            show this help message and exit
      -a, --auto            auto update based on date
      -v, --version         show version
      -l, --license         shows license
      child+/-days          eg. t+1 s-1

    No argument starts gui (graphical user interface).
    Maximum of 99 days.

Resources
---------

* `Repository <https://github.com/jcrmatos/daysgrounded>`_

Contributing
------------

1. Fork the `repository`_ on GitHub.
2. Make a branch of master and commit your changes to it.
3. Ensure that your name is added to the end of the AUTHORS.rst file using the format:
   ``Name <email@domain.com>``
4. Submit a Pull Request to the master branch on GitHub.

.. _repository: https://github.com/jcrmatos/daysgrounded


