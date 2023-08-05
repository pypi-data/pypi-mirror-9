
Mocking Mirror
==============

* .. image:: https://pypip.in/version/mockingmirror/badge.svg?branch=master
    :target: https://pypi.python.org/pypi/mockingmirror/
    :alt: Latest Version

* .. image:: https://travis-ci.org/NegativeMjark/mockingmirror.svg?branch=master 
   :target: https://travis-ci.org/NegativeMjark/mockingmirror
   
* .. image:: https://img.shields.io/coveralls/NegativeMjark/mockingmirror.svg?branch=master
   :target: https://coveralls.io/r/NegativeMjark/mockingmirror?branch=master

Make strict mock objects using a mirror:

.. code:: python

    import mockingmirror

    mirror, mock = mockingmirror.mirror()

    # Create an object with a method that returns "Hello, World" when called
    mirror.myobject.mymethod()[:] = "Hello, World"
    assert mock.myobject.mymethod() == "Hello, World"
 
Install::

   pip install mockingmirror

