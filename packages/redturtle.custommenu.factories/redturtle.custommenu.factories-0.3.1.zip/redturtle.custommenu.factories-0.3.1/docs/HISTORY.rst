Changelog
=========

0.3.1 (2015-02-24)
------------------

- Fixed issue when on folders that are not annotable
  (uncommon, but may happen on old stuff like PloneGazette).
  [keul]
- Plone 3/ Plone 4 compatibility on default menu title and description
  [keul]
- Fixed tests
  [keul]
- Pyflakes cleanup and related errors fixed
  [keul]

0.3.0 (2013-07-10)
------------------

* provided Generic Setup support [nueces]
* now can't no-more manage menu without installing the product [keul]
* disabled useless JavaScript [keul]
* now works also with single entry menu (close `#1`__) [keul]
* now supporting Plone 4 style icons [keul]

  __ https://github.com/keul/redturtle.custommenu.factories/issues/1

0.2.0b - (2010-02-17)
---------------------

* now local customizations must be enabled and disabled per-context [keul]
* fixes to XHTML structure and validation [keul]
* fixed CSS class names to be camelCase as Plone does [keul]
* added tests [keul]
* fixed templates to be test compatible [keul]
* fixed a bug on entry deletion [keul]
* added missing check on required element for entries (in facts were optional) [keul]
* added egg support for z3c.autoinclude [keul]
* now False condition for an element with id hide inherited element with same id [keul]
* added Plone 4 compatibility [keul]

0.1.0a - (2010-01-04)
---------------------

* initial release

