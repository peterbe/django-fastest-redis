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


def reset(request):
    for CACHE in settings.CACHE_NAMES:
        caches[CACHE].delete("benchmarking")
    return http.HttpResponse("Done\n")


def run(request, cache_name):
    if cache_name == "random":
        cache_name = random.choice(settings.CACHE_NAMES)

    cache = caches[cache_name]
    t0 = time.perf_counter()
    data = cache.get("benchmarking", [])
    t1 = time.perf_counter()
    if random.random() < settings.WRITE_CHANCE:
        data.append(str(t1 - t0))
        print(str(t1 - t0))
        cache.set("benchmarking", data, 100)
    if data:
        avg = 1000 * statistics.mean([float(x) for x in data])
    else:
        avg = "notyet"
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
            data = [float(x) for x in data]
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
    for line in graph.graph("Best Means (shorter better)", means):
        r.write(line + "\n")

    r.write("\n")

    for line in graph.graph("Best Medians (shorter better)", medians):
        r.write(line + "\n")

    r.write("\n")

    sizes = []
    for name in settings.CACHE_NAMES:
        connection = get_redis_connection(name)
        sizes.append((name, connection.strlen(":1:benchmarking")))

    graph = Pyasciigraph()
    for line in graph.graph("Size of Data Saved (shorter better)", sizes):
        r.write(line + "\n")

    r.write("\n")

    graph = Pyasciigraph()
    except_default = [(name, size) for name, size in sizes if name != "default"]
    for line in graph.graph(
        "Size of Data without Default (shorter better)", except_default
    ):
        r.write(line + "\n")

    r.write("\n")
    return r
