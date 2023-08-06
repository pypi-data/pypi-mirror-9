register
========


.. image:: https://travis-ci.org/areku/register.svg
    :target: https://travis-ci.org/areku/register

Python Module for providing a simple register for function and classes with support of meta data.

.. code-block::
    Author: Alexander Weigl
    License: MIT

Getting Started
---------------

Install with pip::

    $ pip install --user register


Use it::

>>> from register import Registry
>>> r = Registry()
>>> @r
>>> def abc(): pass
>>> r.lookup("abc")
