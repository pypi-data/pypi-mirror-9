.. -*- coding: utf-8 -*-

0.4.6
-----

* Add deposit links, taxes, product organic flag.

* Improve product and vendor schema some more.

* Revert to simple names and descriptions for model ``unicode()``.

* Add ``GPC.pretty()`` method.

* Add ``order_by`` kwarg to ``db.cache.cache_model()`` function.

* Add ``get_subdepartment()`` API function.

* Add duplicate UPC warning in ``ProductCost`` importer.

* Hopefully fix ``install_pip`` Fabric function.


0.4.5
-----

* Add ``status_text`` field to batch row tables.

* Add ``BatchHandler.make_batch()`` method.

* Add ``FileBatchHandler`` class.

* Add ``repr()`` for batch models.

* Add vendor catalog batch importer.

* Add vendor invoice batch importer.

* Add some docs for new batch system.

* Add initial ``RattailConfig`` class.

* Make sure ``unzip`` is installed when fabricating POD stuff.

* Fix some string formatting for Python 2.6.


0.4.4
-----

* Make ``Employee.person`` column unique.

* Try again to make database stuff an optional dependency...

* Increase size of ``ProductCost.code`` column.

* Add ``Product.case_pack`` column.

* Add ``encoding_errors`` kwarg to ``UnicodeWriter`` class constructor.


0.4.3
-----

* Fix Alembic ``env.py`` script to accommodate Continuum.

* Add ``Product.deleted`` column.


0.4.2
-----

* Fix password prompt on Windows for ``make-user`` command.


0.4.1
-----

* Rework how Continuum versioning is configured.


0.4.0
-----

This version primarily got the bump it did because of the addition of the data
import framework and support for SQLAlchemy-Continuum versioning.  There were
several other minor changes as well.

* Allow Fabric ``env`` to override POD download URL.

* Quote packages when installing via Fabric ``pip()`` function.

* Add ``time.make_utc()`` function.

* Add ``db.util.maxlen()`` function.

* Add ``set_regular_price()`` and ``set_current_sale_price()`` API functions.

* Add ``db.cache.cache_model()`` function.

* Add ``csvutil.UnicodeWriter`` class.

* Add ``db.importing`` subpackage.

* Add ``ImportSubcommand`` as base class for data import subcommands.

* Add ``import-csv`` command.

* Fix encoding issue when sending email with non-ASCII chars in message.

* Increase length of ``Vendor.name`` column.

* Add encoding support to ``files.count_lines()``.

* Add initial versioning support with SQLAlchemy-Continuum.


0.3.50
------

* Add Alembic files to the manifest.


0.3.49
------

* Make all constraint and index names explicit.

* Add core Alembic migration repository.


0.3.48
------

* Fix filemon fallback watcher to ignore things which aren't files.


0.3.47
------

* Pause execution within filemon action loops (fix CPU usage).

* Add fallback watcher feature for filemon on Windows.


0.3.46
------

* Add ``Product.pretty_upc`` and improve ``unicode(Product)``.

* Make ``Vendor.id`` unique; add ``get_vendor()`` API function.

* Change default batch purge date to 60 days out instead of 90.

* Make SIL writer use a temp path if caller doesn't provide one.

* Add ``Product.cost_for_vendor()`` method.

* New batch mixin system...

* Split ``db.model`` into subpackage.


0.3.45
------

* Quote PG username when setting password via Fabric.

* Allow override of progress text in ``sil.Writer.write_rows()``.

* Move bcrypt requirement into 'auth' extra feature.


0.3.44
------

* Fix some string literal bugs.


0.3.43
------

* Add ``shell=False`` arg to some Fabric calls for PostgreSQL.


0.3.42
------

* Add ``consume_batch_id()`` convenience method to ``sil.Writer`` class.

* Add mail alias option to ``make_system_user()`` Fabric function.

* Add virtualenvwrapper to profile script for root and current user.

* Make alembic a core requirement, for now...


0.3.41
------

* Add ``fablib`` subpackage.

* Add ``obfuscate_url_pw()`` to ``db.util`` module.

* Add ``temp_path()`` method to ``rattail.sil.Writer`` class.


0.3.40
------

* Allow overriding key used to determine mail template name.

* Add ``Store.database_key`` column.

* Move some function logic to ``db.util``.

* Add ``csvutil.UnicodeDictReader`` class.


0.3.39
------

* Let mail template paths be specified as relative to a Python package.


0.3.38
------

* Tweak ``BatchProvider`` constructor, to prepare for edbob removal.

* Email notification rewrite.

* Improve Unicode handling within some label printing logic.


0.3.37
------

* Add ``Product.not_for_sale`` flag.


0.3.36
------

* Add ``time`` module.


0.3.35
------

* Fix bug in SIL writer (make sure all writes use instance method).


0.3.34
------

* Add error handling when attempting user authentication with non-ASCII characters.

* Add timeout to ``locking_copy()``.


0.3.33
------

* Add ``User.active`` and disallow authentication for inactive users.


0.3.32
------

* Add ``ReportCode`` and ``Product.report_code`` to schema.

* Fix ``Product.family`` relationship.

* Add ``rattail.config`` module, currently with ``parse_list()`` function only.


0.3.31
------

* Fix unicode bug in filemon config parsing on Python 2.6.


0.3.30
------

* File Monitor overhaul!

   * New configuration syntax (old syntax still supported but deprecated).
   * Class-based actions.
   * Configure keyword arguments to action callables.
   * Configure retry for actions.
   * Add (some) tests, docs.


0.3.29
------

* Add support for older SQLAlchemy (0.6.3 specifically).


0.3.28
------

* Accept config section name within ``rattail.db.util.get_engines()`` and
  ``rattail.db.util.get_default_engine()``.

* Remove deprecated ``record_changes`` option in ``[rattail.db]`` config
  section.

* Remove deprecated ``rattail.db.init()`` function stub.


0.3.27
------

* Don't require bcrypt unless 'db' feature is requested.


0.3.26
------

* Add ``filemon.util.raise_exception`` for simple file monitor testing.

* Add tox support; fix several test oddities.

* Fix thread naming bug in Windows file monitor.


0.3.25
------

* Require process elevation for ``make-user`` command.

* Use 64-bit registry key when hiding user account on 64-bit Windows.

* Refactor to remove namespace structure.


0.3.24
------

* Stop using ``logging.get_logger()`` adapter wrapper, until we know how to do
  it right.


0.3.23
------

* Use ``find_packages()`` again, as the last build was broken.  (But still
  exclude tests.)


0.3.22
------

* Add some error checking when starting Linux daemons.

* Add ``'uid'`` and ``'username'`` to logger adapter context dict.

* Add initial POD integration module.

* Stop using ``find_packages()``; it was including tests.

* Add "lock" support to Windows file monitor.


0.3.21
------

* Add custom ``LoggerAdapter`` implementation; used by file monitor.
    
  Hopefully this does a better job and avoids some wheel reinvention.


0.3.20
------

* Better leverage config when initializing Win32 services.


0.3.19
------

* Define ``Command`` and ``Subcommand`` classes.
    
  These are (finally) no longer borrowed from ``edbob``, yay.

* Add SQLAlchemy to core dependencies.

* Database config/init overhaul.
    
  This contains some not-very-atomic changes:

  * Get rid of ``get_session_class()`` function and return to global
    ``Session`` class approach.
  * Primary database ``Session`` is now configured as part of command
    initialization, by default.
  * Make ``config`` object available to subcommands, and ``Daemon`` instances
    (the beginning of the end for ``edbob.config``!).
  * Add ``--stdout`` and ``--stderr`` arguments to primary ``Command``.  These
    are in turn made available to subcommands.
  * Overhauled some subcommand logic per new patterns.
  * Get rid of a few other random references to ``edbob``.
  * Added and improved several tests.
  * Added ability to run tests using arbitrary database engine.


0.3.18
------

* Populate ``rattail.db.model.__all__`` dynamically.

* Add ``util.load_entry_points()``.


0.3.17
------

* Add SQLAlchemy engine poolclass awareness to config file.


0.3.16
------

* Make ``get_sync_engines()`` require a config object.

* Add ``getset_factory()`` to ``rattail.db.core``.

* Dont auto-import ``core`` and ``changes`` from ``rattail.db``.

* Handle keyboard interrupt when running dbsync on Linux console.

* Make ``rattail.db.model`` the true home for all models.


0.3.15
------

* Removed global ``Session`` from ``rattail.db``.
    
  A Session class may now be had via ``get_session_class()``.

* Removed reliance on ``edbob.db.engines``.

* Added initial docs (barely, mostly for testing Buildbot).

* Updated tests to work on Python 2.6.

* Improved init scripts to create PID file parent directory as needed.

* Allow Windows file monitor installation with custom user account.


0.3.14
------

* Improve ``make-user`` command somewhat.
    
  Allow username etc. to be overridden; add sanity check if running on platform
  other than win32.


0.3.13
------

* Fix ``ChangeRecorder.is_deletable_orphan()`` for SQLAlchemy 0.7.
    
  Apparently ``Mapper.relationships`` is not available until SQLAlchemy 0.8 and
  later...


0.3.12
------

* Add ``deleted`` attribute to ``repr(Change)``.

* Add "deletable orphan" awareness when recording changes.
    
  Turns out there was a long-standing bug where orphans which were deleted from
  the host would be marked as "changed" (instead of deleted), causing the store
  databases to keep the orphan.


0.3.11
------

* Added ``mail.send_message()`` etc.


0.3.10
------

* Altered ``dump`` command to allow easy overriding of data model.


0.3.9
-----

* Add all of ``data`` folder to manifest.

* Replaced ``insserv`` calls with ``update-rc.d`` in Fabric script.

* Fixed bug in ``price_check_digit()``; added tests.

* Fixed bug in ``upce_to_upca()``; added tests.

* Added ``get_employee_by_id()`` convenience function.

* Refactored model imports, etc.
    
  This is in preparation for using database models only from ``rattail``
  (i.e. no ``edbob``).  Mostly the model and enum imports were affected.

* Added remaining values from ``edbob.enum`` to ``rattail.enum``.

* Added ``get_setting()`` and ``save_setting()`` to ``db.api``.


0.3.8
-----

* Overhauled db sync somewhat; made a little more customizable, added tests.


0.3.7
-----

* Fixed db sync to properly handle ``Family`` deletions.


0.3.6
-----

* Fixed bug in ``Product.full_description``.

* Added ``core.Object`` class.

* Made ``enum`` module available from root namespace upon initial import.

* Added ``util`` module, for ``OrderedDict`` convenience.

* Add ``Family`` and ``Product.family``.


0.3.5
-----

* Declare dependencies instead of relying on edbob.

* Added ``db.auth`` module.

* Added ``initdb`` command.

* Added the ``adduser`` command.

* Pretend ``commands.Subcommand`` is defined in ``rattail``.


0.3.4
-----

* Fixed ``Customer._people`` relationship cascading.


0.3.3
-----

* Fixed bugs with ``CustomerGroupAssignment``.
    
  Now orphaned records should no longer be allowed.

* Fixed ``CustomerPerson`` to require customer and person.

* Added ``--do-not-daemonize`` flag to ``dbsync`` command on Linux.

* Overhauled some database stuff; added tests.

* Added some ``CustomerEmailAddress`` tests, removed some unused tests.


0.3.2
-----

* Fixed bug in ``csvutil.DictWriter``; added tests.


0.3.1
-----

* Added ``Product.full_description`` convenience attribute.

* Added ``--do-not-daemonize`` arg to ``filemon`` command on Linux.

* Added ``dump`` command.


0.3a43
------

* Added unicode-aware CSV reader.


0.3a42
------

* Fixed dbsync bug when deleting a ``CustomerGroup``.
    
  Any customer associations which still existed were causing database integrity
  errors.


0.3a41
------

* Added ``get_product_by_code()`` API function.


0.3a40
------

* Added proper ``init.d`` support to Linux dbsync daemon.
    
   * Added ``--pidfile`` argument to ``dbsync`` command.
   * Added ``configure_dbsync`` Fabric command.

* Added ``files.overwriting_move()`` convenience function.

* Added ``--all`` argument to ``purge-batches`` command.

* Added ``ProductCode``, ``Product.codes`` to data model.

* Fixed ``db.cache`` module so as not to require initialization.


0.3a39
------

* Added ``make-user`` command for creating Windows system user account.

* Added avatar image, who knows when that will be useful.
    
  This was created in the hopes it could be used to programmatically set the
  Windows user "tile" image; but that proved unfruitful.

* Changed Linux file monitor to leverage local code instead of ``edbob``.

* Added ``Batch.rows`` property, deprecated ``Batch.iter_rows()``.

* Improved ``sil.Writer.write_rows()``.
    
  This method now allows explicitly specifying the row count, and accepts a
  progress factory.


0.3a38
------

* Changed home folder of system user account to ``/var/lib/rattail``.

* Slight overhaul of Linux file monitor.
    
  This includes the following:
    
  * "More native" Linux file monitor (i.e. less reliant on ``edbob``; current
    code is more or less copied from that project).
  * Addition of ``--pidfile`` command argument on Linux.

* Added (Linux) file monitor configuration to Fabric script.
    
  Also improved ``create_user`` to allow overwriting some settings.

* Fixed file monitor service registration on Windows with ``--auto-start``.

* Fixed "process elevation check" on Windows XP.

* Overhaul of Windows file monitor.
    
  This includes:

  * "More native" Windows file monitor (i.e. less reliant on ``edbob``; current
    code is more or less copied from that project).
  * Improve base class for services, to handle the case where the Windows event
    log is full and can't be written to.  (This prevented the file monitor from
    starting on a machine where the log was full.)


0.3a37
------

* Added ``temp_path()`` function in ``files`` module.


0.3a36
------

* Fixed lingering issues from ``Vendor.contacts`` mapping tweak.


0.3a35
------

* Updated ``repr()`` output for model classes.

* Improved ``find_diffs()`` function.

* Added ``db.model`` module.
    
* Tweaked some ORM mappings.


0.3a34
------

* [feature] Changed some logging instances from ``INFO`` to ``DEBUG``.

  I was just getting tired of the noise.

* [feature] Added ``create_user`` Fabric command.
    
  This creates the ``rattail`` user on a Linux environment.  Probably needs
  some improvement but it's a start.

* [bug] Fixed ``instances_differ()`` function for SQLAlchemy < 0.8.
    
  Presumably the use of ``Mapper.column_attrs`` was not a good idea anyway.
  I'm not quite sure what functionality it adds over ``.columns``.

  (fixes #9)


0.3a33
------

* [general] Tweaked Fabric script to remove egg info before building a
  release.

* [feature] Added ``mail`` module; delegates to ``edbob``.

* [feature] Added ``Session`` to ``db`` module; delegates to ``edbob``.

* [feature] Added ``db.diffs`` module.


0.3a32
------

- Made product cache include *all* costs if so requested.  (Silly oversight.)


0.3a31
------

- [bug] Made change recorder better able to handle new "sets" of related
  objects.  A situation occurred where multiple related objects were being
  introduced to the database within the same session.  Somehow a dependent
  object was being processed first, and its UUID value could not be determined
  since its "upstream" object did yet have one either.  This commit improves
  this situation so that the upstream object will be given an UUID value first,
  if it doesn't yet have one.  The dependent object will then reuse the
  upstream object's UUID as normal.


0.3a30
------

- [feature] Added ``console`` module.  For now this only delegates to
  ``edbob.console``.

- [feature] Added ``get_product_cache()`` function to ``db.cache`` module.
  This is probably the first of many such convenience functions.


0.3a29
------

- [feature] Made Palm conduit unregistration more graceful.  Now this will
  "succeed" even if the conduit isn't actually registered.
  fixes #7

- [feature] Improved Palm conduit (un)registration logic.  Now this can handle
  the case where Hotsync Manager is not installed on the local machine.  The
  code was refactored to make things cleaner also.
  fixes #8

- [feature] Added admin rights check for Palm conduit registration.  Now the
  registration process is checked for an "elevated token" and if none is found,
  a message is displayed and it exits without attempting the registration.
  fixes #3

- [feature] Added admin rights check for Windows file monitor registration.
  Now the registration process is checked for an "elevated token" and if none
  is found, a message is displayed and it exits without attempting the
  registration.
  fixes #5

- [feature] Added ``make-config`` command.  This may need some work yet, to
  better handle the namespace package situation.

- [feature] Added ``Employee.user`` association proxy attribute.

- [feature] Pretend all models and enumerations from ``edbob`` are part of
  ``rattail``.  Some day this will actually be the case.  Client code should be
  able to avoid the ``edbob`` namespace now so that porting will be easier.

- [bug] Fixed issue with recording changes when SQLAlchemy >= 0.8.0.
  Apparently ``RelationshipProperty.remote_side`` is now a ``set`` and doesn't
  support indexing.


0.3a28
------

- [feature] Added ``csvutil`` module.  Currently this only adds some better
  ``DictWriter`` support for Python versions older than 2.7.

- [feature] Added Palm OS app interface.  This adds the Palm HotSync conduit,
  which is used to create CSV files when a handheld running the Rattail app is
  synced with its desktop PC.

- [feature] Added ``files`` module.  This will eventually supercede
  ``edbob.files``, but for now this commit adds only three functions.  These
  just so happened to be ones needed to support some code involving inventory
  count batches.

- [feature] Added ``wince`` module.  This module is used to interface with the
  Rattail app for Windows CE handheld devices.

- [feature] Added new batch system, which will eventually replace the old one.
  Hopefully they can play nicely in parallel, in the meantime.

- [feature] Added `purge-batches` command.  This command will delete forever
  all batches whose purge date has passed.  It is meant to be run on a
  scheduled basis, e.g. nightly.

- [feature] Added "case" value to ``UNIT_OF_MEASURE`` enumeration.

0.3a27
------

- [feature] Added custom `Thread` implementation.  This overrides the default
  behavior of `threading.Thread` by ensuring the system exception hook is
  invoked in case an error occurs within the thread.

0.3a26
------

- [feature] Added `get_product_by_upc()` API function.  This is a convenience
  function which will return a single `Product` instance, or `None`.  It is the
  first of hopefully many API functions.

- [feature] Added SIL columns `F188`, `R71` and `R72`.  These have been added
  to support inventory count batches.

- [bugfix] Fixed `Batch.drop_table()` to handle case where row table doesn't
  exist.  While theoretically this method *shouldn't* encounter a missing
  table, in practice it does happen occasionally.  Now this situation is
  handled gracefully instead of raising an exception.

0.3a25
------

- [bug] Fixed ``Vendor.contacts`` relationship (added 'delete-orphan').

- [feature] Added ``Department.subdepartments`` relationship.

0.3a24
------

- [feature] Added ``__eq__()`` and ``__ne__()`` methods to ``GPC`` class.

- [general] Moved ``GPCType`` SQLAlchemy type class to ``rattail.db`` module.
  This was necessary to make the ``GPC`` class more generally available to
  callers who don't want or need SQLAlchemy to be installed.

- [general] Moved enumerations from database extension to "core" ``enum``
  module.  This is mostly for convenience to callers.

- [bug] Fixed a few bugs with label batches.  These existed mostly because this
  feature hasn't been used in production...

- [feature] Added ``default_format`` attribute to ``LabelFormatter`` class.
  Now when a label profile is edited, this default format is used if no format
  is provided by the user.

- [feature] Changed ``LabelProfile.get_formatter()`` method so that it assigns
  the formatter's ``format`` attribute using the value from the profile.  The
  formatter is free to use or ignore this value, at its discretion.

- [feature] Improved the database synchronizer so that it is *somewhat*
  tolerant of database server restarts.  This likely will need further
  improvement as more testing is done.  The current implementation wraps the
  entire sync loop in a ``try/catch`` block and when a disconnect is detected,
  will wait 5 seconds before re-entering the loop and trying again.

0.3a23
------

- [general] Fixed namespace packages, per ``setuptools`` documentation.

- [feature] Added connection timeout support to ``CommandNetworkPrinter``.

0.3a22
------

- [feature] Added ``LabelProfile.visible`` field.

- [feature] Added generic ``CommandNetworkPrinter`` label printer class.  This
  class sends textual commands directly to a networked printer.

0.3a21
------

- [feature] Refactored database synchronization logic into a proper class,
  which can be overridden based on configuration.

0.3a20
------

- [feature] Tweaked the SIL writer so that it doesn't quote row values when
  they're of data type ``float``.

- [bug] Fixed database sync to properly handle ``Vendor`` deletions.  Now any
  associated ``ProductCost`` records are also deleted, so no more foreign key
  violations.

0.3a19
------

- [bug] Fixed "price toggle" bug in database sync.  It was noticed that
  whenever a product's regular price did not change, yet the product instance
  itself *did* have a change, the regular price association was being removed
  in one sync, then reestablished in the next sync (then removed, etc.).  The
  sync operation now ensures the relationship is removed only when it really
  should be, and that it remains intact when that is appropriate.

0.3a18
------

- [bug] Added special delete logic to the database sync.  Currently, only the
  Department and Subdepartment classes are affected.  When deletions of these
  classes are to be synced between databases, some effort is made to ensure
  that associations with any dependent objects (e.g. Product) are removed
  before the primary instance (e.g. Department) is deleted.

0.3a17
------

- [bug] Added 'delete, delete-orphan' to cascade on ``Product.costs``
  relationship.  This was causing an error when syncing databases.

0.3a16
------

- [bug] Added 'delete, delete-orphan' to cascade on ``Product.prices``
  relationship.  This was causing an error when syncing databases.

0.3a15
------

- [bug] Fixed database sync logic to ensure ``Product`` changes are processed
  before ``ProductPrice`` changes.  Since the underlying tables are mutually
  dependent, the ``dependency_sort()`` call can't *quite* take care of it.  Now
  a lexical sort is applied to the class names before the dependency sort
  happens.  This is somewhat of a hack, merely taking advantage of the fact
  that "Product" comes before "ProductPrice" when lexically sorted.  If other
  mutually-dependent tables come about in the future, this approach may need to
  be revised if their class names don't jive.

0.3a14
------

- [bug] Fixed database synchonization logic to properly handle merging
  ``Product`` instances between database sessions.  Since ``Product`` is so
  interdependent on ``ProductPrice``, a pretty custom merge hack is required.

0.3a13
------

- [bugfix] Fixed ``rattail.db.record_changes()`` so that it also ignores
  ``UserRole`` instance changes if configuration dictates that ``Role`` changes
  are to be ignored.

0.3a12
------

- [bugfix] Fixed foreign key uuid handling in ``rattail.db.record_changes()``.
  Some tables are meant to be used solely as providers of "association proxy"
  fields, the ``uuid`` column is not only a primary key, but also a *foreign
  key* to the "primary" entity table.  In such cases, the uuid value was not
  present at session flush time, so a new one was being generated.
  Unfortunately this meant that the ``Change`` record would point to a
  nonexistent entity record, so the sync would not work.  Now uuid fields are
  inspected to determine if a foreign key is present, in which case the
  relationship is traversed and the true uuid value is used.

- [feature] Added "extra classes" configuration for the ``load-host-data``
  command.  This is necessary when initially populating a "store" (er,
  "non-host") database instance if custom schema extensions are in use (and
  need to be synchronized with the host).

0.3a11
------

- Add R49 SIL column.

- Add ``rattail.pricing`` module.

0.3a10
------

- Ignore batch data when recording changes.

0.3a9
-----

- Bump edbob dependency.

0.3a8
-----

- Tweak database sync.

- Tweak batch processing.

0.3a7
-----

- Add ``Vendor.special_discount``.

0.3a6
-----

- Bump edbob dependency.

0.3a5
-----

- Added ``Store`` and related models.

- Added ``Customer.email_preference`` field.

- Added ``load-host-data`` command.

- Added database changes/synchronization framework.

- Fixed batch table create/drop.

0.3a4r1
-------

- Added ``Product.cost``, ``Product.vendor``.

- Added basic one-up label printing support.

- Added initial batch support, with ``PrintLabels`` provider.

- Added GPC data type.

- Changed internal name of file monitor Windows service.

- Added progress support for label printing.

- Label profiles moved from config to database model.

- Removed ``rattail.db.init_database()`` function.

- Moved some enum values from db extension to core (``rattail.enum`` module).

- Improved SIL support: moved ``rattail.sil`` to subpackage, added ``Writer``
  class etc.

- Fixed file monitor in Linux.

- Added ``delete-orphan`` to ``Vendor.contacts`` relationship cascade.

0.3a4
-----

- Update file monitor per changes in ``edbob``.

0.3a3
-----

- Move database extension to subdir (``rattail.db.extension``).

- Make database extension require ``auth`` extension.

- Fix ``rattail.db.init()``.

- Add lots of classes to database extension model.

- Add ``rattail.labels`` module.

- Add ``rattail.db.cache`` module.

- Add SIL output functions.

- Remove some batch code (for now?).

0.3a2
-----

- Added Windows file monitor service.

0.3a1
-----

-  Refactored to rely on `edbob <http://edbob.org/>`_.  (Most of Rattail's
   "guts" now live there instead.)
