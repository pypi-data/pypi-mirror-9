robotframework-jalali
====================

This module allows easy to create JALALI Date in any format you want.



Installation
------------

``pip install robotframework-jalali``

Usage
-----
`jalaliLibrary keyword
documentation <http://samira-esnaashari.github.io/robotframework-jalali/>`__

.. code:: robotframework

    *** Settings ***
    Library     jalaliLibrary

    *** Test Cases ***
    Get Today jalaliDate
        ${Date}=   today date
        log     ${Date}     console=True


    Get Today jalaliDate with special format
        ${Date}=   today date   %y.%m.%d
        log     ${Date}     console=True



    *** Keywords ***


Contribute
----------

If you like this module, please contribute! I welcome patches,
documentation, issues, ideas, and so on.