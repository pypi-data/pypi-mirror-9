CHANGELOG
=========

0.1.24 (2015-04-13)
===================

- Nothing changed yet.


0.1.23 (2015-04-13)
===================

- Changed location of classproperty decorator from ``ripozo.utilities`` to ``ripozo.decorators``
- Fixed bug with wrapping _apiclassmethod decorated functions.


0.1.22 (2015-04-10)
===================

- Fixed error with formatting exceptions


0.1.21 (2015-04-07)
===================

- Added links
- Added _list_fields attribute to BaseManager for more efficient querying when necessary
- Moved getting the adapter class based on the format type in the dispatcher to its own method.


0.1.20 (2015-03-24)
===================

- Fields no longer have a default.
- Adapter.extra_headers returns a dictionary instead of a list
- Fields can specify an error message.
- ListField added
- Fixed deep inheritance issue with translate decorator.
- Added the name of the relationship as an item in the rel list in the SIREN adapter.


0.1.19 (2015-03-16)
===================

- Endpoint name


0.1.18 (2015-03-16)
===================

- Fixed bug with RetrieveList mixin
- Added ``picky_processor`` which specifically includes processors to include or exclude.
- pre and post processors now get the name of the function being called. before running


0.1.17 (2015-03-16)
===================

- Fucked up...


0.1.16 (2015-03-16)
===================

- Fixed the bug where inheritance of abstract methods resulted in mutable common endpoint_dictionaries
- endpoint_dictionary is now a method and not a property


0.1.15 (2015-03-16)
===================

- Fixed bug that resulted in multiple forward slashes in a row on a url


0.1.14 (2015-03-16)
===================

- Added method to RequestContainer object
- Imported Relationship and ListRelationship into relationships.__init__.py module for more intuitive access
- Imported HtmlAdapter to adapters.__init__.py for more intuitive imports.
- Including html adapter templates in package


0.1.13 (2015-03-14)
===================

- Added generic CRUD+L mixins.  These are included merely for convience
- Required fields validation can be skipped.  In other words, you can now specify that a field does not need to be present when validating


0.1.12 (2015-03-14)
===================

- Code cleanup


0.1.11 (2015-03-08)
===================

* Some updates to the release process.


0.1.10 (2015-03-08)
===================

* Started using zest.releaser for managing releases.
* Added ``register_resources`` method to the DispatcherBase class
