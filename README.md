Fastest Redis
=============

Blog post
---------

Please see [Fastest Redis configuration for Django](https://www.peterbe.com/plog/fastest-redis-optimization-for-django).

Introduction
------------

An experiment ground for testing which way to use Redis
as a cache backend is the fastest.

All these tests are variations of configurations
using [django-redis](https://niwinz.github.io/django-redis/latest/).


Sample Run
----------

Start the server:

    ./manage.py runserver

First run it a bunch of times:

    wrk -d20s "http://127.0.0.1:8000/random"

Then to see which was the fastest:

    curl http://127.0.0.1:8000/summary

You'll get an output like this:

                             TIMES        AVERAGE        MEDIAN         STDDEV
    json                      1508        2.178ms        1.551ms        1.866ms
    lzma                      1110        2.016ms        1.075ms        2.102ms
    ujson                     1835        1.634ms        0.829ms        1.862ms
    zlib                      1656        1.618ms        0.781ms        1.882ms
    hires                     1791        1.513ms        0.743ms        1.701ms
    default                   1763        1.508ms        0.745ms        1.773ms
    msgpack                   1784        1.543ms        0.735ms        1.768ms

    Best Averages (shorter better)
    ###############################################################################
    ███████████████████████████████████████████████████████████████  2.178  json
    ██████████████████████████████████████████████████████████       2.016  lzma
    ███████████████████████████████████████████████                  1.634  ujson
    ██████████████████████████████████████████████                   1.618  zlib
    ███████████████████████████████████████████                      1.513  hires
    ███████████████████████████████████████████                      1.508  default
    ████████████████████████████████████████████                     1.543  msgpack
    Best Medians (shorter better)
    ###############################################################################
    ███████████████████████████████████████████████████████████████  1.551  json
    ███████████████████████████████████████████                      1.075  lzma
    █████████████████████████████████                                0.829  ujson
    ███████████████████████████████                                  0.781  zlib
    ██████████████████████████████                                   0.743  hires
    ██████████████████████████████                                   0.745  default
    █████████████████████████████                                    0.735  msgpack


    Size of Data Saved (shorter better)
    ###############################################################################
    █████████████████████████████████████████████████████████████████  34K  json
    █████                                                               3K  lzma
    █████████████████████████████████████████████                      24K  ujson
    █████████                                                           5K  zlib
    ██████████████████████████████                                     16K  hires
    ██████████████████████████████                                     16K  default
    ██████████████████████████████                                     16K  msgpack
