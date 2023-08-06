=========================
kids.sh
=========================


.. image:: http://img.shields.io/pypi/v/kids.sh.svg?style=flat
   :target: https://pypi.python.org/pypi/kids.sh/
   :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/kids.sh.svg?style=flat
   :target: https://pypi.python.org/pypi/kids.sh/
   :alt: Number of PyPI downloads

.. image:: http://img.shields.io/travis/0k/kids.sh/master.svg?style=flat
   :target: https://travis-ci.org/0k/kids.sh/
   :alt: Travis CI build status

.. image:: http://img.shields.io/coveralls/0k/kids.sh/master.svg?style=flat
   :target: https://coveralls.io/r/0k/kids.sh
   :alt: Test coverage


``kids.sh`` is a Python library providing helpers when calling shell
commands thanks to python. It's part of 'Kids' (for Keep It Dead Simple)
library.


Maturity
========

This is Alpha release. More a place to store common librairies. Will
perhaps evolve into something more consistent.

It is, for now, a very humble package.


Features
========

using ``kids.sh``:

- Call ``wrap()`` when you want to call a system command and you don't
  have to bother about subprocess and other stuff. You get the standard
  output of the command as the return string.

These assumptions are in the code:

- You don't want to deal with precise subprocess things, don't really need to
  care about security (because system command you launch are hard-written).
- You don't need asynchronous code.


Installation
============

You don't need to download the GIT version of the code as ``kids.sh`` is
available on the PyPI. So you should be able to run::

    pip install kids.sh

If you have downloaded the GIT sources, then you could add install
the current version via traditional::

    python setup.py install

And if you don't have the GIT sources but would like to get the latest
master or branch from github, you could also::

    pip install git+https://github.com/0k/kids.sh

Or even select a specific revision (branch/tag/commit)::

    pip install git+https://github.com/0k/kids.sh/colour@master


Usage
=====


More documentation is available in the code.


Wrap
----

If command doesn't fail, standard output is returned::

    >>> from __future__ import print_function

    >>> from kids.sh import wrap
    >>> print(wrap('test "$HELLO" && echo "foo" || echo "bar"'))
    bar


But if command fails, then a special ShellError exception is casted::

    >>> wrap('test "$HELLO" && echo "foo" || { echo "bar" ; false ; }')
    Traceback (most recent call last):
    ...
    ShellError: Wrapped command returned with unexpected errorlevel.
      command: 'test "$HELLO" && echo "foo" || { echo "bar" ; false ; }'
      errlvl: 1
      stdout:
      | bar


cmd
---

If you would rather want to get all information from the command, you can
use ``cmd``::

    >>> from kids.sh import cmd

    >>> cmd('test "$HELLO" && echo "foo" || { echo "bar" ; false ; }')
    ShellOutput(out=...'bar\n', err=...'', errlvl=1)

So, notice it doesn't cast any exception, but outputs a named tuple.


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

.. _BSD License: http://raw.github.com/0k/kids.sh/master/LICENSE
