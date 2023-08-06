.. contents::

Introduction
============

Extends dexterity.localroles:

* provides a principal selector field
* extends the configuration page

When giving local roles, the principal is selected by a field on the object.

The assignement is then different for each object following the selected principal.

This is a refactoring of collective.z3cform.rolefield.

Installation
============

* Add dexterity.localrolesfield to your eggs.
* Re-run buildout.
* Done.

Credits
=======

Have an idea? Found a bug? Let us know by `opening a ticket`_.

.. _`opening a ticket`: https://github.com/IMIO/dexterity.localrolesfield/issues


Tests
=====

This package is tested using Travis CI. The current status of the add-on is :

.. image:: https://api.travis-ci.org/IMIO/dexterity.localrolesfield.png
    :target: https://travis-ci.org/IMIO/dexterity.localrolesfield
