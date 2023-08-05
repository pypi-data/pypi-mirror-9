===============================
pycrunchbase
===============================

| |docs| |travis| |coveralls|
| |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/pycrunchbase/badge/?style=flat
    :target: https://readthedocs.org/projects/pycrunchbase
    :alt: Documentation Status

.. |travis| image:: http://img.shields.io/travis/ngzhian/pycrunchbase/master.png?style=flat
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ngzhian/pycrunchbase

.. |coveralls| image:: https://coveralls.io/repos/ngzhian/pycrunchbase/badge.svg
    :target: https://coveralls.io/r/ngzhian/pycrunchbase

.. |version| image:: http://img.shields.io/pypi/v/pycrunchbase.png?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/pycrunchbase

.. |downloads| image:: http://img.shields.io/pypi/dm/pycrunchbase.png?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/pycrunchbase

.. |wheel| image:: https://pypip.in/wheel/pycrunchbase/badge.png?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/pycrunchbase

.. |supported-versions| image:: https://pypip.in/py_versions/pycrunchbase/badge.png?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/pycrunchbase

.. |supported-implementations| image:: https://pypip.in/implementation/pycrunchbase/badge.png?style=flat
    :alt: Supported imlementations
    :target: https://pypi.python.org/pypi/pycrunchbase

Python bindings to CrunchBase

Examples
========

::

    # initialize the API using your API Key, will throw ValueError if missing
    cb = CrunchBase(API_KEY)
    # look up an organization by name
    github = cb.organization('github')

    # the response contains snippets of data regarding relationships
    # that the organization has, an example is the funding_rounds
    funding_rounds_summary = github.funding_rounds

    # all relationships are paged, and only 8 is returned initially
    # to get more data do this, it handles paging for you
    # and returns a False-y value if there are no more pages
    more_funding_rounds = cb.more(funding_rounds_summary)

    # data in relations are just summaries, and you probably want more details
    # For example funding_rounds returns 5 values: type, name, path
    # created_at, updated_at.
    # If you actually want to know who invested, you have to get to make
    # more API calls

    # first get the uuid of the round
    round_uuid = funding_rounds_summary[0].uuid

    # then use the CrunchBase API to make that call
    round = cb.funding_round(round_uuid)

    # again, investments is a relationship on a FundingRound,
    # so we can get the first item in that relationship
    an_investor = round.investments[0]  # a InvestorInvestmentPageItem

    # and printing that gives us the name of the investor, and the amount
    # invested in USD
    print(str(an_investor))  # prints: Investor Name $100000


Installation
============

::

    pip install pycrunchbase

Documentation
=============

https://pycrunchbase.readthedocs.org/

Development
===========

To run the all tests run::

    tox

Contributions are always welcome!

Use `GitHub issues <https://github.com/ngzhian/pycrunchbase/issues>`_
to report a bug or send feedback.

The best way to send feedback is to file an issue at https://github.com/ngzhian/pycrunchbase/issues.

Goals
=====

1. Support all (or almost all) of CrunchBase's API functionalities
2. Speedy updates when CrunchBase's API changes
3. 'Pythonic' bindings, user doesn't feel like we're requesting URLs


TODO
===========

* Support other nodes (IPO, FundRaise)
* Coerce values in relationships page item to python types (datetime)

License
=======

MIT


Changelog
=========

0.1.5 (2015-02-13)
-----------------------------------------

* Add a `cb_url` attribute for all PageItem, this url is a CrunchBase page
  (not the API) that holds more information for a particular PageItem
  Allows you to make calls like::

    company.funding_rounds[0].cb_url

  to get the url of the page for the first funding round of `company`.

* A new page item, InvestorInvestmentPageItem, that is useful for FundingRound info::

    round = cb.funding_round('round_uuid')
    an_investor = round.investments[0]  # a InvestorInvestmentPageItem
    print(str(an_investor))  # prints: Investor Name $100000

* Add simplified Contribution guidelines in README

0.1.4 (2015-02-13)
-----------------------------------------

* Relationship retrieval is 0-based now, 1-based just doesn't fit well with array
* Better `__str__` for `Node` and `Relationship`
* `Relationship.get(i)` if `i` is too large or small will return a NonePageItem singleton

0.1.3 (2015-02-12)
-----------------------------------------

* Fix Relationship: wasn't using the right build method of PageItem
* Add test to checkk for the above
* remove unused reference to CrunchBase in Relationship


0.1.2 (2015-02-12)
-----------------------------------------

* PageItem and it's subclasses to represent an item within a relationship
  of a Node
* Cleanup of where utility methods live (parse_date)
* More tests as always, overall 98.21% coverage

0.1.0 (2015-02-21)
-----------------------------------------

* First release on PyPI.


