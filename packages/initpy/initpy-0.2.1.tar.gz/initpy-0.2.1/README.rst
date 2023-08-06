initpy
======

.. image:: https://pypip.in/v/initpy/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/initpy/
   :alt: Latest Version
.. image:: https://readthedocs.org/projects/initpy/badge/?version=latest
   :target: http://initpy.readthedocs.org/en/latest/
   :alt: Documentation Status

Generate `Python`_ project.

.. _Python: https://www.python.org/


Installation
-------------

.. sourcecode:: bash

   ~ $ python setup.py install

or can use pip

.. sourcecode:: bash

   ~ $ pip install initpy


Quick start
-----------
Create single Python file.

.. sourcecode:: bash

   ~ $ init.py foo.py
   ~ $ cat foo.py
   #!/usr/bin/python
   # -*- coding:utf-8 -*-

Create Python Module.

.. sourcecode:: bash
   
   ~ $ init.py foo/
   ~ $ tree foo/
   foo/
   └── __init__.py

Create Flask project.

.. sourcecode:: bash
   
   ~ $ init.py -f bar
   ~ $ tree bar/
   bar/
    ├── app
    │   ├── __init__.py
    │   ├── common
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   └── views.py
    │   ├── static
    │   └── templates
    │       ├── base.html
    │       └── common
    │           └── index.html
    ├── manage.py
    └── requirements
        └── dev.txt

Create Tornado web project.

.. sourcecode:: bash
   
   ~ $ init.py -tw bar
   ~ $ tree bar/
   bar/
    ├── app.py
    ├── handlers
    │   ├── __init__.py
    │   └── common.py
    ├── requirements
    │   └── dev.txt
    └── urls.py

Create Falcon project.

.. sourcecode:: bash

   ~ $ init.py -fc bar
   ~ $ tree bar/
   bar/
    ├── app
    │   ├── __init__.py
    │   ├── resources
    │   │   ├── __init__.py
    │   │   └── common.py
    │   ├── middleware
    │   │   └── __init__.py
    │   └── models
    │       └── __init__.py
    ├── manage.py
    └── requirements
        └── dev.txt
