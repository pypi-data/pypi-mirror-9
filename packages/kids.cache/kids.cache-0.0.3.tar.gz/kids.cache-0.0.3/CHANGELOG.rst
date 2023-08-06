Changelog
=========

0.0.3 (2015-02-24)
------------------

Fix
~~~

- Nasty cache collision if two custom objects shared the same hash and
  type but where not ``equal``. [Valentin Lab]

  And as a matter of fact, this happens. For instance, all instance of
  ``object`` or any subclass will inherit a special ``hash`` method that
  uses ``id``, but in some version of python (the recent ones), the ``id``
  value is divided by ``16``. And hash collisions are to be expected
  anyway, and of course should not cause cache collisions.


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


