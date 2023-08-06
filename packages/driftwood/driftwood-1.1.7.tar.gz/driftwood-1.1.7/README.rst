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

    pip install driftwood

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

`MongoHandler <http://driftwood.readthedocs.org/en/latest/driftwood.handlers.html#driftwood.handlers.mongo.MongoHandler>`_
=====================
This handler is used to log records to MongoDB.  The following code:

.. code-block:: python

    import logging
    import os

    from driftwood.handlers.mongo import MongoHandler, LogRecord
    import mongoengine

    mongoengine.connect("testdb", host=os.environ["MONGO_PORT_27017_TCP_ADDR"])
    MongoClient('172.17.0.50', 27017)

    mongo_handler = MongoHandler()
    log = logging.getLogger("test")
    log.addHandler(mongo_handler)

    log.error("something bad happened")
    print(LogRecord.objects)
    print(LogRecord.objects[0].message)

Produces:

.. code-block:: python

    [<LogRecord: LogRecord object>]
    something bad happened

Your message has been logged to mongodb and `includes all standard logging attributes except asctime. <http://driftwood.readthedocs.org/en/latest/driftwood.handlers.html#driftwood.handlers.mongo.BaseLogRecord>`_
See the full documentation for `including extra attributes <http://driftwood.readthedocs.org/en/latest/driftwood.handlers.html#driftwood.handlers.mongo.MongoHandler>`_, as provided by the `DictHandler <http://driftwood.readthedocs.org/en/latest/driftwood.handlers.html#driftwood.handlers.dict.DictHandler>`_ base class.

`StatusUpdateAdapter <http://driftwood.readthedocs.org/en/latest/driftwood.adapters.html#driftwood.adapters.status.StatusUpdateAdapter>`_
=========================
This logging.LoggerAdapter is used to track the status of an operation based on the level of messages being logged.
Every time a message is logged, if the level is higher than any previous message, a callback is triggered to alert of the status change.

.. code-block:: python

    import logging

    from driftwood.adapters import StatusUpdateAdapter

    def status_update(levelno, levelname):
        print("The status has changed to {0}".format(levelname))

    log = logging.getLogger("test")
    log.setLevel(logging.CRITICAL)
    adapter = StatusUpdateAdapter(status_update, log)

    adapter.info("info test")
    adapter.warning("warning test")
    adapter.error("error test")

    adapter.info("won't trigger the callback")

Produces::

    The status has changed to INFO
    The status has changed to WARNING
    The status has changed to ERROR


