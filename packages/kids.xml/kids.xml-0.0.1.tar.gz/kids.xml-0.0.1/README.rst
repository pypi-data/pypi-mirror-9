=========================
kids.xml
=========================

.. image:: http://img.shields.io/pypi/v/kids.xml.svg?style=flat
   :target: https://pypi.python.org/pypi/kids.xml/
   :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/kids.xml.svg?style=flat
   :target: https://pypi.python.org/pypi/kids.xml/
   :alt: Number of PyPI downloads

.. image:: http://img.shields.io/travis/0k/kids.xml/master.svg?style=flat
   :target: https://travis-ci.org/0k/kids.xml/
   :alt: Travis CI build status

.. image:: http://img.shields.io/coveralls/0k/kids.xml/master.svg?style=flat
   :target: https://coveralls.io/r/0k/kids.xml
   :alt: Test coverage



``kids.xml`` is a Python library providing helpers when writing xml
thingy in python.

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

using ``kids.xml``:

- ``xml2string`` that actually works.


Compatibility
=============

Tis code is python2 and python3 ready. It wasn't tested on windows.


Installation
============

You don't need to download the GIT version of the code as ``kids.xml`` is
available on the PyPI. So you should be able to run::

    pip install kids.xml

If you have downloaded the GIT sources, then you could add install
the current version via traditional::

    python setup.py install

And if you don't have the GIT sources but would like to get the latest
master or branch from github, you could also::

    pip install git+https://github.com/0k/kids.xml

Or even select a specific revision (branch/tag/commit)::

    pip install git+https://github.com/0k/kids.xml@master


Usage
=====

::

    >>> from kids.file import tmpfile, rm
    >>> f = tmpfile('<a x="2">Hi</a>')

load
----

Will load content fromn an xml file::


    >>> from kids.xml import load

    >>> xml = load(f)
    >>> rm(f)
    >>> xml
    <Element a at ...>


xml2string
----------

Will output as string the content of an XML object (ElementTree from lxml)::

    >>> from __future__ import print_function
    >>> from kids.xml import xml2string

    >>> print(xml2string(xml))
    <?xml version="1.0" encoding="utf-8"?>
    <a x="2">Hi</a>

Note that the content is linted.


xmlize
------

Will parse a string and return the XML ElementTree::

    >>> from kids.xml import xmlize

    >>> xmlize('<a x="2">Hi</a>')
    <Element a at ...>

quote
-----

You can use ``kids.xml`` as a simple shortcut for handy xml functions::

    >>> from kids.xml import quote_attr, quote_value

If you have to insert values into attribute you could use this to quote it::

    >>> print(quote_attr("It's called \"Smith & Wesson\""))
    "It's called &quot;Smith &amp; Wesson&quot;"

And if you have to insert plain text into XML, you could use this::

    >>> print(quote_value("It's called \"Smith & Wesson\""))
    It's called "Smith &amp; Wesson"


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

.. _BSD License: http://raw.github.com/0k/kids.xml/master/LICENSE
