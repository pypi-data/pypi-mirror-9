Changelog
=========

0.9.4
-----

* Fix: ``SortedMultipleChoiceField`` did not properly report changes of the
  data to ``Form.changed_data``. Thanks to @smcoll for the patch.

0.9.3
-----

* Fix: ``AlterSortedManyToManyField`` operation failed for postgres databases.
* Testing against MySQL databases.

0.9.2
-----

* Fix: ``AlterSortedManyToManyField`` operation failed for many to many fields
  which already contained some data.

0.9.1
-----

* Fix: When using the sortable admin widget, deselecting an item in the list
  had not effect. Thank you to madEng84 for the report and patch!

0.9.0
-----

* Adding ``AlterSortedManyToManyField`` migration operation that allows you to
  migrate from ``ManyToManyField`` to ``SortedManyToManyField`` and vice
  versa. Thanks to Joaquín Pérez for the patch!
* Fix: Supporting migrations in Django 1.7.4.
* Fix: The admin widget is not broken anymore for dynamically added inline
  forms. Thanks to Rubén Díaz for the patch!

0.8.1
-----

* Adding support for Django 1.7 migrations. Thanks to Patryk Hes and Richard
  Barran for their reports.
* Adding czech translations. Thanks to @cuchac for the pull request.

0.8.0
-----

* Adding support for Django 1.7 and dropping support for Django 1.4.

0.7.0
-----

* Adding support for ``prefetch_related()``. Thanks to Marcin Ossowski for
  the idea and patch.

0.6.1
-----

* Correct escaping of *for* attribute in label for the sortedm2m widget. Thanks
  to Mystic-Mirage for the report and fix.

0.6.0 
-----

* Python 3 support!
* Better widget. Thanks to Mike Knoop for the initial patch.

0.5.0
-----

* Django 1.5 support. Thanks to Antti Kaihola for the patches.
* Dropping Django 1.3 support. Please use django-sortedm2m<0.5 if you need to
  use Django 1.3.
* Adding support for a ``sort_value_field_name`` argument in
  ``SortedManyToManyField``. Thanks to Trey Hunner for the idea.

0.4.0
-----

* Django 1.4 support. Thanks to Flavio Curella for the patch.
* south support is only enabled if south is actually in your INSTALLED_APPS
  setting. Thanks to tcmb for the report and Florian Ilgenfritz for the patch.

0.3.3
-----

* South support (via monkeypatching, but anyway... it's there!). Thanks to
  Chris Church for the patch. South migrations won't pick up a changed
  ``sorted`` argument though.

0.3.2
-----

* Use already included jQuery version in global scope and don't override with
  django's version. Thank you to Hendrik van der Linde for reporting this
  issue.

0.3.1
-----

* Fixed packaging error.

0.3.0
-----

* Heavy internal refactorings. These were necessary to solve a problem with
  ``SortedManyToManyField`` and a reference to ``'self'``.

0.2.5
-----

* Forgot to exclude debug print/console.log statements from code. Sorry.

0.2.4
-----

* Fixing problems with ``SortedCheckboxSelectMultiple`` widget, especially in
  admin where a "create and add another item" popup is available.

0.2.3
-----

* Fixing issue with primary keys instead of model instances for ``.add()`` and
  ``.remove()`` methods in ``SortedRelatedManager``.

0.2.2
-----

* Fixing validation error for ``SortedCheckboxSelectMultiple``. It caused
  errors if only one value was passed.

0.2.1
-----

* Removed unnecessary reference of jquery ui css file in
  ``SortedCheckboxSelectMultiple``. Thanks to Klaas van Schelven and Yuwei Yu
  for the hint.

0.2.0
-----

* Added a widget for use in admin.
