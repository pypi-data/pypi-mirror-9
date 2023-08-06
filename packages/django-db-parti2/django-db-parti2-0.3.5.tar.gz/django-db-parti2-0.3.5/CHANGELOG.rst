.. :changelog:

Changelog
---------

0.3.3 (2014-04-17)
~~~~~~~~~~~~~~~~~~

- Fixed a bug with ``partition`` command not working for MySQL backend (Issue #11)

0.3.2 (2014-03-27)
~~~~~~~~~~~~~~~~~~

- Added automatic determination of primary key column name, previously this was hardcoded to ``id``
  (thanks to `fjcapdevila <https://github.com/fjcapdevila>`__)
- Python 2.6 compatibility (thanks to `Daniel Kontsek <https://github.com/dn0>`__)

0.3.1 (2014-02-02)
~~~~~~~~~~~~~~~~~~

- Added support for DateField and DateTimeField with auto_now and auto_now_add attributes set (Issue #3)
- Fixed an issue with unnecessary calling of partitioning functions while reading data from database
- MySQL: Fixed inability to create partitions for December when range was set to ``month``
- MySQL: Backend was completely broken in previous version, now everything should work properly (Issue #4)

0.3.0 (2013-09-15)
~~~~~~~~~~~~~~~~~~

- Rewritten from scratch, introduced new API to add support for new backends and partition types
- All default model settings which are done inside model's Meta class are now set to ``None``, that means
  that there are no more default settings. Everything should be explicitly defined inside each model class.
- Introduced new model setting ``partition_type`` which currently accepts only one value ``range``
- Introduced new model setting ``partition_subtype`` which currently accepts only one value ``date`` and
  is used only with ``partition_type`` when it's set to ``range``
- Better error handling, django-db-parti tries it's best to tell you where and why an error occured
- Added support for day and year partitioning for all backends in addition to week and month
- PostgreSQL: new partitions are now created at the database level, that gave some speed improvement,
  also we don't rely on Django's save() method anymore, that means that there is no more limitation
  with Django's bulk_create() method, you can use it freely with partitioned tables
- PostgreSQL: fixed an error when last day of the week or month wasn't inserted into partition

0.2.1 (2013-08-24)
~~~~~~~~~~~~~~~~~~

- Updated readme
- Python 3 compatibility
- Datetime with timezone support (Issue #1)

0.2.0 (2013-06-10)
~~~~~~~~~~~~~~~~~~

- Added mysql backend
- Fixed incorrect handling of datetime object in DateTimeMixin

0.1.5 (2013-06-08)
~~~~~~~~~~~~~~~~~~

- Updated readme
- Fixed postgresql backend error which sometimes tried to insert the data into partitions that don't exist
- Moved all the database partition system stuff to the command ``partition`` (see readme), that gave a lot
  in speed improvement because we don't need to check for trigger existance and some other things at runtime
  anymore

0.1.4 (2013-06-01)
~~~~~~~~~~~~~~~~~~

- Packaging fix

0.1.3 (2013-06-01)
~~~~~~~~~~~~~~~~~~

- Packaging fix

0.1.2 (2013-06-01)
~~~~~~~~~~~~~~~~~~

- Packaging fix

0.1.1 (2013-06-01)
~~~~~~~~~~~~~~~~~~

- Packaging fix

0.1.0 (2013-06-01)
~~~~~~~~~~~~~~~~~~

- Initial release
