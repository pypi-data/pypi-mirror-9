edeposit.amqp.downloader
====================

This module is basically just simple worker, which listens at AMQP queue and
asynchronously downloads data from internet. Downloaded data are then returned
as AMQP structure.

API
---

.. toctree::
    :maxdepth: 1

    /api/downloader
    /api/downloader.downloader
    /api/downloader.structures

AMQP communication
------------------

.. toctree::
    :maxdepth: 1

    /api/downloader.structures.requests
    /api/downloader.structures.responses


Installation
------------
Installation at debian systems is really easy::

    pip install edeposit.amqp.downloader


Source code
-----------
This project is released as opensource (GPL) and source codes can be found at
GitHub:

- https://github.com/edeposit/edeposit.amqp.downloader


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`