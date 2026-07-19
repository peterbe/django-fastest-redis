install:
    uv sync

dev:
    uv run manage.py runserver 8888

start:
    uv run gunicorn wsgi -w 4 -b 0.0.0.0:8888 --access-logfile=-

shell:
    uv run manage.py shell

format:
    uv run ruff format fastestcache
    uv run ruff check --fix fastestcache
    # correct import sort order
    uv run ruff check --select I --fix

lint: format
    uv run ruff check fastestcache
