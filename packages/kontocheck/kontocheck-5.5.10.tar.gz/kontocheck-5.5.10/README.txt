kontocheck
==========

Python ctypes wrapper of the konto_check library.

This module is based on konto_check_, a small library to check German
bank accounts. It implements all check methods and IBAN generation
rules, published by the German Central Bank.

In addition it provides access to the SCL Directory and the possibility
to verify VAT-IDs by the German Federal Central Tax Office.

.. _konto_check: http://kontocheck.sourceforge.net


Example
-------

.. sourcecode:: python
    
    import kontocheck
    kontocheck.lut_load()
    bankname = kontocheck.get_name('37040044')
    iban = kontocheck.create_iban('37040044', '532013000')
    kontocheck.check_iban(iban)
    bic = kontocheck.get_bic(iban)
    bankname = kontocheck.scl_get_bankname('VBOEATWW')


Changelog
---------

v5.5.10
    - Made the package Py2/3 compatible.
    - Now textual return values are always unicode strings.

v5.5.6
    - Bug fix querying the SCL Directory

v5.5.5
    - Updated the LUT data file
    - Updated the SCL Directory

v5.5.4
    - Fixed a bug in setup.py

v5.5.3
    - Normalized BIC in scl_* functions

v5.5.2
    - Added the SCL Directory, published by the German Central Bank
    - Added some functions to query the SCL Directory.
    - Added functionality to check VAT-IDs for validity.

v5.5.1
    - Minor bug fixes
    
v5.5.0
    - Updated the konto_check library to version 5.5
    - Fixed a bug on Windows using the wrong MSVCRT version.

v5.4.2
    - Updated the LUT data file since it contained an invalid BIC

v5.4.1
    - Fixed a bug on Windows systems, failed to load msvcrt

v5.4.0
    - Updated the konto_check library to version 5.4

v5.3.0
    - Updated the konto_check library to version 5.3
    - Fixed a bug in function get_name that did not recognize an IBAN.

v5.2.1
    - Replaced Cython with ctypes, since it is easier to maintain for different plattforms.
