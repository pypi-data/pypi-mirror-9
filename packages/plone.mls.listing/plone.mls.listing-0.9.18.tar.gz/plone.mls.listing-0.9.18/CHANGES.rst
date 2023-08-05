Changelog
=========

0.9.18 (2015-01-30)
-------------------

- Fixed migration step from 1008 to 1009.


0.9.17 (2015-01-30)
-------------------
- Make a copy of the field before changing its attributes.
- Make ps.plone.fotorama dependency optional.


0.9.16 (2014-11-24)
-------------------

- Listing Details template: add field id CSS class to tabbed ListingDetails.
- Removed kupu integration.
- Support galleria and fotorama slideshow.
- Added MLS UI settings controlpanel. Allows selection of slideshow plugin.


0.9.15 (2014-09-17)
-------------------

- Limit listing types in searches if restricted and no listing type is selected.
- Show no results found message when no search results available.
- I18N updates.


0.9.14 (2014-09-15)
-------------------

- Support 'filtered' vocabularies for e.g. search options.
- Support filtering of listing types within the search.
- Include phone number in contact email.
- I18N updates.


0.9.13 (2014-08-21)
-------------------

- Don't send a copy of the agent contact portlet message to the sender.
- Added override recipient to agent contact portlet. Use this to redirect all emails to that address for (spam) review.
- Add info about the original agent to the contact form email. Referral agents need to be able to contact the responsible listing agent.
- I18N updates.


0.9.12 (2014-07-14)
-------------------

- Added option to filter listing results for the current agency.
- Add css classes for agent info portlet fields.
- I18N updates.


0.9.11 (2014-03-17)
-------------------

- Fixed UnicodeDecodeError for contact portlet.
- I18N updates.


0.9.10 (2014-02-24)
-------------------

- Allow local agency information.
- Show phone number for all listing types in agent contact portlet.
- I18N updates.


0.9.9 (2014-01-31)
------------------

- Fixed traversal conflict with contentleadimage.
- I18N updates.


0.9.8 (2014-01-18)
------------------

- Added agent avatar URL field.
- Fixed portlet reistartions so we can customise them now.
- I18N updates.


0.9.7 (2013-07-02)
------------------

- Changed default search result order to creation date (reversed).


0.9.6 (2013-06-28)
------------------

- Fixed tal error in portlet template.


0.9.5 (2013-06-27)
------------------

- CI with travis-ci.
- Removed dependency to raptus.article.


0.9.4 (2013-06-26)
------------------

- Fixed JS for configuration view overlays.
- CSS fixes.


0.9.3 (2013-06-11)
------------------

- [Bugfix] Set captcha widget after fields are set up.


0.9.2 (2013-06-11)
------------------

- Hide contact info for agent info portlet if contact portlet is available.
- Added fields to agent contact form for residential lease.
- Use transparent background for galleria slideshow container.
- Hide county and district from quick search portlet.
- Add collective.captcha based captcha for agent contact form.


0.9.1 (2013-03-27)
------------------

- I18N updates.


0.9 (2013-03-27)
----------------

- Added lot size and interior size to listing search.
- Made lookup values translatable.
- I18N updates.


0.8 (2012-08-20)
----------------

- Added Agent Contact portlet.
- Added Quick Search portlet.
- Show custom agent info if 3rd party listing and option for showing custom info is selected.


0.7.1 (2012-06-15)
------------------

- Adjusted listing detail view to new api fields.
- I18N updates.


0.7 (2012-06-13)
----------------

- Adjusted viewlets so they can be customized through the ZMI.
- Added noValueMessage adapter for listing forms.
- I18N updates.


0.6 (2012-03-22)
----------------

- Added agent quote section (incl. images and styles).


0.5 (2012-02-14)
----------------

- Added missing i18n ids (#1744).
- I18N updates (es, ja).


0.4 (2012-02-11)
----------------

- Registered I18N locales folder.


0.3 (2012-02-11)
----------------

- I18N updates merged.
- Added SearchOptions cache objects for listing search categories. Defaults to 1 hour ram cache.


0.2 (2012-02-05)
----------------

- Use plone.app.testing for tests.
- Upgraded dexterity content types. Requires plone.app.dexterity >= 1.1.
- Added 'Recent Listings' viewlet with configuration.
- Added 'Listing Collection' viewlet with configuration.
- Added 'Listing Search' viewlet with configuration.
- Added API methods to access the MLS API. Requires mls.apiclient.
- Added Infinite Ajax Scroll JavaScript (disabled by default) for Facebook like scroll and auto-load of next items.
- Added I18N.
- Adjusted raptus.article based views (don't use tables anymore).


0.1.2 (2011-10-26)
------------------

- Bugfix: Plone 4.1.x compatibility.


0.1.1 (2011-09-07)
------------------

- BUGFIX: Added missing get_language import.


0.1 (2011-09-07)
----------------

- Added language support.


0.1rc3 (2011-06-04)
-------------------

- Fixed location info traceback if listing does not exist.


0.1rc2 (2011-05-26)
-------------------

- Added missing lead image to list of images.
- Updated css for listing slideshow.


0.1rc1 (2011-05-26)
-------------------

- Added custom browserlayer and custom css file.
- Added migrations for browserlayer and css.
- Added Galleria JS Slideshow.
- Disable 'Link using UID's in TinyMCE.


0.1b2 (2011-05-24)
------------------

- Added versioning for dexterity content type.


0.1b1 (2011-05-23)
------------------

- Added description and long description to detail view.
- Added listing to linkable types (TinyMCE and Kupu).
- Moved images on top below the listing information.
- Added configuration for raptus.article.
- Added article integration.


0.1dev (2011-05-18)
-------------------

- First Beta Release.
