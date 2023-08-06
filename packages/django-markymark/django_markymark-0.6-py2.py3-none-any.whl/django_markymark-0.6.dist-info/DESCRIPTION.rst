django-markymark
================

.. image:: https://badge.fury.io/py/django-markymark.png
    :target: http://badge.fury.io/py/django-markymark

.. image:: https://travis-ci.org/moccu/django-markymark.png?branch=master
    :target: https://travis-ci.org/moccu/django-markymark

.. image:: https://readthedocs.org/projects/django-markymark/badge/?version=latest
    :target: http://django-markymark.readthedocs.org/en/latest/

*django-markymark* provides helpers and tools to integrate markdown into your editor.

.. figure:: https://django-markymark.readthedocs.org/en/latest/_static/logo.gif


Features
========

 * Django form fields to integrate the bootstrap markdown editor (without the dependency on bootstrap)
 * `django-filer <https://github.com/stefanfoulis/django-filer>`_ integration
 * `django-anylink <https://github.com/moccu/django-anylink>`_ integration
 * Various extensions to provide `GitHub Flavored Markdown <https://help.github.com/articles/github-flavored-markdown/>`_


Resources
=========

* `Documentation <https://django-markymark.readthedocs.org/>`_
* `Bug Tracker <https://github.com/moccu/django-markymark/issues>`_
* `Code <https://github.com/moccu/django-markymark/>`_


Changelog
=========

0.6 (2015-03-09)
----------------

* Rework extensions to allow js/css files to be defined directly on each extension
* The return value of :func:`~markymark.utils.render_markdown` is now marked as safe
* Allow template-names to be overwritten
* Made settings easier to be overwritten, you can now
  import default settings from :mod:`markymark.defaults`
* Fixed contrib.anylink to avoid name clashes with other
  extensions named "link"
* Fix fullscreen icon integration

0.5 (2015-02-13)
----------------

* Removed anylink and filer extensions from being autoloaded.
* Removed dependency on floppyforms.


0.2..0.4 (2015-01-22)
---------------------

* General cleanups and bugfixes.


0.1 (2015-01-22)
----------------

* Initial release.


