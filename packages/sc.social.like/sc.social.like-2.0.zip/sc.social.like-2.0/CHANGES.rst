Changelog
---------

There's a frood who really knows where his towel is.

2.0 (2015-02-10)
^^^^^^^^^^^^^^^^^^^

- Do not load social media stuff on non-canonical views (like edit form or similar). This close `#36`_.
  [keul]

- Added italian translation.
  [keul]

- Load behavior of all social plugins changed to be async.
  [keul]

- Fixed a problem with images loaded in news. If the image isn't a JPG,
  the `get_content_image` method can't get image size and returns nothing.
  This avoid some strange things, like MemoryError with Pillow.
  [cekk]

- If a field named "image" isn't an ImageField, do not break the viewlet.
  [cekk]

- Add exception handling also for TypeError in get_content_image method.
  [cekk]

- Fixed metadata og:type, used value 'article' for internal page.
  [fdelia]


2.0rc1 (2014-10-14)
^^^^^^^^^^^^^^^^^^^

- Use safe_unicode to deal with accented chars in content Title.
  [ericof]


2.0b4 (2014-08-08)
^^^^^^^^^^^^^^^^^^

- Fixed styling for action buttons. Now they are displayed side by side
  [agnogueira]

- Fix an UnicodeDecodeError in the Twitter plugin (Reported by Programa Interlegis)
  [ericof]


2.0b3 (2014-06-06)
^^^^^^^^^^^^^^^^^^

- Fix a division by zero issue happening with AT Images during creation (while on portal_factory)
  [ericof]


2.0b2 (2014-06-02)
^^^^^^^^^^^^^^^^^^

- Facebook now recommends 1200 x 630 images
  [ericof]


2.0b1 (2014-02-07)
^^^^^^^^^^^^^^^^^^^^

- Use View permission on viewlets to avoid security failures into viewlet
  if anonymous try to display non public parts of site.
  [thomasdesvenain]

- Fix package dependencies.
  [hvelarde]


2.0a2 (2013-11-04)
^^^^^^^^^^^^^^^^^^^^

- Use content language instead of request language, avoiding cache problems
  https://github.com/collective/sc.social.like/issues/19
  [ericof]


2.0a1 (2013-07-23)
^^^^^^^^^^^^^^^^^^^^

- Drop support for Plone 4.0.x [ericof]

- Increasing test coverage [ericof]

- Render metadata viewlet on folder_full_view and all_content templates
  https://github.com/collective/sc.social.like/issues/11 [ericof]

- Fixes vertical display
  https://github.com/collective/sc.social.like/issues/5 [ericof]

- Add LinkedIn and Pinterest support.
  https://github.com/collective/sc.social.like/issues/6 [ericof]

- Plugin implementation [ericof]

- Ensure all resources are loaded using scheme-relative URLs.  Previously,
  attempting to load off HTTP on HTTPS sites resulted in broken pages.
  [davidjb]

- Plone 3.x is not officially supported anymore; use it at your own risk.
  [hvelarde]

- Change CSS import to link.
  [agnogueira]


1.0.1 (2013-03-26)
^^^^^^^^^^^^^^^^^^^

- Fix packaging [ericof]


1.0 (2013-03-13)
^^^^^^^^^^^^^^^^^^

- Tested Plone 4.3 compatibility. [hvelarde]

- Updated package documentation. [hvelarde]

- Tested Plone 4.2 compatibility. [hvelarde]

- Added basic installation tests. [hvelarde]


0.9.1 (2012-06-11)
^^^^^^^^^^^^^^^^^^^

* FB support for simple language codes [erral]

* Add basque translation [erral]

* We carry the plusone button after the document load [cleberjsantos]

* Correcting language for the buttons [cleberjsantos]

* Added CSS uninstall profile [cleberjsantos]

* Fix FB iframe url [erral]


0.9 (2011-11-06)
^^^^^^^^^^^^^^^^^^

* Compressed icon ico-sociallike.png with pngout 70% of original
  [Michael Krishtopa]

* Fix loading buttons for diazo themes [cleberjsantos]

0.8 (2011-08-30)
^^^^^^^^^^^^^^^^^^

* Fixed Plone 4.1 compatibility [hvelarde]

* Added testing framework and basic tests [hvelarde]

* Added Spanish translation [hvelarde]

* Fixed "Deadlock when viewing an object on which the user has not the View
  permission" issue with patch provided by glenfant [hvelarde]


0.7 (2011-07-12)
^^^^^^^^^^^^^^^^^^

* i18n support for Facebook button. Now we check which languages the user
  accepts then provide the right link [erico_andrei]

* Add conditions to show each provider [erico_andrei]

* Refactor viewlet code [erico_andrei]

* Enable controlpanel tabbing [erico_andrei]


0.6 (2011-06-09)
^^^^^^^^^^^^^^^^^^

* Support for plusone google button [cleberjsantos]

* jQuery Loading the buttons [cleberjsantos]


0.5 (2011-04-18)
^^^^^^^^^^^^^^^^^^

* Support for Twitter and Facebook [cleberjsantos]

* Initial release [cleberjsantos]

.. _`#36`: https://github.com/collective/sc.social.like/issues/36
