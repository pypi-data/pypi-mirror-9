UnitTest to Canopsis connector
=========================

.. image:: https://travis-ci.org/linkdd/unittest2canopsis.svg?branch=master


This package provides a connector which will executes Python unittest to generate
events for Canopsis.

Usage
-----

In this example, we will use the following test (as ``mytest.py``):

.. code-block:: python

   # -*- coding: utf-8 -*-

   import unittest


   class MyTestCase(unittest.TestCase):
       def test_success(self):
           self.assertTrue(True)

       def test_fail(self):
           self.assertFalse(True)


   if __name__ == '__main__':
       unittest.main()

Run the unittest on :

.. code-block::

   $ unittest2canopsis -t mytest.py -n mytest0 -a "amqp://guest:guest@localhost:5672/"
   unittest.mytest0.check.resource.MyTestCase.test_fail... FAIL
   unittest.mytest0.check.resource.MyTestCase.test_success... OK

You can also use a JSON configuration file :

.. code-block:: javascript

   {"tcp2canopsis": {
       "test": "mytest.py",
       "testname": "mytest0",
       "amqp": "amqp://guest:guest@localhost:5672/"
   }}

And load the file using :

.. code-block::

   $ unittest2canopsis -c path/to/config.json

Example of generated events :

.. code-block:: javascript

   {
     "timestamp": 1418206046,
     "connector": "unittest",
     "connector_name": "mytest0",
     "event_type": "check",
     "source_type": "resource",
     "component": "MyTestCase",
     "resource": "test_fail",
     "state": 2,
     "state_type": 1,
     "output": "Traceback (most recent call last):\n  File \"mytest.py\", line 11, in test_fail\n    self.assertFalse(True)\nAssertionError: True is not false\n"
   }
   {
     "timestamp": 1418206046,
     "connector": "unittest",
     "connector_name": "mytest0",
     "event_type": "check",
     "source_type": "resource",
     "component": "MyTestCase",
     "resource": "test_success",
     "state": 0,
     "state_type": 1,
     "output": "OK"
   }

Installation
------------

Just type :

.. code-block::

   $ pip install unittest2canopsis

Or, to install it in a locally :

.. code-block::

   $ ./makefile

This will create a virtual Python environment in the current folder, and install the dependencies listed by ``requirements.txt``.
Finally, it will perform a ``python setup.py install``.

After executing this script, the connector will be available in the current folder (which is now a virtual Python environment).
