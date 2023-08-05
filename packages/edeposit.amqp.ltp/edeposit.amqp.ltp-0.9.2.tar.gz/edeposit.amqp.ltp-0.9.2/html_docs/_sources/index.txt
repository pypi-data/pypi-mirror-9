edeposit.amqp.ltp
=================

This project provides AMQP bindings for LTP (Long Time Preservation) system
used in Czech National Library.

API
---
.. toctree::
    :maxdepth: 1

    /api/ltp

.. toctree::
    :maxdepth: 1

    /api/ltp.ltp
    /api/ltp.fn_composers
    /api/ltp.xslt_transformer
    /api/ltp.checksum_generator
    /api/ltp.mods_postprocessor

.. toctree::
    :maxdepth: 1

    /api/ltp.structures
    /api/ltp.settings

API relations graph
-------------------
.. image:: /_static/relations.png
    :width: 600px

AMQP connection
---------------
AMQP communication is handled by the
`edeposit.amqp <http://edeposit-amqp.readthedocs.org>`_ module, specifically by
the ``edeposit_amqp_ltpd.py`` script. Bindings to this project are handled by
:func:`.reactToAMQPMessage`.

Source code
-----------
This project is released as opensource (GPL) and source codes can be found at
GitHub:

- https://github.com/edeposit/edeposit.amqp.ltp

Installation
++++++++++++
Module is hosted at `PYPI <https://pypi.python.org/pypi/edeposit.amqp.ltp>`_,
and can be easily installed using
`PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_::

    sudo pip install edeposit.amqp.ltp

Testing
-------
Almost every feature of the project is tested in unit/integration tests. You
can run this tests using provided ``run_tests.sh`` script, which can be found
in the root of the project.

Requirements
++++++++++++
This script expects that pytest_ is installed. In case you don't have it yet,
it can be easily installed using following command::

    pip install --user pytest

or for all users::

    sudo pip install pytest

.. _pytest: http://pytest.org/

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`