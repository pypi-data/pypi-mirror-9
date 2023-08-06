Changelog
=========

This document describes changes between each past release.


1.3.0 (2015-03-20)
------------------

**New features**

- Add PostgreSQL connection pooling, with new settings
  ``cliquet.storage_pool_maxconn`` and ``cliquet.cache_pool_maxconn``
  (*Default: 50*) (#112)
- Add `StatsD <https://github.com/etsy/statsd/>`_ support,
  enabled with ``cliquet.statsd_url = udp://server:port`` (#114)
- Add `Sentry <http://sentry.readthedocs.org>`_ support,
  enabled with ``cliquet.sentry_url = http://user:pass@server/1`` (#110)

**Bug fixes**

- Fix FxA verification cache not being used (#103)
- Fix heartbeat database check (#109)
- Fix PATCH endpoint crash if request has no body (#115)

**Internal changes**

- Switch to `ujson <https://pypi.python.org/pypi/ujson>`_ for JSON
  de/serialization optimizations (#108)


1.2.1 (2015-03-18)
------------------

- Fix tests about unicode characters in BATCH querystring patch
- Remove CREATE CAST for the postgresql backend
- Fix environment variable override


1.2 (2015-03-18)
----------------

**Breaking changes**

- `cliquet.storage.postgresql` now uses UUID as record primary key (#70)
- Settings ``cliquet.session_backend`` and ``cliquet.session_url`` were
  renamed ``cliquet.cache_backend`` and ``cliquet.cache_url`` respectively.
- FxA user ids are not hashed anymore (#82)
- Setting ``cliquet.retry_after`` was renamed ``cliquet.retry_after_seconds``
- OAuth2 redirect url now requires to be listed in
  ``fxa-oauth.webapp.authorized_domains`` (e.g. ``*.mozilla.com``)
- Batch are now limited to 25 requests by default (#90)

**New features**

- Every setting can be specified via an environment variable
  (e.g. ``cliquet.storage_url`` with ``CLIQUET_STORAGE_URL``)
- Logging now relies on `structlog <http://structlog.org>`_ (#78)
- Logging output can be configured to stream JSON (#78)
- New cache backend for PostgreSQL (#44)
- Documentation was improved on various aspects (#64, #86)
- Handle every backend errors and return 503 errors (#21)
- State verification for OAuth2 dance now expires after 1 hour (#83)

**Bug fixes**

- FxA OAuth views errors are now JSON formatted (#67)
- Prevent error when pagination token has bad format (#72)
- List of CORS exposed headers were fixed in POST on collection (#54)

**Internal changes**

- Added a method in `cliquet.resource.Resource` to override known fields
  (*required by Kinto*)
- Every setting has a default value
- Every end-point requires authentication by default
- Session backend was renamed to cache (#96)


1.1.4 (2015-03-03)
------------------

- Update deleted_field support for postgres (#62)


1.1.3 (2015-03-03)
------------------

- Fix include_deleted code for the redis backend (#60)
- Improve the update_record API (#61)


1.1.2 (2015-03-03)
------------------

- Fix packaging to include .sql files.


1.1.1 (2015-03-03)
------------------

- Fix packaging to include .sql files.


1.1 (2015-03-03)
----------------

**New features**

- Support filter on deleted using since (#51)

**Internal changes**

- Remove python 2.6 support (#50)
- Renamed Resource.deleted_mark to Resource.deleted_field (#51)
- Improve native_value (#56)
- Fixed Schema options inheritance (#55)
- Re-build the virtualenv when setup.py changes
- Renamed storage.url to cliquet.storage_url (#49)
- Refactored the tests/support.py file (#38)


1.0 (2015-03-02)
----------------

- Initial version, extracted from Mozilla Services Reading List project (#1)

**New features**

- Expose CORS headers so that client behind CORS policy can access them (#5)
- Postgresql Backend (#8)
- Use RedisSession as a cache backend for PyFxA (#10)
- Delete multiple records via DELETE on the collection_path (#13)
- Batch default prefix for endpoints (#14 / #16)
- Use the app version in the / endpoint (#22)
- Promote Basic Auth as a proper authentication backend (#37)

**Internal changes**

- Backends documentation (#15)
- Namedtuple for filters and sort (#17)
- Multiple DELETE in Postgresql (#18)
- Improve Resource API (#29)
- Refactoring of error management (#41)
- Default Options for Schema (#47)
