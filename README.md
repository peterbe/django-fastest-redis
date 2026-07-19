Fastest Redis
=============

Blog post
---------

Please see [Fastest Redis configuration for Django](https://www.peterbe.com/plog/fastest-redis-optimization-for-django).

Introduction
------------

An experiment for testing which way to use Redis
as a cache backend is the fastest.

All these tests are variations of configurations
using [django-redis](https://github.com/jazzband/django-redis).

What it tests
-------------

For 1,000 times, for each cache backend, it measures how long it takes to get
the key back with `data = cache.get("benchmarking", [])`.
Then, that time is converted to a string (e.g. `'0.0028868750669062138'`).

In the end, it takes all those lists and queries Redis how long that cache key
is in using `STRLEN`. For cache backends that uses compression that's the size
of the data in Redis. The smaller that is the more "efficient" the compression
is.

Sample Run
----------

Start the server:

    ./manage.py runserver

First run it a bunch of times:

    oha -n 1000 "http://127.0.0.1:8888/run/random"

Then to see which was the fastest:

    curl http://127.0.0.1:8888/summary

You'll get an output like this:

                            TIMES        AVERAGE   MEDIAN (P50)   MEDIAN (P90)         STDDEV
    default                    198        0.181ms        0.176ms        0.216ms        0.038ms
    zlib                       213        0.190ms        0.182ms        0.237ms        0.039ms
    lzma                       134        0.273ms        0.272ms        0.332ms        0.042ms
    zstd                       202        0.192ms        0.180ms        0.243ms        0.046ms

    Best Means (shorter better)
    ###############################################################################
    █████████████████████████████████████████                        0.181  default
    ███████████████████████████████████████████                      0.190  zlib
    ███████████████████████████████████████████████████████████████  0.273  lzma
    ████████████████████████████████████████████                     0.192  zstd

    Best Medians (shorter better)
    ###############################################################################
    ████████████████████████████████████████                         0.176  default
    ██████████████████████████████████████████                       0.182  zlib
    ███████████████████████████████████████████████████████████████  0.272  lzma
    █████████████████████████████████████████                        0.180  zstd

    Size of Data Saved (shorter better)
    ###############################################################################
    ████████████████████████████████████████████████████████████████  5151  default
    ██████████████████████████                                        2151  zlib
    █████████████████                                                 1420  lzma
    ████████████████████████                                          2010  zstd

    Size of Data without Default (shorter better)
    ###############################################################################
    ███████████████████████████████████████████████████████████████████  2151  zlib
    ████████████████████████████████████████████                         1420  lzma
    ██████████████████████████████████████████████████████████████       2010  zstd

Analysis
--------

`zstd` requires a third-party package called `pyzstd` whereas `zlib` and `lzma`
are built in to Python as standard libraries.

On my macOS, `lzma` is the most space efficient but it takes marginally
longer to retrieve. The benchmark is also run in a GitHub Action workflow.
There, the fastest is `zlib` and most space efficient is `zlib` too.

