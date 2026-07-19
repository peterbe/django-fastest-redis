from django.apps import AppConfig
from django_redis import get_redis_connection


class BenchmarkingConfig(AppConfig):
    name = "fastestcache"

    def ready(self):
        connection = get_redis_connection("default")
        print("All Redis flushed")
        connection.flushall()
