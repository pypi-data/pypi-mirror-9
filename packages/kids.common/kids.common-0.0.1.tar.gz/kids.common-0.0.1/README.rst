=========================
kids.common
=========================

.. image:: http://img.shields.io/pypi/v/kids.common.svg?style=flat
   :target: https://pypi.python.org/pypi/kids.common/
   :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/kids.common.svg?style=flat
   :target: https://pypi.python.org/pypi/kids.common/
   :alt: Number of PyPI downloads

.. image:: http://img.shields.io/travis/0k/kids.common/master.svg?style=flat
   :target: https://travis-ci.org/0k/kids.common/
   :alt: Travis CI build status

.. image:: http://img.shields.io/coveralls/0k/kids.common/master.svg?style=flat
   :target: https://coveralls.io/r/0k/kids.common
   :alt: Test coverage



``kids.common`` is a Python library providing helpers when writing command
line utilities in python.

It's part of 'Kids' (for Keep It Dead Simple) library.


Maturity
========

This code is in alpha stage. It wasn't tested on Windows. API may change.
This is more a draft for an ongoing reflection.

And I should add this is probably not ready to show. Although, a lot of these
function are used everyday in my projects and I got sick rewritting them for
every project.


Features
========

using ``kids.common``:

- TBD


Compatibility
=============

Tis code is python2 and python3 ready. It wasn't tested on windows.


Installation
============

You don't need to download the GIT version of the code as ``kids.common`` is
available on the PyPI. So you should be able to run::

    pip install kids.common

If you have downloaded the GIT sources, then you could add install
the current version via traditional::

    python setup.py install

And if you don't have the GIT sources but would like to get the latest
master or branch from github, you could also::

    pip install git+https://github.com/0k/kids.common

Or even select a specific revision (branch/tag/commit)::

    pip install git+https://github.com/0k/kids.common@master


Usage
=====

TBD


Contributing
============

Any suggestion or issue is welcome. Push request are very welcome,
please check out the guidelines.


Push Request Guidelines
-----------------------

You can send any code. I'll look at it and will integrate it myself in
the code base and leave you as the author. This process can take time and
it'll take less time if you follow the following guidelines:

- check your code with PEP8 or pylint. Try to stick to 80 columns wide.
- separate your commits per smallest concern.
- each commit should pass the tests (to allow easy bisect)
- each functionality/bugfix commit should contain the code, tests,
  and doc.
- prior minor commit with typographic or code cosmetic changes are
  very welcome. These should be tagged in their commit summary with
  ``!minor``.
- the commit message should follow gitchangelog rules (check the git
  log to get examples)
- if the commit fixes an issue or finished the implementation of a
  feature, please mention it in the summary.

If you have some questions about guidelines which is not answered here,
please check the current ``git log``, you might find previous commit that
would show you how to deal with your issue.


License
=======

Copyright (c) 2015 Valentin Lab.

Licensed under the `BSD License`_.

.. _BSD License: http://raw.github.com/0k/kids.common/master/LICENSE
