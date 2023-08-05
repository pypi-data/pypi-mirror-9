=========================================================
Morris - an announcement (signal/event) system for Python
=========================================================

.. image:: https://badge.fury.io/py/morris.png
    :target: http://badge.fury.io/py/morris

.. image:: https://travis-ci.org/zyga/morris.png?branch=master
        :target: https://travis-ci.org/zyga/morris

.. image:: https://pypip.in/d/morris/badge.png
        :target: https://pypi.python.org/pypi/morris

Features
========

* Free software: LGPLv3 license
* Documentation: https://morris.readthedocs.org.
* Create signals with a simple decorator :class:`morris.signal`
* Send signals by calling the decorated method or function
* Connect to and disconnect from signals with :meth:`morris.signal.connect()`
  and :meth:`morris.signal.disconnect()`.
* Test your code with :meth:`morris.SignalTestCase.watchSignal()`,
  :meth:`morris.SignalTestCase.assertSignalFired()`,
  :meth:`morris.SignalTestCase.assertSignalNotFired()`
  and :meth:`morris.SignalTestCase.assertSignalOrdering()`





History
=======

1.2 (2015-02-030
----------------
* Merge backwards compatibility features for Plainbox migration.
  (signal_name, SignalInterceptorMixIn)
* Fix a bug in signal.__repr__()
* Document internals better

1.1 (2015-02-02)
----------------

* Merge ``Signal`` and ``signal`` into one class.
* Make ``Signal`` an alias of ``signal``.
* Make ``Signal.define`` an alias of ``signal``.
* Fix signal support on standalone functions
  (https://github.com/zyga/morris/issues/1)
* Add more documentation and tests
* Enable travis-ci.org integration

1.0 (2014-09-21)
----------------

* First release on PyPI.


2012-2014
---------

* Released on PyPI as a part of plainbox as ``plainbox.impl.signal``


