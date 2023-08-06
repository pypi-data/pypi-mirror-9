
Changelog
=========

0.2.5 (2015-04-04)
------------------

* Added: Locations - get a list of active locations from CrunchBase
* Added: LocationPageItem - each location in the Page of Locations
* Added: Categories - get a list of active categories from CrunchBase
* Added: CategoryPageItem - each location in the Page of Categories

0.2.4 (2015-04-03)
------------------

* Added: IPO - you can now use a uuid to grab IPO data


0.2.3 (2015-03-01)
------------------

* Fix: Travis builds and tests

0.2.2 (2015-02-25)
------------------

* Fix: Unicode output (using UTF-8 encoding)

0.2.1 (2015-02-21)
------------------

* Fix `__version__`


0.2.0 (2015-02-15)
------------------

* The API is now considered relatively *stabled*. Updated the classifier to
  reflect so
* Change to how `CrunchBase.more` reacts to a `Relationship`, we no longer
  optimize when the `Relationship` has all items, just call
  `first_page_url`

0.1.9 (2015-02-15)
------------------

* Add `series` to the `FundingRound` node.

0.1.8 (2015-02-15)
------------------

* Update `__str__` for nodes and relationships


0.1.7 (2015-02-15)
------------------

* `Relationship` is now a subclass of `Page`, although this strictly isn't true.
  The benefit is that this allows us to reuse a lot of logic.
  Relationship can be thought of as Page 0, which is a summary of potentially
  multiple pages of `PageItem`. The only time we get a relationship is when we
  query for a particular `Node`, e.g. organiation, and we grab the relationships
  returned by the API. After this, to get more details we call `Crunchbase.more`,
  and this returns us a `Page`.

* Added `__repr__` methods to all the `Node`, `Relationship`, `PageItem`.
  Previously we only defined `__str__`, but these didn't show up in places
  like the REPL. This fixes that. We try to make it obvious what object it is
  based on what is printed, but also don't want to be too verbose.

0.1.6 (2015-02-15)
------------------

* `InvestorInvestmentPageItem` now has the possibility of being either a
  `investor`, or a `invested_in` relationship

* Propogates any exception when making the actual HTTP call to CrunchBase

0.1.5 (2015-02-13)
------------------

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
