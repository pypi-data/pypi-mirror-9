adblockparser
=============

.. image:: https://img.shields.io/pypi/v/adblockparser.svg
   :target: https://pypi.python.org/pypi/adblockparser
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/l/adblockparser.svg
   :target: https://github.com/scrapinghub/adblockparser/blob/master/LICENSE.txt
   :alt: License

.. image:: https://img.shields.io/travis/scrapinghub/adblockparser/master.svg
   :target: https://travis-ci.org/scrapinghub/adblockparser
   :alt: Build Status


``adblockparser`` is a package for working with `Adblock Plus`_ filter rules.
It can parse Adblock Plus filters and match URLs against them.

.. _Adblock Plus: https://adblockplus.org

Installation
------------

::

    pip install adblockparser

If you plan to use this library with a large number of filters
installing pyre2_ library is highly recommended: the speedup
for a list of default EasyList_ filters can be greater than 1000x.
Version from github is required::

    pip install git+https://github.com/axiak/pyre2.git#egg=re2

.. _pyre2: https://github.com/axiak/pyre2
.. _EasyList: https://easylist.adblockplus.org/en/

Usage
-----

To learn about Adblock Plus filter syntax check these links:

* https://adblockplus.org/en/filter-cheatsheet
* https://adblockplus.org/en/filters


1. Get filter rules somewhere: write them manually, read lines from a file
   downloaded from EasyList_, etc.::

       >>> raw_rules = [
       ...     "||ads.example.com^",
       ...     "@@||ads.example.com/notbanner^$~script",
       ... ]

2. Create ``AdblockRules`` instance from rule strings::

       >>> from adblockparser import AdblockRules
       >>> rules = AdblockRules(raw_rules)

3. Use this instance to check if an URL should be blocked or not::

       >>> rules.should_block("http://ads.example.com")
       True

   Rules with options are ignored unless you pass a dict with options values::

       >>> rules.should_block("http://ads.example.com/notbanner")
       True
       >>> rules.should_block("http://ads.example.com/notbanner", {'script': False})
       False
       >>> rules.should_block("http://ads.example.com/notbanner", {'script': True})
       True

Consult with Adblock Plus `docs <https://adblockplus.org/en/filters#options>`__
for options description. These options allow to write filters that depend
on some external information not available in URL itself.

Performance
-----------

Regex engines
^^^^^^^^^^^^^

``AdblockRules`` class creates a huge regex to match filters that
don't use options. pyre2_ library works better than stdlib's re
with such regexes. If you have pyre2_ installed then ``AdblockRules``
should work faster, and the speedup can be dramatic - more than 1000x
in some cases.

Sometimes pyre2 prints something like
``re2/dfa.cc:459: DFA out of memory: prog size 270515 mem 1713850`` to stderr.
Give re2 library more memory to fix that::

    >>> rules = AdblockRules(raw_rules, use_re2=True, max_mem=512*1024*1024)  # doctest: +SKIP

Make sure you are not using re2 0.2.20 installed from PyPI, it doesn't work.
Install it from the github repo.

Parsing rules with options
^^^^^^^^^^^^^^^^^^^^^^^^^^

Rules that have options are currently matched in a loop, one-by-one.
Also, they are checked for compatibility with options passed by user:
for example, if user didn't pass 'script' option (with a ``True`` or ``False``
value), all rules involving ``script`` are discarded.

This is slow if you have thousands of such rules. To make it work faster,
explicitly list all options you want to support in ``AdblockRules`` constructor,
disable skipping of unsupported rules, and always pass a dict with all options
to ``should_block`` method::

    >>> rules = AdblockRules(
    ...    raw_rules,
    ...    supported_options=['script', 'domain'],
    ...    skip_unsupported_rules=False
    ... )
    >>> options = {'script': False, 'domain': 'www.mystartpage.com'}
    >>> rules.should_block("http://ads.example.com/notbanner", options)
    False

This way rules with unsupported options will be filtered once, when
``AdblockRules`` instance is created.

Limitations
-----------

There are some known limitations of the current implementation:

* element hiding rules are ignored;
* matching URLs against a large number of filters can be slow-ish,
  especially if pyre2_ is not installed and many filter options are enabled;
* ``match-case`` filter option is not properly supported (it is ignored);
* ``document`` filter option is not properly supported;
* rules are not validated *before* parsing, so invalid rules may raise
  inconsistent exceptions or silently work incorrectly;
* regular expressions in rules are not supported.

It is possible to remove all these limitations. Pull requests are welcome
if you want to make it happen sooner!

Contributing
------------

* source code: https://github.com/scrapinghub/adblockparser
* issue tracker: https://github.com/scrapinghub/adblockparser/issues

In order to run tests, install `tox <http://tox.testrun.org>`_ and type

::

    tox

from the source checkout.

The license is MIT.
