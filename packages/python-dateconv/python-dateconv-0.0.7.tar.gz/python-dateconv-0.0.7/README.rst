python-dateconv
------------------



.. image:: https://api.travis-ci.org/WarmongeR1/python-dateconv.png
    :target: https://travis-ci.org/WarmongeR1/python-dateconv

.. image:: https://coveralls.io/repos/WarmongeR1/python-dateconv/badge.png
    :target: https://coveralls.io/r/WarmongeR1/python-dateconv

.. image:: https://pypip.in/v/python-dateconv/badge.png
    :target: https://pypi.python.org/pypi/python-dateconv

.. image:: https://pypip.in/d/python-dateconv/badge.png
    :target: https://pypi.python.org/pypi/python-dateconv
    
.. image:: https://readthedocs.org/projects/python-dateconv/badge/?version=latest
    :target: https://readthedocs.org/projects/python-dateconv/?badge=latest
    :alt: Documentation Status

Description
--------------

Simple package for convert time between types


Usage
-----

.. code-block:: bash

    $ pip install python-dateconv


.. code-block:: python

    from dateconv import *
    
    human_time = '2015-01-01 18:21:26'
    datetime_time = datetime.datetime(2015, 1, 1, 18, 21, 26)
    my_unix_time = 1420136486
    
    print(d2u(datetime_time))
    # 1420114886
    
    print(d2h(datetime_time))
    # 2015-01-01 18:21:26
    
    print(h2u(human_time))
    # 1420114886
    
    print(type(h2d(human_time)))
    # <type 'datetime.datetime'>
    
    print(u2h(my_unix_time))
    # 2015-01-01 18:21:26
    
    print(type(u2d(my_unix_time)))
    # <type 'datetime.datetime'>
