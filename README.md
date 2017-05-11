Fastest Redis
=============

An experiment ground for testing which way to use Redis
as a cache backend is the fastest.


Sample Run
----------

Start the server:

    ./manage.py runserver

First run it a bunch of times:

    wrk -d10s "http://127.0.0.1:8000/random"

Then to see which was the fastest:

    curl http://127.0.0.1:8000/summary

You'll get an output like this:

              TIMES        AVERAGE         MEDIAN         STDDEV
    redis                     1896        0.623ms        0.474ms        0.738ms
    default                   1981        0.087ms        0.074ms        0.105ms
    memcached                 1629        2.328ms        1.915ms        1.877ms

    Best Averages (shorter better)
    ###############################################################################
    ████████████████                                               0.623  redis
    ██                                                             0.087  default
    █████████████████████████████████████████████████████████████  2.328  memcached
