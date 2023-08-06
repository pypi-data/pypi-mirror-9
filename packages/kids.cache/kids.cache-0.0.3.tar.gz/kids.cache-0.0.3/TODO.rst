

- speak of lazy evaluation and singleton pattern
   - could offer some aliases @singleton or @lazy, with predefined adapted cache stores
     - no need for stats, nor even a real CacheStore, it could be a dummy one cell cache.
   - singleton should have a key=constant.
   - singleton should support decorating classes
- say where is stored the cache, allow a 'expose_attr' of the cache function to allow access to the cache
- remove stats from cachedfunc, these should be in the Cache object.
   - the cache object should be the only attribute accessible if 'expose_attr' is set.
   - The stats are in the cache object.
   - we can do generic stat objects to adapt normal cache object and give them stat info as:
     hit, misses, memory footprint, time spent in function, time spent in cache mecanism
   - other adaptors could be dynamic Loggers
- other adaptors could be dynamic tailoring or warnings about size of some cache.

  - a good way would be to allow some loggers to print warning when
    size, or number of miss, or if ratio of hit/miss is not good
    - only on DEBUG and for all the cache. This permits a quick audit.

- offer a "middlewares" arg to specify "adaptors" to cache store. 
  - a default generic middlewares could be used by default, and more
    precise ones for @lazy and @singleton

- add a section implementation detail to README
  - state where is stored the cache.
