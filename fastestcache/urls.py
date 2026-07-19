from django.urls import include, path

urlpatterns = [
    path("", include("fastestcache.benchmarking.urls")),
]
