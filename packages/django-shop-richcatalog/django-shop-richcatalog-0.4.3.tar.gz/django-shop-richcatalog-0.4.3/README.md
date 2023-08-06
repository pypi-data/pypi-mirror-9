django-shop-richcatalog
=======================

A rich catalog plugin for django shop.

[![Build Status](https://travis-ci.org/nimbis/django-shop-richcatalog.svg?branch=master)](https://travis-ci.org/nimbis/django-shop-richcatalog)

[![Coverage](https://coveralls.io/repos/nimbis/django-shop-richcatalog/badge.png?branch=master)](https://coveralls.io/r/nimbis/django-shop-richcatalog?branch=master)


Requirements
------------

* django < 1.7
* django >= 1.5
* django-shop
* django-shop-richproduct


Installation
------------

* Run `pip install django-shop-richcatalog` or download this package and run `python setup.py install`

* Ensure that `django_shop_richcatalog` is in your INSTALLED APPS

* Run `syncdb` or `migrate django_shop_richcatalog` if you have South installed.

History
-------

v0.4.3:

    * Removing pip requirement from setup.py.

v0.1.0:

    * Initial version.
