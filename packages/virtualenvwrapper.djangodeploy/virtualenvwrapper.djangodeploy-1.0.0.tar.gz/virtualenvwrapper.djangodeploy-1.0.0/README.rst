================================
 virtualenvwrapper.djangodeploy
================================

virtualenvwrapper.djangodeploy is a template plugin for `virtualenvwrapper`_ to
create new a virtualenv for deploying a django project.  When used with
``mkproject``, it installs Django into the new virtualenv then runs ``django-
admin.py`` to create a new project skeleton.

Installation
============

::

  $ pip install virtualenvwrapper.djangodeploy

Usage
=====

::

  $ mkproject -t djangodeploy djangodeploy_test
  New python executable in djangodeploy_test/bin/python
  Installing setuptools, pip...done.
  Creating /Users/tino/Dev/projects/djangodeploy_test
  Setting project for djangodeploy_test to /Users/tino/Dev/projects/djangodeploy_test

  Applying template djangodeploy

  (djangodeploy_test)$ tree
  .
  ├── code
  ├── conf
  ├── log
  ├── media
  └── static

  5 directories, 0 files

.. _virtualenvwrapper: https://pypi.python.org/pypi/virtualenvwrapper
