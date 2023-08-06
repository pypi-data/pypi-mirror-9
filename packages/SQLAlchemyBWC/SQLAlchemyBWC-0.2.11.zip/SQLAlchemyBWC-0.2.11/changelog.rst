Change Log
===========

0.2.11 released 2015-03-17
--------------------------

 - fixed bad MANIFEST.in from 0.2.10

0.2.10 released 2015-03-17
--------------------------

 - allow testing-related decorators/helpers to specify db for proper rollbacks
   and dialect message checks

0.2.9 released 2014-08-29
-------------------------

 - add auto-cleanup of beaker sessions for database storage (if applicable).
   settings.beaker.auto_clear_sessions (default True) controls this function
 - handle new format for SQLite null messages
 - restructure setup.py, version, readme, etc.

0.2.8 released 2014-07-08
-------------------------

 - fix problem when metadata "sticking" when using multiple databases
 - SQLAlchemyContainer can now handle None for a URL and won't throw an exception
 - add .lib.sql.SQLLoader() to be a more flexible option than the other functions in that module

0.2.7 released 2013-12-17
-------------------------

 - adjust declarative order_by_helper() to not assume an id column but use primary keys instead

0.2.6 released 2012-10-24
-------------------------

 - added assert_raises_*_exc() decorators for testing
 - update SAValidation dependency to >= 0.2.0

0.2.5 released 2011-12-13
-------------------------

 - fix problem in requirements that would result in conflicting SQLAlchemy
    versions

0.2.4 released 2011-11-09
-------------------------
 - **BC BREAK**: changing LookupMixin.test_create() to .testing_create()
 - convert sql processing to use generators
 - add lib/helpers.py:clear_db_data(), only postgres supported currently

0.2.3 released 2011-07-16
-----------------------------
 - Facilitate use by non-default SA engine.  Enables a project to have two
    DB connections and hence two SA sessions, and still be able to use this lib.

0.2.2 released 2011-05-19
-----------------------------
 - same as 0.2.1 (accidental release bump)

0.2.1 released 2011-05-19
-----------------------------
 - remove explicit SQLAlchemy version since savalidation will install it
