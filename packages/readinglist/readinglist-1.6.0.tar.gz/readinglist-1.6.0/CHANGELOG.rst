Changelog
=========

This document describes changes between each past release.

1.6.0 (2015-04-10)
------------------

**Deployment instructions**

Some changes were introduced in database schema. Run schema migration command
before starting the application:

::

    cliquet --ini production.ini migrate

**New features**

- Add more info in heartbeat (fixes #229)
- Clarify conflict docs (#244)
- Clarify data model docs (#247)
- Add PostgreSQL schema migration system (mozilla-services/cliquet#139)

See `every features brought by Cliquet 1.7 <https://github.com/mozilla-services/cliquet/releases/tag/1.7.0>`_

**Bug fixes**

- Fix login prompt when Basic Auth is disabled (#237)
- Fix random IndexError in load tests (#238)
- Fix smoke tests configuration reading
- Fix Heka logging format of objects (#199)
- Fix performance of record insertion using ordered index (mozilla-services/cliquet#138)
- Fix 405 errors not JSON formatted (mozilla-services/cliquet#88)

See `every bug fixes brought by Cliquet 1.7 <https://github.com/mozilla-services/cliquet/releases/tag/1.7.0>`_


1.5.0 (2015-03-30)
------------------

**New features**

- Split schema initialization from application startup, using a command-line
  tool.

::

    cliquet --ini production.ini init


**Bug fixes**

- Fix documentation about WSGI and Sentry
- Fix connection pool no being shared between cache and storage (mozilla-services/cliquet#176)
- Default connection pool size to 10 (instead of 50) (mozilla-services/cliquet#176)
- Warn if PostgreSQL session has not UTC timezone (mozilla-services/cliquet#177)

**Internal changes**

- Deprecated ``cliquet.storage_pool_maxconn`` and ``cliquet.cache_pool_maxconn``
  settings (renamed to ``cliquet.storage_pool_size`` and ``cliquet.cache_pool_size``)


1.4.0 (2015-03-27)
------------------

**New features**

- Smoke test of FxA authentication using Loads (#220)
- Mesure calls on the authentication policy (mozilla-services/cliquet#167)
- Force default pagination to 100 if not set in settings (#214)
- Add documentation about setting up Sentry loggers (#227)

**Breaking changes**

- Prefix statsd metrics with the value of `cliquet.statsd_prefix` or
  `cliquet.project_name` (mozilla-services/cliquet#162)
- `http_scheme` setting has been replaced by `cliquet.http_scheme` and
  `cliquet.http_host` was introduced (mozilla-services/cliquet#151, mozilla-services/cliquet#166)
- URL in the hello view now has version prefix (mozilla-services/cliquet#165)

**Bug fixes**

- Fix changing read position (#213)
- Fix some PostgreSQL connection bottlenecks (mozilla-services/cliquet#170)
- Pull monitoring dependencies during install (#218)

**Internal changes**

- Update of PyFxA to get it working with gevent monkey patching (mozilla-services/cliquet#168)


1.3.0 (2015-03-25)
------------------

**Deployment instructions**

Until the database schema migration system is released (mozilla-services/cliquet#139),
changes on schema have to be applied manually:

::

    ALTER FUNCTION as_epoch(TIMESTAMP) IMMUTABLE;
    CREATE INDEX idx_records_last_modified_epoch ON records(as_epoch(last_modified));
    CREATE INDEX idx_deleted_last_modified_epoch ON deleted(as_epoch(last_modified));

**New features**

- Add setting to enable to asynchronous PostgreSQL using `Psycogreen <https://pypi.python.org/pypi/psycogreen>`_.
  (*default: disabled*). See installation documentation for more details on this.
- Add ability to execute only action in loads tests using the ``LOAD_ACTION``
  environment variable. See contributing documentation for more details (#208).
- Add new load tests with several kinds of batch operations (#204)

**Bug fixes**

- Fix pagination URL in Next-page headers (fixes #210)
- Fix regression on records URL unicity when using ujson (#205)
- Fix hashing of user_id for BasicAuth (mozilla-services/cliquet#128)
- Force PostgreSQl session timezone to UTC (mozilla-services/cliquet#122)
- Make sure the `paginate_by` setting overrides the passed `limit`
  argument (mozilla-services/cliquet#129)
- Fix limit comparison under Python3 (mozilla-services/cliquet#143)
- Do not serialize using JSON if not necessary (mozilla-services/cliquet#131)
- Fix crash of classic logger with unicode (mozilla-services/cliquet#142)
- Fix crash of CloudStorage backend when remote returns 500 (mozilla-services/cliquet#142)
- Fix behaviour of CloudStorage with backslashes in querystring (mozilla-services/cliquet#142)
- Fix python3.4 segmentation fault (mozilla-services/cliquet#142)
- Add missing port in Next-Page header (mozilla-services/cliquet#147)


**Internal changes**

- Use postgres cache in loads tests (#203)
- Use ujson again, it was removed in the 1.3.2 release (#132)
- Add index for as_epoch(last_modified) (#130). Please add the following
  statements to SQL for the migration::
- Prevent fetching to many records for one user collection (#130)
- Use UPSERT for the heartbeat (#141)
- Improve tests of basic auth (#128)


1.2.0 (2015-03-20)
------------------

**New features**

- Add PostgreSQL connection pooling, with new settings
  ``cliquet.storage_pool_maxconn`` and ``cliquet.cache_pool_maxconn``
  (*Default: 50*) (mozilla-services/cliquet#112)
- Add `StatsD <https://github.com/etsy/statsd/>`_ support,
  enabled with ``cliquet.statsd_url = udp://server:port`` (mozilla-services/cliquet#114)
- Add `Sentry <http://sentry.readthedocs.org>`_ support,
  enabled with ``cliquet.sentry_url = http://user:pass@server/1`` (mozilla-services/cliquet#110)

**Bug fixes**

- Fix FxA verification cache not being used (mozilla-services/cliquet#103)
- Fix heartbeat database check (mozilla-services/cliquet#109)
- Fix PATCH endpoint crash if request has no body (mozilla-services/cliquet#115)

**Internal changes**

- Switch to `ujson <https://pypi.python.org/pypi/ujson>`_ for JSON
  de/serialization optimizations (mozilla-services/cliquet#108)
- Use async connections for psycopg (#201)
- Imrpove the documentation layout (#200)


1.1.0 (2015-03-18)
------------------

**Breaking changes**

* `cliquet.storage.postgresql` now uses UUID as record primary key (mozilla-services/cliquet#70)
* Settings ``cliquet.session_backend`` and ``cliquet.session_url`` were
  renamed ``cliquet.cache_backend`` and ``cliquet.cache_url`` respectively.
* FxA user ids are not hashed anymore (mozilla-services/cliquet#82)
* Setting ``cliquet.retry_after`` was renamed ``cliquet.retry_after_seconds``
* OAuth2 redirect url now requires to be listed in
  ``fxa-oauth.webapp.authorized_domains`` (e.g. ``*.mozilla.com``)
* Batch are now limited to 25 requests by default (mozilla-services/cliquet#90)
* OAuth relier has been disabled by default (#193)

**New features**

* Every setting can be specified via an environment variable
  (e.g. ``cliquet.storage_url`` with ``CLIQUET_STORAGE_URL``)
* Logging now relies on `structlog <http://structlog.org>`_ (mozilla-services/cliquet#78)
* Logging output can be configured to stream JSON (mozilla-services/cliquet#78)
* New cache backend for PostgreSQL (mozilla-services/cliquet#44)
* Documentation was improved on various aspects (mozilla-services/cliquet#64, mozilla-services/cliquet#86)
* Handle every backend errors and return 503 errors (mozilla-services/cliquet#21)
* State verification for OAuth2 dance now expires after 1 hour (mozilla-services/cliquet#83)
* Add the preview field for an article (#156)
* Setup the readinglist OAuth scope (#16)
* Add a uwsgi file (#180)

**Bug fixes**

* FxA OAuth views errors are now JSON formatted (mozilla-services/cliquet#67)
* Prevent error when pagination token has bad format (mozilla-services/cliquet#72)
* List of CORS exposed headers were fixed in POST on collection (mozilla-services/cliquet#54)
* Fix environment variables not overriding configuration (mozilla-services/cliquet#100)
* Got rid of custom *CAST* in PostgreSQL storage backend to prevent installation
  errors without superuser (ref #174, mozilla-services/cliquet#99)


1.0 (2015-03-03)
----------------

**Breaking changes**

- Most configuration entries were renamed, see `config/readinglist.ini`
  example to port your configuration
- Status field was removed, archived and deleted fields were added
  (requires a database flush.)
- Remove Python 2.6 support

**New features**

- Add the /fxa-oauth/params endpoint
- Add the DELETE /articles endpoint
  (Needs cliquet.delete_collection_enabled configuration)
- Add the Response-Behavior header on PATCH /articles
- Add HTTP requests / responses examples in the documentation
- Use Postgresql as the default database backend

**Internal changes**

- Main code base was split into a separate project
  `Cliquet <https://github.com/mozilla-services/cliquet>`_
- Perform continuated pagination in loadtests
- Use PostgreSQL for loadtests


0.2.2 (2015-02-13)
------------------

**Bug fixes**

- Fix CORS preflight request permissions (PR #119)


0.2.1 (2015-02-11)
------------------

**Breaking changes**

- Internal user ids for FxA are now prefixed, all existing records
  will be lost (refs #109)

**Bug fixes**

- Fix CORS headers on validation error responses (ref #104)
- Fix handling of defaults in batch requests (ref #111, #112)


0.2 (2015-02-09)
----------------

**Breaking changes**

- PUT endpoint was disabled (ref #42)
- ``_id`` field was renamed to ``id`` (ref PR #91)
- FxA now requires a redirection URL (ref PR #69)

**New features**

- URLs uniques by user (ref #20)
- Handle conflicts responses (ref #45)
- Conditional changes for some articles attributes (ref #6)
- Batching support (ref #2)
- Pagination support (ref #25)
- Online documentation available at http://readinglist.readthedocs.org (ref PR #73)
- Basic Auth nows support any user/password combination (ref PR #78)

**Bug fixes**

- ``marked_read_by`` was ignored on PATCH (ref PR #72)
- Timestamp was not incremented on DELETE (ref PR #95)
- Fix number of bugs regarding support of CORS in error views (ref PR #105)
- Previous Basic Auth could impersonate FxA user (ref PR #78)


0.1 (2015-01-30)
----------------

- Allow Cors (#67)
- Log incomming request to the console (#65)
- Add timestamp for 304 and 412 response (#40)
- Add time vector to GET /articles and GET /articles/<id> (#4)
- Preconditions Headers for Update and Creation (#60)
- Provide number of items in headers of GET /articles (#39)
- Check for filter values (#58)
- Handle article title length (#37)
- Support min, max and no keywords filters (#43)
- Prevent to modify read-only fields (#26)
- Filtering and sort querystring (#44)
- Redis storage (#50)
- Handle errors (#24 - #49)
- Add loadtests (#47)
- Handle API version in URL (#33)
