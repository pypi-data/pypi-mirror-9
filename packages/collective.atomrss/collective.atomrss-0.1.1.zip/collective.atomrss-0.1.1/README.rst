====================
collective.atomrss
====================

Package extends Plone syndication for using Atom RSS by default.

"The Atom syntax was specifically designed to allow elements to be reused outside the context of an Atom feed document" wikipedia

It added some field as events date, image (for news) and leadimage (for event) into rss content feed.
This package also add content text into rss feed
What this package do :
    - Added content into rss items feed, by default, render_body is set to True in FeedSettings
    - Added image (for News Item), leadimage (for Event) in content items
    - Use only Atom as default view in FeedSettings

It also package added event startdate, enddate, location, organizer, type into feed items as explain in
http://web.resource.org/rss/1.0/modules/event/

* `Source code @ GitHub <https://github.com/collective/collective.atomrss>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/collective.atomrss>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/collective/collective.atomrss>`_


How it works
============

This package :
    - adapts IFeedSettings for changing default value of rss feed.
    - override atom.xml browserview for adding news image and event informations.


Installation
============

To install `collective.atomrss` you simply add ``collective.atomrss``
to the list of eggs in your buildout, run buildout and restart Plone.
Then, install `collective.atomrss` using the Add-ons control panel.
