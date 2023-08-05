Python SMPP
===========

An SMPP version 3.4 library written in Python, suitable for use in Twisted_.

|travis|_ |coveralls|_


To get started with development::

    $ virtualenv --no-site-packages ve/
    $ source ve/bin/activate
    (ve)$ pip install -r requirements.pip
    (ve)$ python
    >>> import smpp
    >>>

Run the tests with nose

    (ve)$ nosetests

.. _Twisted: http://www.twistedmatrix.com
.. |travis| image:: https://travis-ci.org/praekelt/python-smpp.png?branch=develop
.. _travis: https://travis-ci.org/praekelt/python-smpp

.. |coveralls| image:: https://coveralls.io/repos/praekelt/python-smpp/badge.png?branch=develop
.. _coveralls: https://coveralls.io/r/praekelt/python-smpp
