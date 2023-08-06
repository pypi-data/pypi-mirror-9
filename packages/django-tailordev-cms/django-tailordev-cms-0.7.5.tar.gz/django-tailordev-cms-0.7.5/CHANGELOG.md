# Changelog

## 0.7.4/5 - 2015/03/03

Fix page ordering (issue #27). Pages are now also ordered by `last_modified` datetime (after `position`).

## 0.7.2/3 - 2014/08/31

Fix TinyMCE admin mixin media urls.

## 0.7.1 - 2014/08/31

Fix migrations ImageField reference.

## 0.7 - 2014/08/19

Django-filebrowser is no longer a dependency. Thumbnails generation and files management with other storages that the standard one motivated this decision.

## 0.6.2 - 2014/03/13

Some more work on issue #19 (language switching) for Page-derived objects detail views. This feature is now fully functional (and tested).

## 0.6.1 - 2014/03/06

Fix issue #17. First migration is now fully compatible with Django>=1.5 custom User model.

## 0.6 - 2014/03/06

New features:

* add a new assignment template tag: `get_page_url_for_language` 
* add a custom `SetLanguageView` to switch languages for a page or category (or an inherited model detail view)

Fix minor issues:

* issue #13: add tinyMCE styles to page and categorie detail view templates.
* issue #18: we now raise a warning message when disqus is not configured instead of an `ImproperlyConfigured` exception.
* issue #21: pages from other languages are now displayed instead of raising a 404 error.

## 0.5.4 - 2013/12/19

Fix issue #16: when asking for category pages, default ordering (position) was overridden. This is now fixed.

## 0.5.3 - 2013/12/03

Fix issue #15: categories can now be related to objects that do not inherit from the Page model, and the get_pages method will list them.

## 0.5.2 - 2013/11/22

Fix social media page sharing logic: everything stands in the `td_cms/partials/page_social.html` template. Feel free to add your killer plugin.

## 0.5.1 - 2013/11/15

Fix requirements in setup.py installation script

## 0.5 - 2013/11/11

First public stable release

## TODO

* Write the doc :)
