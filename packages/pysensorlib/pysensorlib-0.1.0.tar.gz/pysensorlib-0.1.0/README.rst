pySensorLib
===========

.. image:: https://travis-ci.org/MIT-CityFARM/pysensorlib.svg?branch=master
    :target: https://travis-ci.org/MIT-CityFARM/pysensorlib
    :alt: Build

.. image:: https://pypip.in/version/pysensorlib/badge.svg
    :target: https://pypi.python.org/pypi/pysensorlib/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/pysensorlib/badge.svg
    :target: https://pypi.python.org/pypi/pysensorlib/
    :alt: Supported Python versions

A python module for reading from sensors. Abstracts the specifics of the sensor
hardware and communication protocol and provides a general API for reading from
sensors of all types.

Currently, only serial sensors are supported, but the design allows for
the addition of different sensor types with different read interfaces.
