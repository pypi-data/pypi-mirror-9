Changelog
---------

0.9.1 (2015-01-20)
==================

- Fix test with Plone-4.3.4. [taito]

0.9 (2014-09-16)
================

- Update icons for content types: CartContainer and OrderContainer. [taito]

0.8 (2013-11-06)
================

- Fix module name template.py -> view.py [taito]

0.7 (2013-10-28)
================

- Update view for content type: collective.cart.core.Order. [taito]
- Update roles. [taito]
- Move BaseFormView to package: collective.base. [taito]
- Move base viewlet interface to package: collective.base. [taito]
- Move test packages to extras_require. [taito]
- Remove dependency from five.grok. [taito]
- Move cart related content to order related. [taito]
- Test with Plone-4.3.2. [taito]
- Added CSRF authenticator. [taito]

0.6 (2013-03-11)
================

- Updated cart to use session. [taito]
- Covered tests. [taito]
- Added dependency to collective.base. [taito]
- Added method: shop_path to ShoppingSite adapter. [taito]
- Added redirection from other check out url to cart url when cart is empty. [taito]
- Moved subscribers and utilities to collective.cart.shopping. [taito]
- Updated workflows. [taito]
- Updated translations. [taito]
- Added testing integration to Travis CI. [taito]

0.5.2 (2012-09-24)
==================

- Added permission for cart portlet. [taito]

0.5.1 (2012-09-20)
==================

- Added purge="False" to types_not_searched and metaTypesNotToList properties. [taito]

0.5 (2012-09-19)
================

- Use Dexterity. [taito]
- Tested with Plone-4.2.1. [taito]

0.4.1 (2011-10-03)
==================
- easy_install error fixed. [taito]

0.4 (2011-09-24)
================
- End of support for Plone-3.x.
- License updated from GPL to BSD.

0.3.2 (2011-05-14)
==================
- has_cart_folder method added.

0.3.1 (2011-04-25)
==================
- Some template fixes.

0.3.0 (2011-04-25)
==================
- Refactored for plugins.

0.2.0 (2011-04-23)
==================
- Input support for quantity method.
- Multiple cart folder support.

0.1.1 (2011-04-21)
==================
- Double registration of cart portlet fixed.

0.1.0 (2011-04-21)
==================
- Initial release
