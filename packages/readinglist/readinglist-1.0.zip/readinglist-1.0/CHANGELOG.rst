Changelog
=========

This document describes changes between each past release.


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
