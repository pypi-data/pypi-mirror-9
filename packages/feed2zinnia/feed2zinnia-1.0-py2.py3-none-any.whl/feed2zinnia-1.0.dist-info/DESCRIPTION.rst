==============
Feed to Zinnia
==============

Feed2zinnia is package allowing you to import from RSS or Atom feeds.

Installation
============

* Install the package on your system: ::

  $ pip install feed2zinnia

* Register the ``'zinnia_feed'`` in your ``INSTALLED_APPS``.

Importing from a feed
=====================

Simply run this command to start the importation on your blog. ::

  $ python manage.py feed2zinnia http://url.of/the/feed

For the options execute this. ::

  $ python manage.py help feed2zinnia


