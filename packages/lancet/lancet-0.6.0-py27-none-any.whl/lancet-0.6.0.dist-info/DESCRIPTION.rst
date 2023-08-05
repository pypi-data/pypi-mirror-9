======
LANCET
======

.. image:: https://badge.fury.io/py/lancet.png
   :target: http://badge.fury.io/py/lancet

.. image:: https://pypip.in/d/lancet/badge.png
   :target: https://crate.io/packages/lancet?version=latest

.. image:: https://travis-ci.org/GaretJax/lancet.png?branch=master
   :target: https://travis-ci.org/GaretJax/lancet

.. image:: https://readthedocs.org/projects/lancet/badge/?version=latest
   :target: http://lancet.readthedocs.org/en/latest/

.. image:: https://requires.io/github/GaretJax/lancet/requirements.svg?branch=master
   :target: https://requires.io/github/GaretJax/lancet/requirements/?branch=master
   :alt: Requirements Status

>From http://en.wikipedia.org/wiki/Scalpel:

    A scalpel, or lancet, is a small and extremely sharp bladed instrument used
    for surgery, anatomical dissection, and various arts and crafts (called a
    hobby knife).

Lancet is a command line utility to streamline the various activities related
to the development and maintenance of a software package.

* Free software: MIT license
* Documentation: http://lancet.rtfd.org


Installation
============

Check out the documentation_.

.. _documentation: http://lancet.readthedocs.org/en/latest/installation/


Getting started
===============

Once installed, set up the initial configuration by running::

   lancet setup

For each not-yet-configured project, you can then run::

   cd path/to/project
   lancet init

This creates a new project-level configuration file that can be shared across
different users (and thus commited to source control).

Install dev version
===================

::

   ~/.local/venvs/lancet/bin/pip uninstall lancet
   ~/.local/venvs/lancet/bin/pip install https://github.com/GaretJax/lancet/archive/master.zip


TODO
====

A lot of commands are still missing, as for example:

* ``review``: to streamline the whole reviewing process (pulling, linting,\
  diffs,...).
* ``merge``: to help in getting a more strict merge process in place (and
  cleanup afterwards). Can include rebasing helpers.
* Other issue tracker/Harvest interaction utilities (``list``, ``search``,
  ``comment``, ...)


=======
History
=======

0.6.0 - 2015-01-19
==================

* Added support for pluggable Harvest task/project mapper.
* Added support for epics based time tracking.
* Added support for pluggable branch naming backends.
* Added support for different branch prefixes based on issue type.
* Added URL hints to ``lancet setup``.
* Fix assignee comparison bug.
* More robust support for flawed versions of the git ``osxkeychain``
  credentials helper.
* Increase the slug length in branch names to 50 chars.
* Built in support for debugging exceptions.


0.5.1 - 2015-01-13
==================

* Coerce config values to int when calling `init`.


0.5.0 – 2015-01-05
==================

* Include all resources in the distribution.
* Cleanup docker-related leftovers.
* Added a ``pr`` command to automate pull requests creation.
* The ``logout`` command can now logout from a single service.

0.4.2 – 2015-01-05
==================

* Fix ``python-slugify`` requirement.


0.4.1 – 2015-01-05
==================

* Update requirements.


0.4 – 2015-01-05
================

.. warning::

   If your setup includes remote configured to be accessed over SSH, you may
   need to reinstall ``libgit2`` with ``brew reinstall libgit2 --with-libssh2``.

* Added facilities to integrate with the current shell, for stuff like cd'ing
  to other directories or activating virtual environments.
* Added a ``--version`` option to ``lancet``.
* Fetch latest changes from origin before creating new working branches (#1).
* Added an ``activate`` command to ``cd`` to the project directory and
  (optionally) activate a virtual environment.
* Added the ``harvest-projects`` and ``harvest-tasks`` commands to list
  projects/tasks IDs from Harvest.
* Added an ``init`` command to create project-level configuration files (#2).


0.3 – 2014-12-30
================

* Handle unassigned issues (#5).
* Avoid logging out the web user when accessign the JIRA API (#4).
* Initial documentation stub (#3).


