=========
 IA Mine
=========
Internet Archive data mining tools.


What Is IA Mine?
================

IA Mine is a command line tool and Python 3 library for data mining
the Internet Archive. Note: documentation in progress.


How Do I Get Started?
=====================


Command Line Interface
----------------------

The IA Mine command line tool should work on any Unix-like operating
system that has Python 3 installed on it. To start using ``ia-mine``,
simply download one of the latest binaries from
`https://archive.org/details/iamine-pex
<https://archive.org/details/iamine-pex>`_.

Currently, ``ia-mine`` binaries are dependent on the Python 3 minor
version you have installed. For example, if you have Python 3.4
installed on your operating system, you would download an ``ia-mine``
py3.4 binary.

.. code:: bash

    # Download ia-mine and make it executable.
    $ curl -L https://archive.org/download/iamine-pex/ia-mine-0.1.3-py3.4.pex > ia-mine
    $ chmod +x ia-mine
    $ ./ia-mine -v
    0.1.3
    

Python Library
--------------

The IA Mine Python library can be installed with pip:

.. code:: bash

    # Create a Python 3 virtualenv, and install iamine.
    $ virtualenv --python=python3 venv
    $ . venv/bin/activate
    $ pip install iamine

This will also install the ``ia-mine`` comand line tool into your virtualenv:

.. code:: bash

    $ which ia-mine
    /home/user/venv/bin/ia-mine


Data Mining with IA Mine and jq
===============================

``ia-mine`` simply retrieves metadata and search results concurrently
from Archive.org, and dumps the JSON returned to stdout and any error
messages to stderr. Mining the JSON dumped to stdout can be done using a
tool like `jq <http://stedolan.github.io/jq/>`_, for example. jq
binaries can be downloaded at `http://stedolan.github.io/jq/download/
<http://stedolan.github.io/jq/download/>`_.


Mining Search Results
---------------------
