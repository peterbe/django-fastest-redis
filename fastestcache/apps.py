from django_redis import get_redis_connection

from django.apps import AppConfig


class BenchmarkingConfig(AppConfig):
    name = 'fastestcache'

    def ready(self):
        connection = get_redis_connection('default')
        print("All Redis flushed")
        connection.flushall()
