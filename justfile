dev:
    uv run manage.py runserver

shell:
    uv run manage.py shell

format:
    uv run ruff format fastestcache
    uv run ruff check --fix fastestcache
    # correct import sort order
    uv run ruff check --select I --fix

lint: format
    uv run ruff check fastestcache
