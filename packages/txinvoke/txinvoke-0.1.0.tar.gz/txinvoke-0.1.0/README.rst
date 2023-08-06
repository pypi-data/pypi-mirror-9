txinvoke
========

|PyPI package| |PyPI downloads| |License|

Run inline callbacks from ``Twisted`` as ``Invoke`` tasks.

Installation
------------

.. code-block:: bash

    pip install txinvoke


Example
-------

.. code-block:: python

    # -*- coding: utf-8 -*-
    # tasks.py

    import time
    import txmongo

    from txinvoke import task_on_callbacks


    @task_on_callbacks(name='test_task')
    def example(verbose=False):
        connection = yield txmongo.MongoConnection()
        test_collection = connection.db.test

        for x in range(10000):
            data = x * time.time()
            doc = {'something': data}
            yield test_collection.insert(doc, safe=True)

            if verbose:
                print("Test data '{data}' was inserted".format(data=data))


Caveats
-------

Sorry, but tasks chaining **will NOT** work currently.


.. |PyPI package| image:: http://img.shields.io/pypi/v/txinvoke.svg?style=flat
   :target: http://badge.fury.io/py/txinvoke/
.. |PyPI downloads| image:: http://img.shields.io/pypi/dm/txinvoke.svg?style=flat
   :target: https://crate.io/packages/txinvoke/
.. |License| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat
   :target: https://github.com/oblalex/txinvoke/blob/master/LICENSE
