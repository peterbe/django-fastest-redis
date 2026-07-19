import random
import statistics
import time

from ascii_graph import Pyasciigraph
from django import http
from django.conf import settings
from django.core.cache import caches
from django_redis import get_redis_connection


def index(request):
    r = http.HttpResponse(content_type="text/plain")
    r.write("Available caches:\n")
    for CACHE in settings.CACHE_NAMES:
        r.write("  {}\n".format(CACHE))
    r.write("\n")
    r.write("To run a benchmark, go to /run/<cache_name> or /run/random\n")
    return r


def run(request, cache_name):
    if cache_name == "random":
        cache_name = random.choice(settings.CACHE_NAMES)

    cache = caches[cache_name]
    t0 = time.time()
    data = cache.get("benchmarking", [])
    t1 = time.time()
    if random.random() < settings.WRITE_CHANCE:
        data.append(t1 - t0)
        cache.set("benchmarking", data, 100)
    if data:
        avg = 1000 * sum(data) / len(data)
    else:
        avg = "notyet"
    # print(cache_name, '#', len(data), 'avg:', avg, ' size:', len(str(data)))
    return http.HttpResponse("{}\n".format(avg))


def summary(request):

    P = 15

    def fmt_ms(s):
        return ("{:.3f}ms".format(1000 * s)).rjust(P)

    r = http.HttpResponse(content_type="text/plain")
    r.write("".ljust(P))
    r.write("TIMES".rjust(P))
    r.write("AVERAGE".rjust(P))
    r.write("MEDIAN (P50)".rjust(P))
    r.write("MEDIAN (P90)".rjust(P))
    r.write("STDDEV".rjust(P))
    r.write("\n")
    means = []
    medians = []
    MINIMUM = 10
    for CACHE in settings.CACHE_NAMES:
        data = caches[CACHE].get("benchmarking")
        if not data:
            r.write("Nothing for {}\n".format(CACHE))
        elif len(data) < MINIMUM:
            r.write("Not enough data for {}\n".format(CACHE))
        else:
            # Always chop off the first 10 measurements because it's usually
            # way higher than all the others. That way we're only comparing
            # configurations once they're all warmed up
            data = data[MINIMUM:]
            median = statistics.median(data)
            mean = statistics.mean(data)
            stddev = statistics.stdev(data)
            percentiles = statistics.quantiles(data, n=100)
            p90 = percentiles[89]

            means.append((CACHE, mean * 1000))
            medians.append((CACHE, median * 1000))
            r.write(
                "{}{}{}{}{}{}\n".format(
                    CACHE.ljust(P),
                    str(len(data)).rjust(P),
                    fmt_ms(mean),
                    fmt_ms(median),
                    fmt_ms(p90),
                    fmt_ms(stddev),
                )
            )

    r.write("\n")

    graph = Pyasciigraph(float_format="{0:,.3f}")
    for line in graph.graph("Best Averages (shorter better)", means):
        print(line, file=r)
    for line in graph.graph("Best Medians (shorter better)", medians):
        print(line, file=r)

    print("\n", file=r)

    sizes = []
    for name in settings.CACHE_NAMES:
        connection = get_redis_connection(name)
        sizes.append((name, connection.strlen(":1:benchmarking")))

    graph = Pyasciigraph(
        human_readable="si",
    )
    for line in graph.graph("Size of Data Saved (shorter better)", sizes):
        print(line, file=r)

    print("\n", file=r)
    return r
