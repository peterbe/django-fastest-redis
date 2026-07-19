# Copilot Instructions

## Project Overview

This is a benchmarking experiment that measures the performance of different Redis cache configurations in Django using [django-redis](https://niwinz.github.io/django-redis/latest/). It is not a production app — it is a load-testing harness.

## Running the Project

```bash
# Install dependencies
uv sync

# Start the Django dev server (requires a running Redis at 127.0.0.1:6379)
uv run manage.py runserver

# Hammer the /random endpoint to populate benchmark data
wrk -d20s "http://127.0.0.1:8000/random"

# View benchmark results
curl http://127.0.0.1:8000/summary
```

Configuration via environment variables (uses `python-decouple`):
- `REDIS_LOCATION` — Redis URL, default `redis://127.0.0.1:6379`
- `CACHE_NAMES` — comma-separated list of cache configs to benchmark (default: all)
- `WRITE_CHANCE` — float 0.0–1.0 controlling how often a write happens (default `1.0`)
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`

## Architecture

The app has a single Django app (`fastestcache/benchmarking`) with two views:

- **`/random`** (or `/<cache_name>`) — picks a cache backend, performs a `get`, optionally a `set`, and records the elapsed time in the cached list itself. Each cache backend stores its own timing list under the key `benchmarking`.
- **`/summary`** — reads all timing lists, computes median/average/stddev per backend, and renders ASCII bar charts using `ascii_graph`. Also uses `get_redis_connection` to report raw byte sizes stored in Redis.

Each cache backend in `settings.py` maps to a separate Redis database (db 0–7) to avoid key collisions.

## Cache Backends Defined

| Name         | DB  | Variation                             |
|--------------|-----|---------------------------------------|
| `default`    | 0   | Default pickle serializer             |
| `json`       | 1   | JSON serializer                       |
| `ujson`      | 2   | Custom `UJSONSerializer` (see below)  |
| `msgpack`    | 3   | MSGPack serializer                    |
| `hires`      | 4   | Default + HiredisParser               |
| `zlib`       | 5   | Default + zlib compressor             |
| `lzma`       | 6   | Default + lzma compressor             |
| `msgpack_zlib` | 7 | MSGPack + zlib compressor             |

## Key Conventions

- **Custom serializer pattern**: `fastestcache/ujson_serializer.py` shows the pattern for adding a new serializer — subclass `django_redis.serializers.base.BaseSerializer` and implement `dumps`/`loads`.
- **`CACHE_NAMES` drives everything**: URL patterns in `benchmarking/urls.py` are built dynamically from `settings.CACHE_NAMES` at startup. Adding a new cache backend requires adding it to `CACHES` in `settings.py`; it will automatically be registered in URLs and included in the summary.
- **First 10 measurements are discarded**: `summary` view strips `data[:10]` from each backend's list to avoid cold-start skew.
- **No database migrations needed**: The app uses SQLite for Django internals but no models with data — all benchmark state lives in Redis.
- **No test suite**: `fastestcache/benchmarking/tests.py` exists but is empty.
