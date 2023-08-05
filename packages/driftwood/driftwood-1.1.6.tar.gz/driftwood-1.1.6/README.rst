`Full Documentation <http://driftwood.readthedocs.org/en/latest/>`_

#########
Driftwood
#########
**A collection of python logging extensions**

Features
========
- Compatible with Python 3 (only)
- Provides Dictionary, JSON, and MongoDB logging
- Features for logging custom attributes
- Can notify of status changes based on the level of messages being logged

Get Driftwood
=============

.. code-block:: shell

    pip install git+https://github.com/HurricaneLabs/driftwood.git

Run the tests
=============
Assumes you have Driftwood already installed

.. code-block:: shell

    pip install nose2
    git clone https://github.com/HurricaneLabs/driftwood.git
    cd driftwood/test/unit
    nose2

Examples
--------

`JSON Formatter <http://driftwood.readthedocs.org/en/latest/driftwood.formatters.html#driftwood.formatters.json.JSONFormatter>`_
==============
This code example:

.. code-block:: python

    import logging
    from driftwood.formatters import JSONFormatter
    log = logging.getLogger("test")
    handler = logging.StreamHandler()
    json_formatter = JSONFormatter()
    handler.setFormatter(json_formatter)
    log.addHandler(handler)
    log.warning("uh oh")

Produces (as a string, not a dict):

.. code-block:: json

    {"created": 1422386241.4394472, "pathname": "<stdin>", "message": "uh oh", "threadName": "MainThread", "levelname": "WARNING", "process": 4384, "module": "<stdin>", "thread": 139785634490176, "levelno": 30, "msecs": 439.44716453552246, "filename": "<stdin>", "lineno": 1, "relativeCreated": 52455.650329589844, "funcName": "<module>", "name": "test"}

