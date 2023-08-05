Changelog
=========

0.0.2 (2015-02-02)
------------------

New
~~~

- Added type to cache stats, removed dependency to ``cachetools``.
  [Valentin Lab]

Changes
~~~~~~~

- Default cache store's ``currsize`` use the ``len()`` instead of None.
  [Valentin Lab]

  And this makes sense for the default dict implementation.


Fix
~~~

- Wrong attribution for ``cache_clear`` and ``cache_info`` functions.
  [Valentin Lab]

- Similar ``set`` could get different hash. [Valentin Lab]

  ``set`` weren't sorted prior to introspection for hashing.


0.0.1 (2014-05-23)
------------------

- First import. [Valentin Lab]


