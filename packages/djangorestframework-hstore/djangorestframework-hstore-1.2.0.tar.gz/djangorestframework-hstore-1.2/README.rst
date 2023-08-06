Django Rest Framework HStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://travis-ci.org/djangonauts/django-rest-framework-hstore.png
   :target: https://travis-ci.org/djangonauts/django-rest-framework-hstore

.. image:: https://coveralls.io/repos/djangonauts/django-rest-framework-hstore/badge.png
  :target: https://coveralls.io/r/djangonauts/django-rest-framework-hstore

.. image:: https://landscape.io/github/djangonauts/django-rest-framework-hstore/master/landscape.png
   :target: https://landscape.io/github/djangonauts/django-rest-framework-hstore/master
   :alt: Code Health

.. image:: https://requires.io/github/djangonauts/django-rest-framework-hstore/requirements.png?branch=master
   :target: https://requires.io/github/djangonauts/django-rest-framework-hstore/requirements/?branch=master
   :alt: Requirements Status

.. image:: https://badge.fury.io/py/djangorestframework-hstore.png
   :target: https://pypi.python.org/pypi/djangorestframework-hstore

.. image:: https://pypip.in/d/djangorestframework-hstore/badge.png
   :target: https://pypi.python.org/pypi/djangorestframework-hstore

------------

Django Rest Framework tools for `django-hstore <https://github.com/djangonauts/django-hstore>`__.

Tribute to `Nodeshot <https://github.com/ninuxorg/nodeshot>`__
==============================================================

This code was originally written for `Nodeshot <https://github.com/ninuxorg/nodeshot>`__
and then extracted into this generic python package.

Compatibility with DRF, Django and Python
=========================================

==================  =========== ====================== ================ ================
DRF-hstore version  DRF version django-hstore version  Django version   Python version
**1.2**             **3.1.x**   **1.3.1** to **1.3.5** **1.6**, **1.7** **2.7**, **3.4**
**1.1**             **2.4.x**   **1.3.1** to **1.3.5** **1.6**, **1.7** **2.7**, **3.4**
**1.0**             **2.4.x**   **1.3.1** to **1.3.5** **1.6**, **1.7** **2.7**, **3.4**
==================  =========== ====================== ================ ================

Install
=======

.. code-block:: bash

    pip install djangorestframework-hstore

HStoreField Usage
=================

This field is not sufficient to support **django-hstore** ``schema-mode``.

.. code-block:: python

    from rest_framework import serializers
    from myapp.models import MyModel

    # rest_framework_hstore
    from rest_framework_hstore.fields import HStoreField

    class MyHStoreSerializer(serializers.ModelSerializer):
        data = HStoreField()

        class Meta:
            model = MyModel


HStoreSerializer Usage
======================

Supports **django-hstore** ``DictionaryField`` and ``schema-mode`` out of the box.

Prefer this to ``HStoreField``.

.. code-block:: python

    from myapp.models import MyModel

    # rest_framework_hstore
    from rest_framework_hstore.serializers import HStoreSerializer

    class MyHStoreSerializer(HStoreSerializer):
        class Meta:
            model = MyModel

Contributing
------------

1. Join the `Django REST Framework HStore Mailing
   List <http://bit.ly/1OUTLH6>`__
   and announce your intentions
2. Follow the `PEP8 Style Guide for Python
   Code <http://www.python.org/dev/peps/pep-0008/>`__
3. Fork this repo
4. Write code
5. Write tests for your code
6. Ensure all tests pass
7. Ensure test coverage is not under 90%
8. Document your changes
9. Send pull request

BSD License
===========
Copyright (C) 2014 Federico Capoano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
