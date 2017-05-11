import time
import random

from ascii_graph import Pyasciigraph
from django_redis import get_redis_connection

from django import http
from django.conf import settings
from django.core.cache import caches


def run(request, cache_name):
    if cache_name == 'random':
        cache_name = random.choice(settings.CACHE_NAMES)

    cache = caches[cache_name]
    t0 = time.time()
    data = cache.get('benchmarking', [])
    t1 = time.time()
    if random.random() < settings.WRITE_CHANCE:
        data.append(t1 - t0)
        print("WRITE", cache_name, len(str(data)))
        cache.set('benchmarking', data, 100)
    if data:
        avg = 1000 * sum(data) / len(data)
    else:
        avg = 'notyet'
    # print(cache_name, '#', len(data), 'avg:', avg, ' size:', len(str(data)))
    return http.HttpResponse('{}\n'.format(avg))


def _stats(r):
    # returns the median, average and standard deviation of a sequence
    tot = sum(r)
    avg = tot/len(r)
    sdsq = sum([(i-avg)**2 for i in r])
    s = list(r)
    s.sort()
    return s[len(s)//2], avg, (sdsq/(len(r)-1 or 1))**.5


def summary(request):

    P = 15

    def fmt_ms(s):
        return ('{:.3f}ms'.format(1000 * s)).rjust(P)

    r = http.HttpResponse()
    r.write(''.ljust(P))
    r.write('TIMES'.rjust(P))
    r.write('AVERAGE'.rjust(P))
    r.write('MEDIAN'.rjust(P))
    r.write('STDDEV'.rjust(P))
    r.write('\n')
    avgs = []
    medians = []
    for CACHE in settings.CACHE_NAMES:
        data = caches[CACHE].get('benchmarking')
        if data is None:
            r.write('Nothing for {}\n'.format(CACHE))
        else:
            median, avg, stddev = _stats(data)
            avgs.append((CACHE, avg * 1000))
            medians.append((CACHE, median * 1000))
            r.write(
                '{}{}{}{}{}\n'
                .format(
                    CACHE.ljust(P),
                    str(len(data)).rjust(P),
                    fmt_ms(avg),
                    fmt_ms(median),
                    fmt_ms(stddev),
                )
            )

    r.write('\n')

    graph = Pyasciigraph(
        float_format='{0:,.3f}'
    )
    for line in graph.graph('Best Averages (shorter better)', avgs):
        print(line, file=r)
    for line in graph.graph('Best Medians (shorter better)', medians):
        print(line, file=r)

    print('\n', file=r)

    sizes = []
    for name in settings.CACHE_NAMES:
        connection = get_redis_connection(name)
        sizes.append((name, connection.strlen(":1:benchmarking")))

    graph = Pyasciigraph(
        human_readable='si',
    )
    for line in graph.graph('Size of Data Saved (shorter better)', sizes):
        print(line, file=r)

    print('\n', file=r)
    return r
