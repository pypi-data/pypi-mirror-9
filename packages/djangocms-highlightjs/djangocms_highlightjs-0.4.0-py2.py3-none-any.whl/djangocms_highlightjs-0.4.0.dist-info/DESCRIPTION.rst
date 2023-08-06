=====================
djangocms-highlightjs
=====================

.. image:: https://badge.fury.io/py/djangocms-highlightjs.png
    :target: http://badge.fury.io/py/djangocms-highlightjs

.. image:: https://travis-ci.org/nephila/djangocms-highlightjs.png?branch=master
        :target: https://travis-ci.org/nephila/djangocms-highlightjs

.. image:: https://pypip.in/d/djangocms-highlightjs/badge.png
        :target: https://pypi.python.org/pypi/djangocms-highlightjs

.. image:: https://coveralls.io/repos/nephila/djangocms-highlightjs/badge.png?branch=master
        :target: https://coveralls.io/r/nephila/djangocms-highlightjs?branch=master


highlight.js plugin for django CMS 3.0

Documentation
-------------

The full documentation is at http://djangocms-highlightjs.rtfd.org.

Quickstart
----------

#. Install djangocms-highlightjs::

    pip install djangocms-highlightjs

#. Add to INSTALLED_APPS::

    'djangocms_highlightjs',

#. Update the database schema::

    $ python manage migrate djangocms_highlightjs

#. Add "**highlight.js code**" plugin to your placeholders

Features
--------

* Use `highlight.js`_ to do syntax highlighting on provided code


.. _highlight.js: http://highlightjs.org/


.. image:: https://d2weczhvl823v0.cloudfront.net/nephila/djangocms-highlightjs/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free




History
-------

0.3.1 (2014-09-16)
++++++++++++++++++

* Fix security issue.

0.3.0 (2014-09-15)
++++++++++++++++++

* Add icon when plugin is used in text plugin.
* Switch to djangocms-helper for tests.
* Officially supports python 3.


0.2.0 (2014-04-21)
++++++++++++++++++

* Support for django CMS 3 final.

0.1.0 (2014-02-02)
++++++++++++++++++

* First release on PyPI.


