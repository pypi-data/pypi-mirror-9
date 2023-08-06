Changelog
=========

Version 2.1.1
-------------

* Fix Django 1.7/1.8 model saving issues.
* Added ``AnyUrlValue.from_model()`` to directly wrap a model into an ``AnyUrlValue``.

Version 2.1
-----------

* Added Django 1.8 support
* Fix importing json fixture data.

Released as 2.1a1:
~~~~~~~~~~~~~~~~~~

* Added caching support for URL values.


Version 2.0.4
-------------

* Fixed Python 3.3 issues


Version 2.0.3
-------------

* Fixed ``__eq__()`` for comparing against other object types.


Version 2.0.2
-------------

* Added pickle support.
* Fixed Django 1.7 support.


Version 2.0.1
-------------

* Fix performance issue with form fields.


Version 2.0
-----------

Released as 2.0b1:
~~~~~~~~~~~~~~~~~~

* Improved Python 3 support.
* Delay initialisation of ``ModelChoiceField`` objects.
* Fix ``exists()`` value for empty URLs


Released as 2.0a1:
~~~~~~~~~~~~~~~~~~

* Added Python 3 support
* Allow passing callables to the form_field parameter of ``AnyUrlField.register_model``


Version 1.0.12
--------------

* Implement ``AnyUrlField.__deepcopy__()`` to workaround Django < 1.7 issue,
  where ``__deepcopy__()`` is missing for ``MultiValueField`` classes.


Version 1.0.11
--------------

* Improve external URL support (https, ftps, smb, etc..)
* Fix unnecessary query at registration of custom models.


Version 1.0.10
--------------

* Fix using ``AnyUrlField`` with ``blank=True``.
* Fix ``_has_changed`` is no longer used in django >= 1.6.0


Version 1.0.9
-------------

* Fixed exporting the value in the ``dumpdata`` command.


Version 1.0.8
-------------

* Use ``long()`` for ID's, not ``int()``.
* Improve ``ObjectDoesNotExist`` check in ``AnyUrlValue.__unicode__()``, to support model translations.


Version 1.0.7
-------------

* Fix using this widget with Django 1.6 alpha 1


Version 1.0.5
-------------

* Fix errors during south migration
* Fix errors when deleting rows in an inline formset which uses an ``AnyUrlField``.


Version 1.0.4
-------------

* Fix https URL support


Version 1.0.3
-------------

* Fix change detection, to support formsets and admin inlines.
* Fix widget alignment within a ``TabularInline``.


Version 1.0.2
-------------

* Fix ``setup.py`` code to generate translation files for the ``sdist``.
* Remove ``HorizonatalRadioFieldRenderer`` from the public API.


Version 1.0.1
-------------

* Use jQuery live events to support using the ``AnyUrlField`` in Django inlines.


Version 1.0.0
-------------

First PyPI release.

The module design has been stable for quite some time,
so it's time to release this module to the public.
